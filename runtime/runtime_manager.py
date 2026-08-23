import threading

from engine.live_engine import LiveEngine

from providers.indmoney_provider import INDMoneyProvider
from providers.simulation_provider import SimulationProvider

from runtime.runtime_mode import RuntimeMode
from runtime.scheduler import Scheduler
from runtime.composition import CompositionRoot


class RuntimeManager:
    """Own the single canonical QuantNifty runtime."""

    _instance = None

    def __new__(cls, mode: RuntimeMode = RuntimeMode.LIVE, replay_session=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(mode, replay_session)
        return cls._instance

    def _initialize(self, mode, replay_session):
        self.mode = mode
        self.composition = CompositionRoot()
        self.provider = self._create_provider(mode, replay_session)
        self.engine = LiveEngine(
            provider=self.provider,
            intelligence_service=self.composition.intelligence_service,
            paper_broker=self.composition.paper_broker,
            trade_pipeline=self.composition.trade_pipeline,
        )
        self.scheduler = Scheduler()
        self.running = False
        self.thread = None

    def _create_provider(self, mode, replay_session):
        if mode == RuntimeMode.LIVE:
            return INDMoneyProvider()

        if mode in (RuntimeMode.REPLAY_FAST, RuntimeMode.REPLAY_RECOMPUTE):
            if replay_session is None:
                raise ValueError("ReplaySession is required.")
            return SimulationProvider(
                replay_source=replay_session,
                runtime_mode=mode,
            )

        raise ValueError(f"Unsupported runtime mode: {mode}")

    def start(self, interval=30):
        if self.running:
            print("Runtime already running.")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self.scheduler.start,
            kwargs={
                "callback": self.engine.run_cycle,
                "interval": interval,
            },
            daemon=True,
        )
        self.thread.start()
        print(f"Runtime started ({self.mode.value}).")

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.scheduler.stop()
        if self.thread is not None:
            self.thread.join(timeout=2)
            self.thread = None
        print("Runtime stopped.")

    def run_once(self, symbol=None, levels=None):
        """Run one canonical runtime cycle for the requested dashboard state."""
        if symbol:
            self.engine.ctx.symbol = symbol
        if levels is not None:
            if not isinstance(levels, int) or not 2 <= levels <= 10:
                raise ValueError("levels must be an integer between 2 and 10")
            self.engine.ctx.strike_levels = levels
        return self.engine.run_cycle()

    def get_context(self):
        return self.engine.ctx

    def get_engine(self):
        return self.engine

    def get_provider(self):
        return self.provider

    def is_running(self):
        return self.running
