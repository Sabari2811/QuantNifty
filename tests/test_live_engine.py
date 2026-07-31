import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from engine.live_engine import LiveEngine


def main():

    print("=" * 70)
    print("TESTING LIVE ENGINE")
    print("=" * 70)

    engine = LiveEngine()

    ctx = engine.run_cycle()

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print("Spot               :", ctx.spot)
    print("Option Chain       :", ctx.option_chain is not None)
    print("Greeks DF          :", ctx.greeks_df is not None)
    print("Candles            :", ctx.candles is not None)
    print("Analytics          :", ctx.analytics is not None)
    print("Snapshot           :", ctx.snapshot is not None)
    print("Decision           :", ctx.decision is not None)
    print("Portfolio          :", ctx.portfolio is not None)
    print("Cycle              :", ctx.cycle_no)
    print("Runtime Status     :", ctx.runtime_status)


if __name__ == "__main__":

    main()