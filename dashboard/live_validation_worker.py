import json
import os
import threading
from datetime import datetime, time as dt_time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

from brain.adaptive_brain import AdaptiveBrain
from core.logger import logger
from engine.live_engine import LiveEngine
from monitoring.live_session_evidence import build_live_cycle_evidence, create_live_evidence_store
from providers.indmoney_provider import INDMoneyProvider


IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 40)
DEFAULT_INTERVAL_SECONDS = 60
MIN_INTERVAL_SECONDS = 5

_worker_lock = threading.Lock()
_worker_started = False
_health_lock = threading.Lock()
_health_state = {
    "status": "starting",
    "last_cycle_at": None,
    "last_cycle_no": None,
    "last_error": None,
    "cycles": 0,
}


def is_nse_derivatives_session_open(now=None):
    """Return True only during normal NSE equity-derivatives hours on weekdays."""
    current = now.astimezone(IST) if now is not None else datetime.now(IST)
    return current.weekday() < 5 and MARKET_OPEN <= current.time() <= MARKET_CLOSE


def get_validation_interval_seconds(value=None):
    """Return a safe worker polling interval, defaulting to one minute."""
    raw = value if value is not None else os.getenv("LIVE_VALIDATION_INTERVAL_SECONDS")
    if raw is None or str(raw).strip() == "":
        return DEFAULT_INTERVAL_SECONDS
    try:
        interval = int(raw)
    except (TypeError, ValueError):
        logger.warning(
            "LIVE VALIDATION INTERVAL INVALID | value=%r | using=%ss",
            raw,
            DEFAULT_INTERVAL_SECONDS,
        )
        return DEFAULT_INTERVAL_SECONDS
    if interval < MIN_INTERVAL_SECONDS:
        logger.warning(
            "LIVE VALIDATION INTERVAL TOO SMALL | value=%ss | using=%ss",
            interval,
            MIN_INTERVAL_SECONDS,
        )
        return MIN_INTERVAL_SECONDS
    return interval


def _health_snapshot():
    with _health_lock:
        return dict(_health_state)


def _mark_health(**updates):
    with _health_lock:
        _health_state.update(updates)


class _HealthHandler(BaseHTTPRequestHandler):
    """Small dependency-free HTTP endpoint so Render can keep the worker alive."""

    def do_GET(self):  # noqa: N802
        if self.path not in {"/", "/healthz"}:
            self.send_response(404)
            self.end_headers()
            return
        payload = _health_snapshot()
        payload["live_validation_mode"] = os.getenv("LIVE_VALIDATION_MODE", "").strip().lower() == "true"
        payload["market_open"] = is_nse_derivatives_session_open()
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A003
        return


def _start_health_server(stop_event):
    """Bind Render's PORT and serve a lightweight liveness endpoint."""
    raw_port = os.getenv("PORT", "10000")
    try:
        port = int(raw_port)
    except (TypeError, ValueError):
        raise RuntimeError(f"Invalid PORT value: {raw_port!r}")
    if not 1 <= port <= 65535:
        raise RuntimeError(f"Invalid PORT value: {port!r}")

    server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
    server.daemon_threads = True
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.5},
        name="quantnifty-health-server",
        daemon=True,
    )
    thread.start()

    def shutdown_watcher():
        stop_event.wait()
        server.shutdown()
        server.server_close()

    threading.Thread(
        target=shutdown_watcher,
        name="quantnifty-health-shutdown",
        daemon=True,
    ).start()
    logger.info("LIVE VALIDATION HEALTH SERVER STARTED | port=%s", port)
    return server


def _initialize_runtime():
    evidence_store = create_live_evidence_store()
    brain = AdaptiveBrain()
    provider = INDMoneyProvider()
    engine = LiveEngine(provider=provider)
    logger.info(
        "LIVE VALIDATION WORKER READY | evidence_store=%s | brain_store=%s",
        type(evidence_store).__name__,
        type(brain.store).__name__,
    )
    return evidence_store, brain, provider, engine


def _persistence_status(evidence_store, brain):
    """Report durable persistence only when both required stores are durable."""
    brain_durable = getattr(brain.store, "_sql_store", None) is not None
    evidence_durable = bool(getattr(evidence_store, "durable", False))
    return "DURABLE_DATABASE" if brain_durable and evidence_durable else "LOCAL_OR_PARTIAL"


def run_validation_cycle(evidence_store, brain, provider, engine):
    """Execute exactly one validation-only live cycle and persist its evidence."""
    ctx = engine.run_cycle()
    brain_result = brain.observe(ctx, broker=engine.paper_broker)
    ctx.brain_status = brain_result.status
    ctx.learning_status = "LEARNED" if brain_result.status == "LEARNED" else "PENDING_OUTCOME"
    ctx.persistence_status = _persistence_status(evidence_store, brain)

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
    return ctx, evidence


def _poll_loop(interval_seconds=DEFAULT_INTERVAL_SECONDS, stop_event=None):
    """Run continuously until the host requests shutdown."""
    stop_event = stop_event or threading.Event()
    evidence_store, brain, provider, engine = _initialize_runtime()
    interval_seconds = get_validation_interval_seconds(interval_seconds)

    while not stop_event.is_set():
        try:
            now = datetime.now(IST)
            if is_nse_derivatives_session_open(now):
                ctx, evidence = run_validation_cycle(
                    evidence_store,
                    brain,
                    provider,
                    engine,
                )
                provenance = getattr(ctx, "data_provenance", None)
                option_provenance = getattr(provenance, "option_chain", None) if provenance else None
                _mark_health(
                    status="running",
                    last_cycle_at=now.isoformat(),
                    last_cycle_no=getattr(ctx, "cycle_no", None),
                    last_error=None,
                    cycles=_health_snapshot()["cycles"] + 1,
                )
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
            else:
                _mark_health(status="waiting_for_market", last_error=None)
        except Exception as exc:
            _mark_health(status="error", last_error=type(exc).__name__)
            logger.exception("LIVE VALIDATION CYCLE FAILED")

        stop_event.wait(interval_seconds)


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
        interval_seconds = get_validation_interval_seconds()
        thread = threading.Thread(
            target=_poll_loop,
            kwargs={"interval_seconds": interval_seconds},
            name="quantnifty-live-validation",
            daemon=True,
        )
        thread.start()
    logger.info("LIVE VALIDATION WORKER STARTED | interval=%ss", interval_seconds)
    return True


def run_live_validation_worker(interval_seconds=None):
    """Run validation as a foreground process with a Render-compatible health endpoint."""
    enabled = os.getenv("LIVE_VALIDATION_MODE", "").strip().lower() == "true"
    if not enabled:
        logger.info("LIVE VALIDATION WORKER DISABLED | set LIVE_VALIDATION_MODE=true to enable")
        return 0

    interval_seconds = get_validation_interval_seconds(interval_seconds)
    stop_event = threading.Event()
    server = _start_health_server(stop_event)
    logger.info("LIVE VALIDATION WORKER FOREGROUND START | interval=%ss", interval_seconds)
    try:
        _poll_loop(interval_seconds=interval_seconds, stop_event=stop_event)
    except KeyboardInterrupt:
        logger.info("LIVE VALIDATION WORKER STOPPED | reason=keyboard_interrupt")
    finally:
        stop_event.set()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_live_validation_worker())
