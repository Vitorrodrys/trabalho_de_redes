import logging

from .settings import environment_settings


def init_logging():
    warnings = []
    levelstr = environment_settings.log_level
    levelobj = logging.getLevelName(levelstr)

    logger = logging.getLogger()
    logger.setLevel(levelobj)

    logging.log(
        levelobj, "Logging with loglevel %s (%d)", levelstr, levelobj
    )
    for msg in warnings:
        logging.warning(msg)
