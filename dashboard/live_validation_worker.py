import os
import threading
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

from core.logger import logger
from engine.live_engine import LiveEngine
from providers.indmoney_provider import INDMoneyProvider


IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 40)

_worker_lock = threading.Lock()
_worker_started = False


def is_nse_derivatives_session_open(now=None):
    """Return True only during normal NSE equity-derivatives hours on weekdays."""
    current = now.astimezone(IST) if now is not None else datetime.now(IST)
    return current.weekday() < 5 and MARKET_OPEN <= current.time() <= MARKET_CLOSE


def _poll_loop(interval_seconds=60):
    try:
        engine = LiveEngine(provider=INDMoneyProvider())
        logger.info("LIVE VALIDATION WORKER READY | interval=%ss", interval_seconds)
    except Exception:
        logger.exception("LIVE VALIDATION WORKER INIT FAILED")
        return

    while True:
        try:
            now = datetime.now(IST)
            if not is_nse_derivatives_session_open(now):
                time.sleep(interval_seconds)
                continue

            ctx = engine.run_cycle()
            provenance = getattr(ctx, "data_provenance", None)
            option_provenance = getattr(provenance, "option_chain", None) if provenance else None
            logger.info(
                "LIVE VALIDATION CYCLE | timestamp=%s | cycle=%s | spot=%s | runtime=%s | "
                "trade_status=%s | block_reason=%s | option_chain_coverage=%s | option_chain_integrity=%s",
                now.isoformat(),
                getattr(ctx, "cycle_no", None),
                getattr(ctx, "spot", None),
                getattr(ctx, "runtime_status", None),
                getattr(ctx, "trade_status", None),
                getattr(ctx, "trade_block_reason", None),
                getattr(option_provenance, "coverage_status", None),
                getattr(option_provenance, "integrity_status", None),
            )
        except Exception:
            logger.exception("LIVE VALIDATION CYCLE FAILED")
        finally:
            time.sleep(interval_seconds)


def start_live_validation_worker():
    """Start one validation-only background worker for the Render service."""
    global _worker_started
    enabled = os.getenv("LIVE_VALIDATION_MODE", "").strip().lower() == "true"
    if not enabled:
        return False

    with _worker_lock:
        if _worker_started:
            return False
        _worker_started = True
        thread = threading.Thread(
            target=_poll_loop,
            name="quantnifty-live-validation",
            daemon=True,
        )
        thread.start()
    logger.info("LIVE VALIDATION WORKER STARTED")
    return True
