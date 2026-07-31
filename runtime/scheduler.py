from runtime.market_clock import MarketClock
from runtime.sleep_timer import SleepTimer


class Scheduler:

    def __init__(self):

        self.clock = MarketClock()
        self.timer = SleepTimer()

        self.running = False

    # ==========================================================
    # START
    # ==========================================================

    def start(
        self,
        callback,
        interval=30,
        max_cycles=None
    ):

        if self.running:
            print("Scheduler already running.")
            return

        self.running = True

        print()
        print("=" * 70)
        print("SCHEDULER STARTED")
        print("=" * 70)

        cycle = 0

        try:

            while self.running:

                cycle += 1

                print()
                print("-" * 70)
                print(f"Cycle : {cycle}")
                print("-" * 70)

                status = self.clock.market_status()

                print(f"Market Status : {status}")

                if self.clock.is_market_open():

                    callback()

                else:

                    print("Market Closed.")

                if (
                    max_cycles is not None
                    and cycle >= max_cycles
                ):

                    print()
                    print("=" * 70)
                    print("MAX CYCLES REACHED")
                    print("=" * 70)

                    break

                self.timer.wait(interval)

        except KeyboardInterrupt:

            print()
            print("Scheduler interrupted by user.")

        finally:

            self.running = False

            print()
            print("=" * 70)
            print("SCHEDULER STOPPED")
            print("=" * 70)

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(self):

        self.running = False