from runtime.runtime_manager import RuntimeManager


class LiveCycle:
    """
    Executes one complete market cycle.

    Scheduler calls this class repeatedly.
    """

    def __init__(self):

        self.runtime = RuntimeManager()

    def cycle(self):

        return self.runtime.run_once()

    def get_context(self):

        return self.runtime.get_context()

    def get_engine(self):

        return self.runtime.get_engine()