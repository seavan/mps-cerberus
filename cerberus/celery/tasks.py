# encoding: utf-8

from celery import shared_task

from cerberus.storage import *
from cerberus.services import *

@shared_task
def transcode_audio(params, storage_config):
    """
    Задача Celery. Выполняет транскодирование audio файла в mp3 и mp4 с
    указанными настройками. Видео файлы используются для публикации на
    сервисах типа YouTube, Vimeo и т.п.

    :param params:
    :param storage_config:
    :return: None
    """

@shared_task
def upload_to(params, service_config, storage_config):
    """
    Задача Celery. Выполняет публикацию материала на указанный
    сервис.

    :param params:
    :param service_config:
    :param storage_config:
    :return: None
    """

    if storage_config['type'] == 'webdav':
        storage = WebDavStorage(url=storage_config['url'])

    if params['service'] == 'youtube':
        config = service_config['youtube']
        uploader = YouTube(config, storage)

    uploader.upload(filename=params['filename'],
        description=params['description'],
        category=params['category'])

@shared_task
def delete_from(params, service_config):
    """
    Задача Celery. Выполняет удаление ранее опубликованного материала с
    указанного сервиса.

    :param params:
    :param service_config:
    :return: None
    """
