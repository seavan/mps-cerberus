# encoding: utf-8

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def info(message):
    logger.info(message)

def warn(message):
    logger.warn(message)

def error(message):
    logger.error(message)

def debug(message):
    logger.debug(message)
