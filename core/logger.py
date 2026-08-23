"""Shared application logger for QuantNifty.

The runtime imports ``logger`` from this module from multiple layers.  Keep
this module deliberately small and dependency-free so importing the runtime
does not depend on application/UI configuration.
"""

import logging
import sys


LOGGER_NAME = "quantnifty"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


logger = _build_logger()

__all__ = ["logger"]
