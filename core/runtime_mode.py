from enum import Enum


class RuntimeMode(str, Enum):
    LIVE = "LIVE"
    REPLAY = "REPLAY"
    SIMULATION = "SIMULATION"