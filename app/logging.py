from loguru import logger
import sys


def setup_logging() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", backtrace=False, diagnose=False)


__all__ = ["logger", "setup_logging"]
