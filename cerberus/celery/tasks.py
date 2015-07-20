# encoding: utf-8

import json
import functools

import redis

from celery import shared_task

from os.path import splitext
from tempfile import NamedTemporaryFile as TempFile

from cerberus.system import *
from cerberus.storage import *
from cerberus.services import *

from .logger import *

def emit_transcode_progress(db, queue, message, progress):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'TRANSCODE_PROGRESS',
        'params': {
          'progress': progress
        }
    }

    info("{0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event))

def emit_success(db, queue, message):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'SUCCESS',
        'params': {}
    }

    info("{0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event))

def emit_fail(db, queue, message):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'FAIL',
        'params': {}
    }

    info("{0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event))

@shared_task
def transcode_av(message, storage_config, redis_config):
    """
    Задача Celery. Выполняет транскодирование audio файла в mp3 и mp4 с
    указанными настройками. Видео файлы используются для публикации на
    сервисах типа YouTube, Vimeo и т.п.

    :param params:
    :param storage_config:
    :param redis_config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=redis_config['host'],
                    port=redis_config['port'],
                    db=redis_config['db'])

    progress = functools.partial(emit_transcode_progress, redis_db,
                        redis_config['queue_name'], message)

    success = functools.partial(emit_success, redis_db,
                        redis_config['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        redis_config['queue_name'], message)

    params = message['params']

    # XXX: Вынести в основной конф. файл
    FFMPEG_COMMAND_TEMPLATE = ('ffmpeg -y -loop 1 '
        '-i {input_picture} -i {input_audio} -shortest '
        '-vcodec libx264 -acodec aac -strict experimental {output_video}')

    info("start task with params: {0}, storage_config: {1}".format(params,
        storage_config))

    if storage_config['type'] == 'webdav':
        storage = WebDavStorage(url=storage_config['url'])
    else:
        error("unknown storage type `{0}`".format(storage_config['type']))
        publish_result("fail: unknown storage type")
        return


    input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])
    input_picture_temp = TempFile(delete=False,
                            suffix=splitext(params['input_picture'])[1])
    output_video_temp = TempFile(delete=False,
                            suffix=splitext(params['output_video'])[1])


    try:
        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        storage.download_to(params['input_picture'], input_picture_temp.name)
        info("input_picture downloaded to `{0}`".format(input_picture_temp.name))
    except Exception as e:
        publish_result("fail: could not download files from storage: {0}".format(e))
        return

    cmd = FFMPEG_COMMAND_TEMPLATE.format(
                                input_audio=input_audio_temp.name,
                                input_picture=input_picture_temp.name,
                                output_video=output_video_temp.name)
    info("run command `{0}`".format(cmd))
    run_ffmpeg(cmd, progress_handler=progress)

    try:
        storage.upload(output_video_temp.name, params['output_video'])
    except Exception as e:
        publish_result("fail: could not upload files to storage")
        return

    success()

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
