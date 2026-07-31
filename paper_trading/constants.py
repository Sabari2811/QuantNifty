from enum import Enum


class OrderStatus(str, Enum):

    OPEN = "OPEN"

    CLOSED = "CLOSED"

    CANCELLED = "CANCELLED"


class ExitReason(str, Enum):

    TARGET = "TARGET"

    STOP_LOSS = "STOP_LOSS"

    END_OF_DAY = "END_OF_DAY"

    OPPOSITE_SIGNAL = "OPPOSITE_SIGNAL"

    MANUAL = "MANUAL"


class SignalType(str, Enum):

    BUY_CALL = "BUY_CALL"

    BUY_PUT = "BUY_PUT"

    WAIT = "WAIT"