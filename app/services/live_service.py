from runtime.runtime_manager import RuntimeManager


class LiveService:
    """
    Compatibility adapter for legacy UI pages.

    This service does not own market-data acquisition. It delegates
    every operation to the single canonical RuntimeManager so legacy
    pages cannot create a second runtime/data path.
    """

    def __init__(self):
        self.runtime = RuntimeManager()

    def get_context(self):
        """Return the canonical RuntimeContext, running one cycle if needed."""
        ctx = self.runtime.get_context()

        if not ctx.timestamp:
            ctx = self.runtime.run_once()

        return ctx

    def refresh(self):
        """Execute one canonical market cycle."""
        return self.runtime.run_once()

    def start(self):
        """Start the canonical runtime scheduler."""
        self.runtime.start()

    def stop(self):
        """Stop the canonical runtime scheduler."""
        self.runtime.stop()
