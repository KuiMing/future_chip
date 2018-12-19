import logging
import os

LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARN': logging.WARN,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL
}
level = LOG_LEVEL_MAP.get(
    os.getenv('LOG_LEVEL', 'ERROR').upper(), logging.ERROR)
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(levelname)s [ %(asctime)s ] %(message)s', level=level)
