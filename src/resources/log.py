import logging
import datetime
import os
import constants

if constants.DEBUG:
    pt = None
else:
    pt = os.path.join(os.path.expanduser('~'), './.underia', 'logs')

    if not os.path.exists(pt):
        os.makedirs(pt)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not constants.DEBUG:
    file_handler = logging.FileHandler(os.path.join(pt, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'))
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    file_handler.setFormatter(formatter)


    logger.addHandler(file_handler)

else:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)


def debug(message):
    logger.debug(message)

def info(message):
    logger.info(message)

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)

def critical(message):
    logger.critical(message)