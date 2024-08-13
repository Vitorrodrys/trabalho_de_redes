from enum import StrEnum
import logging

from .settings import enviroment_settings

class LogLevelsEnum(StrEnum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warn = "WARN"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"


def init_logging():
    warnings = []
    levelstr = enviroment_settings.log_level
    levelobj = logging.getLevelName(levelstr)

    logger = logging.getLogger()
    logger.setLevel(levelobj)

    logging.log(
        levelobj, "Logging with loglevel %s (%d)", levelstr, levelobj
    )
    for msg in warnings:
        logging.warning(msg)
