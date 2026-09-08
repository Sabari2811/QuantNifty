import os
import threading
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

from brain.adaptive_brain import AdaptiveBrain
from core.logger import logger
from engine.live_engine import LiveEngine
from monitoring.live_session_evidence import build_live_cycle_evidence, create_live_evidence_store
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
        evidence_store = create_live_evidence_store()
        brain = AdaptiveBrain()
        provider = INDMoneyProvider()
        engine = LiveEngine(provider=provider)
        logger.info(
            "LIVE VALIDATION WORKER READY | interval=%ss | evidence_store=%s | brain_store=%s",
            interval_seconds,
            type(evidence_store).__name__,
            type(brain.store).__name__,
        )
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
            brain_result = brain.observe(ctx, broker=engine.paper_broker)
            ctx.brain_status = brain_result.status
            ctx.learning_status = "LEARNED" if brain_result.status == "LEARNED" else "PENDING_OUTCOME"
            persistence = "DURABLE_DATABASE" if getattr(brain.store, "_sql_store", None) is not None else "LOCAL_EPHEMERAL"
            ctx.persistence_status = persistence

            # The worker itself is the authoritative source for provider mode;
            # never fall back to an environment variable that could mislabel a
            # replay/simulation process as live.
            provider_name = getattr(provider, "provider_name", None) or getattr(provider, "name", None) or "INDMONEY"
            provider_mode = "LIVE_PROVIDER" if isinstance(provider, INDMoneyProvider) else "UNKNOWN"
            evidence = build_live_cycle_evidence(
                ctx,
                provider=str(provider_name),
                provider_mode=provider_mode,
                brain_status=ctx.brain_status,
                learning_status=ctx.learning_status,
                persistence_status=ctx.persistence_status,
            )
            evidence_store.append(evidence)
            provenance = getattr(ctx, "data_provenance", None)
            option_provenance = getattr(provenance, "option_chain", None) if provenance else None
            logger.info(
                "LIVE VALIDATION CYCLE | timestamp=%s | cycle=%s | spot=%s | runtime=%s | "
                "trade_status=%s | block_reason=%s | option_chain_coverage=%s | option_chain_integrity=%s | "
                "provider=%s | provider_mode=%s | brain=%s | learning=%s | persistence=%s | "
                "evidence=%s | evidence_count=%s",
                now.isoformat(),
                getattr(ctx, "cycle_no", None),
                getattr(ctx, "spot", None),
                getattr(ctx, "runtime_status", None),
                getattr(ctx, "trade_status", None),
                getattr(ctx, "trade_block_reason", None),
                getattr(option_provenance, "coverage_status", None),
                getattr(option_provenance, "integrity_status", None),
                evidence.provider,
                evidence.provider_mode,
                evidence.brain_status,
                evidence.learning_status,
                evidence.persistence_status,
                evidence.evidence_state,
                evidence_store.count(),
            )
        except Exception:
            logger.exception("LIVE VALIDATION CYCLE FAILED")
        finally:
            time.sleep(interval_seconds)


def start_live_validation_worker():
    """Start one validation-only background worker for embedding hosts."""
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


def run_live_validation_worker(interval_seconds=60):
    """Run validation as a foreground process, independent of Streamlit."""
    enabled = os.getenv("LIVE_VALIDATION_MODE", "").strip().lower() == "true"
    if not enabled:
        logger.info("LIVE VALIDATION WORKER DISABLED | set LIVE_VALIDATION_MODE=true to enable")
        return 0

    logger.info("LIVE VALIDATION WORKER FOREGROUND START | interval=%ss", interval_seconds)
    _poll_loop(interval_seconds=interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_live_validation_worker())
