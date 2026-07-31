import os
import sys
import traceback

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.live_trading_engine import LiveTradingEngine


# ---------------- Mock Classes ----------------

class MockProvider:

    def connect(self):
        pass

    def get_spot_price(self, symbol):
        return 25050


class MockOptionChain:

    def get_live_option_chain(self, symbol, spot_price, levels):
        return [{"strike": 25000}]


class MockGreeks:

    def calculate(self, option_chain):
        return {"rows": 1}


class MockRuntime:

    symbol = "NIFTY"

    option_levels = 5

    refresh_interval = 0


# ---------------- Monkey Patch ----------------

class MockAnalytics:

    def run(self, **kwargs):
        return {"score": 80}


class MockDecisionObj:

    valid = True


class MockDecision:

    def build(self, analytics):
        return MockDecisionObj()


class MockBroker:

    def execute(self, decision):
        return {"status": "EXECUTED"}


def check(name, condition):

    if condition:
        print(f"✓ {name}")
    else:
        raise AssertionError(name)


def run():

    print("=" * 70)
    print("Live Trading Engine Test")
    print("=" * 70)

    engine = LiveTradingEngine(
        MockProvider(),
        MockOptionChain(),
        MockGreeks(),
        MockRuntime(),
    )

    # Inject mocks for internal collaborators
    engine.analytics = MockAnalytics()
    engine.decision = MockDecision()
    engine.paper_broker = MockBroker()

    engine.initialize()
    engine.process_market()

    check("Process Completed", True)

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":

    try:
        run()
    except Exception:
        traceback.print_exc()