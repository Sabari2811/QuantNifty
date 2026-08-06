from simulation.replay_controller import ReplayController
from simulation.replay_state import ReplayState

from app.services.replay_loader_service import ReplayLoaderService


class ReplayControllerService:
    """
    Creates and manages ReplayController instances.

    The UI should never construct ReplaySession,
    ReplayState or ReplayController directly.
    """

    def __init__(self):

        self.loader = ReplayLoaderService()

    # ==========================================================
    # Controller
    # ==========================================================

    def load(self, recording):

        session = self.loader.load(recording)

        state = ReplayState()

        controller = ReplayController(

            session=session,

            state=state

        )

        return controller