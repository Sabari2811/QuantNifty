from recording.snapshot_repository import SnapshotRepository


class ReplayService:
    """
    Service layer between Streamlit and the recording repository.
    """

    def __init__(self):

        self.repository = SnapshotRepository()

    # ==========================================================
    # Recordings
    # ==========================================================

    def get_recordings(self):

        return self.repository.list_recordings()