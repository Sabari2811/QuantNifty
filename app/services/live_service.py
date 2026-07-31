from runtime.runtime_manager import RuntimeManager


class LiveService:
    """
    Bridge between the UI and the QuantNifty runtime.

    Ensures the first market cycle is executed before
    the dashboard attempts to consume RuntimeContext.
    """

    def __init__(self):

        self.runtime = RuntimeManager()

    # ==========================================================
    # GET CURRENT CONTEXT
    # ==========================================================

    def get_context(self):

        ctx = self.runtime.get_context()

        # ------------------------------------------------------
        # First dashboard request
        # RuntimeContext.timestamp defaults to ""
        # so we check for any falsy value.
        # ------------------------------------------------------

        if not ctx.timestamp:

            ctx = self.runtime.run_once()

        return ctx

    # ==========================================================
    # MANUAL REFRESH
    # ==========================================================

    def refresh(self):
        """
        Executes one complete market cycle.

        Used by:
            - CLI
            - Testing
            - Manual Refresh button
        """

        return self.runtime.run_once()

    # ==========================================================
    # START BACKGROUND RUNTIME
    # ==========================================================

    def start(self):

        self.runtime.start()

    # ==========================================================
    # STOP BACKGROUND RUNTIME
    # ==========================================================

    def stop(self):

        self.runtime.stop()