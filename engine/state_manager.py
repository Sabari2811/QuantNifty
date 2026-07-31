class StateManager:
    """
    Keeps previous market snapshot in memory.

    Future:
        Redis
        SQLite
        PostgreSQL
    """

    def __init__(self):

        self.previous_snapshot = None

    def get_previous_snapshot(self):

        return self.previous_snapshot

    def update_snapshot(self, snapshot):

        self.previous_snapshot = snapshot

    def clear(self):

        self.previous_snapshot = None