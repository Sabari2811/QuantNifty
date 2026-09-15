# QuantNifty Post-Market Strategy Lab

This is a research-only section. It is intentionally isolated from the live decision and execution path.

## Strategies included

- Mean reversion
- Directional momentum
- Semi-directional volatility/reversal
- EMA + VWAP breakout
- Opening-range breakout (ORB)
- VWAP momentum
- Stoch RSI + Supertrend-style trend confirmation

These strategy families were selected from the external NIFTY-options research reviewed for QuantNifty. Public repositories show similar NIFTY option implementations using mean reversion/directional/semi-directional logic and EMA/VWAP/Stoch-RSI/Supertrend/ORB families. They are research references, not proof of profitability. 

## Required raw-data schema

`timestamp,spot,option_type,strike,expiry,option_ltp`

Optional: `underlying,volume,oi,bid,ask`.

The runner is fail-closed for non-NIFTY data, uses exact timestamps for option fills (no forward-fill), selects the nearest 50-point ATM strike, allows at most three entries per day, starts entries at 09:30 IST, and forces the research position out at 15:00 IST.

## Running

```python
from post_market.strategy_lab import run_post_market_replay

result = run_post_market_replay("runtime_data/post_market/2026-09-15.csv")
```

The result contains the immutable research contract, strategy summaries, and trade-by-trade records.

## Important validation rule

Do not publish a P&L result when the raw intraday option dataset is missing, partial, stale, or unauthenticated. EOD bhavcopy/closing prices are not a substitute for the intraday option path required to test SL/target execution.
