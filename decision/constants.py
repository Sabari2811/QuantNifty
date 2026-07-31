from enum import Enum


class Signal(Enum):
    BUY_CALL = "BUY CALL"
    BUY_PUT = "BUY PUT"
    WAIT = "WAIT"


class OptionType(Enum):
    CE = "CE"
    PE = "PE"


class DealerPosition(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class InstitutionalFlow(Enum):
    STRONG = "STRONG"
    WEAK = "WEAK"
    NEUTRAL = "NEUTRAL"