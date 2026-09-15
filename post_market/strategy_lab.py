"""Deterministic, NIFTY-only post-market strategy replay.

Input schema (CSV or DataFrame):
  timestamp, spot, option_type, strike, expiry, option_ltp
Optional: volume, oi, bid, ask.

The engine evaluates strategies on spot bars and buys the corresponding ATM
CE/PE contract from the same timestamp. It enforces the research guardrails:
09:30 entry start, max 3 entries/day, no overlap, NIFTY only, and 15:00 exit.
Risk parameters are explicit and are not connected to live execution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd

LOT_SIZE = 65
ENTRY_START = "09:30"
EXIT_TIME = "15:00"
STRIKE_STEP = 50
MAX_TRADES_PER_DAY = 3
STOP_PCT = 0.25
TARGET_MULTIPLIER = 1.55


@dataclass(frozen=True)
class Trade:
    strategy: str
    side: str
    timestamp: str
    exit_timestamp: str
    strike: float
    entry: float
    exit: float
    quantity: int
    pnl: float
    pnl_pct: float
    exit_reason: str


@dataclass(frozen=True)
class StrategySummary:
    strategy: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    net_pnl: float
    profit_factor: float
    avg_trade: float
    max_drawdown: float


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def _atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    prev = frame["spot"].shift(1)
    tr = pd.concat(
        [
            frame["spot"].sub(prev).abs(),
            frame["spot"].sub(prev).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["ema20"] = out["spot"].ewm(span=20, adjust=False).mean()
    out["ema50"] = out["spot"].ewm(span=50, adjust=False).mean()
    out["ema200"] = out["spot"].ewm(span=200, adjust=False).mean()
    out["rsi"] = _rsi(out["spot"])
    out["atr"] = _atr(out)
    out["vwap"] = (out["spot"] * out["volume"]).cumsum() / out["volume"].replace(0, np.nan).cumsum()
    out["ma20"] = out["spot"].rolling(20, min_periods=20).mean()
    out["ma30"] = out["spot"].rolling(30, min_periods=30).mean()
    out["ret5"] = out["spot"].pct_change(5)
    out["rolling_high20"] = out["spot"].rolling(20, min_periods=20).max().shift(1)
    out["rolling_low20"] = out["spot"].rolling(20, min_periods=20).min().shift(1)
    # A compact Stoch-RSI proxy used only for replay signal generation.
    rsi_low = out["rsi"].rolling(14, min_periods=14).min()
    rsi_high = out["rsi"].rolling(14, min_periods=14).max()
    out["stoch_rsi"] = ((out["rsi"] - rsi_low) / (rsi_high - rsi_low).replace(0, np.nan)).fillna(0.5)
    return out


def _signal(strategy: str, row: pd.Series, prev: pd.Series | None) -> str | None:
    if strategy == "mean_reversion":
        if row.spot > row.ma30 * 1.005:
            return "PE"
        if row.spot < row.ma30 * 0.995:
            return "CE"
    elif strategy == "directional":
        if row.spot > row.ma20 * 1.005 and row.spot > row.ema50:
            return "CE"
        if row.spot < row.ma20 * 0.995 and row.spot < row.ema50:
            return "PE"
    elif strategy == "semi_directional":
        if row.spot > row.ma30 * 1.003 and row.ret5 > 0:
            return "PE"
        if row.spot < row.ma30 * 0.997 and row.ret5 < 0:
            return "CE"
    elif strategy == "ema_vwap_breakout":
        if row.spot > row.vwap and row.ema20 > row.ema50 and row.rsi >= 55:
            return "CE"
        if row.spot < row.vwap and row.ema20 < row.ema50 and row.rsi <= 45:
            return "PE"
    elif strategy == "orb":
        if row.or_high is not None and row.spot > row.or_high:
            return "CE"
        if row.or_low is not None and row.spot < row.or_low:
            return "PE"
    elif strategy == "vwap_momentum":
        if row.spot > row.vwap and row.ret5 > 0 and row.rsi > 55:
            return "CE"
        if row.spot < row.vwap and row.ret5 < 0 and row.rsi < 45:
            return "PE"
    elif strategy == "stoch_rsi_supertrend":
        # Supertrend direction proxy: EMA20 vs EMA50 with ATR buffer.
        if row.ema20 > row.ema50 + 0.10 * row.atr and row.stoch_rsi > 0.80:
            return "CE"
        if row.ema20 < row.ema50 - 0.10 * row.atr and row.stoch_rsi < 0.20:
            return "PE"
    return None


def _prepare_spot(data: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "spot", "option_type", "strike", "expiry", "option_ltp"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    out = data.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out["spot"] = pd.to_numeric(out["spot"], errors="coerce")
    out["strike"] = pd.to_numeric(out["strike"], errors="coerce")
    out["option_ltp"] = pd.to_numeric(out["option_ltp"], errors="coerce")
    if "volume" not in out.columns:
        out["volume"] = 1.0
    out["volume"] = pd.to_numeric(out["volume"], errors="coerce").fillna(0)
    out = out.dropna(subset=["timestamp", "spot", "strike", "option_ltp"])
    out["option_type"] = out["option_type"].astype(str).str.upper()
    out = out[out["option_type"].isin(["CE", "PE"])]
    if out.empty:
        raise ValueError("no CE/PE NIFTY option rows available")
    spot = (
        out.groupby("timestamp", as_index=False)
        .agg(spot=("spot", "first"), volume=("volume", "max"))
        .sort_values("timestamp")
    )
    spot["day"] = spot["timestamp"].dt.date
    # ORB is the first 15 minutes from 09:15; values are fixed for the session.
    local = spot["timestamp"].dt.tz_convert("Asia/Kolkata")
    spot["local_time"] = local.dt.strftime("%H:%M")
    spot["or_high"] = np.nan
    spot["or_low"] = np.nan
    for day, idx in spot.groupby("day").groups.items():
        session = spot.loc[idx]
        opening = session[session["local_time"] < "09:30"]
        if not opening.empty:
            spot.loc[idx, "or_high"] = opening["spot"].max()
            spot.loc[idx, "or_low"] = opening["spot"].min()
    return _features(spot)


def _option_lookup(options: pd.DataFrame, ts: pd.Timestamp, side: str, spot: float) -> tuple[float, float] | None:
    rows = options[(options["timestamp"] == ts) & (options["option_type"] == side)]
    if rows.empty:
        # Permit exact timestamp only. No forward fill: that would introduce look-ahead/stale pricing.
        return None
    rows = rows.copy()
    rows["distance"] = (rows["strike"] - spot).abs()
    rows = rows.sort_values(["distance", "strike"])
    row = rows.iloc[0]
    return float(row["strike"]), float(row["option_ltp"])


def _summary(strategy: str, trades: list[Trade]) -> StrategySummary:
    pnls = np.array([t.pnl for t in trades], dtype=float)
    wins = int((pnls > 0).sum())
    losses = int((pnls <= 0).sum())
    gross_profit = float(pnls[pnls > 0].sum()) if wins else 0.0
    gross_loss = float(-pnls[pnls < 0].sum()) if (pnls < 0).any() else 0.0
    equity = np.cumsum(pnls) if len(pnls) else np.array([0.0])
    peak = np.maximum.accumulate(equity)
    drawdown = equity - peak
    return StrategySummary(
        strategy=strategy,
        trades=len(trades),
        wins=wins,
        losses=losses,
        win_rate=round(100 * wins / len(trades), 2) if trades else 0.0,
        gross_profit=round(gross_profit, 2),
        gross_loss=round(gross_loss, 2),
        net_pnl=round(float(pnls.sum()), 2) if len(pnls) else 0.0,
        profit_factor=round(gross_profit / gross_loss, 3) if gross_loss else (float("inf") if gross_profit else 0.0),
        avg_trade=round(float(pnls.mean()), 2) if len(pnls) else 0.0,
        max_drawdown=round(float(drawdown.min()), 2),
    )


def replay_strategy(data: pd.DataFrame, strategy: str) -> tuple[list[Trade], StrategySummary]:
    spot = _prepare_spot(data)
    options = data.copy()
    options["timestamp"] = pd.to_datetime(options["timestamp"], utc=True)
    options["option_type"] = options["option_type"].astype(str).str.upper()
    options = options[options["option_type"].isin(["CE", "PE"])].copy()
    options["strike"] = pd.to_numeric(options["strike"], errors="coerce")
    options["option_ltp"] = pd.to_numeric(options["option_ltp"], errors="coerce")
    options = options.dropna(subset=["strike", "option_ltp"])

    trades: list[Trade] = []
    for day, day_spot in spot.groupby("day", sort=True):
        entries = 0
        open_trade = None
        rows = day_spot.sort_values("timestamp")
        for i, (_, row) in enumerate(rows.iterrows()):
            local_time = row.timestamp.tz_convert("Asia/Kolkata").strftime("%H:%M")
            if open_trade is not None:
                current = _option_lookup(options, row.timestamp, open_trade["side"], row.spot)
                if current is not None:
                    _, px = current
                    stop = open_trade["entry"] * (1 - STOP_PCT)
                    target = open_trade["entry"] * TARGET_MULTIPLIER
                    reason = None
                    if px <= stop:
                        reason = "STOP_LOSS"
                    elif px >= target:
                        reason = "TARGET"
                    elif local_time >= EXIT_TIME:
                        reason = "TIME_EXIT"
                    if reason:
                        pnl = (px - open_trade["entry"]) * LOT_SIZE
                        trades.append(Trade(strategy, open_trade["side"], open_trade["timestamp"], str(row.timestamp), open_trade["strike"], open_trade["entry"], px, LOT_SIZE, pnl, px / open_trade["entry"] - 1, reason))
                        open_trade = None
            if open_trade is None and entries < MAX_TRADES_PER_DAY and local_time >= ENTRY_START and local_time < EXIT_TIME:
                signal = _signal(strategy, row, rows.iloc[i - 1] if i else None)
                if signal:
                    picked = _option_lookup(options, row.timestamp, signal, row.spot)
                    if picked is not None and picked[1] > 0:
                        strike, px = picked
                        open_trade = {"side": signal, "strike": strike, "entry": px, "timestamp": str(row.timestamp)}
                        entries += 1
        if open_trade is not None:
            final = rows.iloc[-1]
            picked = _option_lookup(options, final.timestamp, open_trade["side"], final.spot)
            if picked is not None:
                px = picked[1]
                pnl = (px - open_trade["entry"]) * LOT_SIZE
                trades.append(Trade(strategy, open_trade["side"], open_trade["timestamp"], str(final.timestamp), open_trade["strike"], open_trade["entry"], px, LOT_SIZE, pnl, px / open_trade["entry"] - 1, "TIME_EXIT"))
    return trades, _summary(strategy, trades)


STRATEGIES = (
    "mean_reversion",
    "directional",
    "semi_directional",
    "ema_vwap_breakout",
    "orb",
    "vwap_momentum",
    "stoch_rsi_supertrend",
)


def run_post_market_replay(data: pd.DataFrame | str | Path, strategies: Iterable[str] = STRATEGIES) -> dict:
    """Run all requested strategies and return JSON-serializable results."""
    frame = pd.read_csv(data) if isinstance(data, (str, Path)) else data.copy()
    # Fail closed: this lab is NIFTY-only and never guesses the underlying.
    if "underlying" in frame.columns:
        values = {str(v).upper() for v in frame["underlying"].dropna().unique()}
        if values and values != {"NIFTY"}:
            raise ValueError(f"post-market lab is NIFTY-only; received {sorted(values)}")
    selected = list(strategies)
    unknown = [s for s in selected if s not in STRATEGIES]
    if unknown:
        raise ValueError(f"unknown strategies: {unknown}")
    all_trades: list[Trade] = []
    summaries: list[StrategySummary] = []
    for strategy in selected:
        trades, summary = replay_strategy(frame, strategy)
        all_trades.extend(trades)
        summaries.append(summary)
    return {
        "contract": {
            "underlying": "NIFTY",
            "lot_size": LOT_SIZE,
            "entry_start": ENTRY_START,
            "exit_time": EXIT_TIME,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "stop_pct": STOP_PCT,
            "target_multiplier": TARGET_MULTIPLIER,
            "no_lookahead": True,
        },
        "strategies": [asdict(s) for s in summaries],
        "trades": [asdict(t) for t in all_trades],
    }
