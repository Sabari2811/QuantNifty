from datetime import datetime
import time


class SleepTimer:

    def wait(self, interval=30):

        now = datetime.now()

        current = now.timestamp()

        next_tick = (
            (int(current / interval) + 1)
            * interval
        )

        sleep_time = next_tick - current

        if sleep_time > 0:

            print()

            print("-" * 70)
            print(f"Sleeping {sleep_time:.2f} seconds...")
            print("-" * 70)

            time.sleep(sleep_time)