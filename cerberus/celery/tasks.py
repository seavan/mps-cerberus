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

class CerberusTaskFail(Exception):
    pass

def emit_transcode_progress(message, progress):
    event = {
        'id': message['id'],
        'type': 'TRANSCODE_PROGRESS',
        'params': {
          'progress': progress
        }
    }

    # XXX: Убрать хардкод timeout
    info("{0}: {1}".format(event))
    try:
        requests.post(message['callback_uri'], data=json.dumps(event), timeout=2)
    except Exception as e:
        warn("could not send progress event: {0}".format(e))

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

    progress = functools.partial(emit_transcode_progress, message)

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
        fail()
        raise CerberusTaskFail("unknown storage type `{0}`".format(
            storage_config['type']))

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
        fail()
        raise CerberusTaskFail("could not download files from storage: {0}".format(e))

    cmd = FFMPEG_COMMAND_TEMPLATE.format(
                                input_audio=input_audio_temp.name,
                                input_picture=input_picture_temp.name,
                                output_video=output_video_temp.name)
    info("run command `{0}`".format(cmd))
    run_ffmpeg(cmd, progress_handler=progress)

    try:
        storage.upload(output_video_temp.name, params['output_video'])
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not upload files to storage")

    success()

@shared_task
def upload_to(params, service_config, storage_config, redis_config):
    """
    Задача Celery. Выполняет публикацию материала на указанный
    сервис.

    :param params:
    :param service_config:
    :param storage_config:
    :param redis_config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=redis_config['host'],
                    port=redis_config['port'],
                    db=redis_config['db'])

    success = functools.partial(emit_success, redis_db,
                        redis_config['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        redis_config['queue_name'], message)


    if storage_config['type'] == 'webdav':
        storage = WebDavStorage(url=storage_config['url'])
    else:
        fail()
        raise CerberusTaskFail("unknown storage type `{0}`".format(
            storage_config['type']))

    if params['service'] == 'youtube':
        config = service_config['youtube']
        uploader = YouTube(config, storage)
    else:
        fail()
        raise CerberusTaskFail("unknown service type `{0}`".format(
            params['service'])

    try:
        uploader.upload(filename=params['filename'],
            description=params['description'],
            category=params['category'])
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not upload `{0}` to {1}".format(
            params['filename'], params['service'])

    success()

@shared_task
def delete_from(params, service_config):
    """
    Задача Celery. Выполняет удаление ранее опубликованного материала с
    указанного сервиса.

    :param params:
    :param service_config:
    :return: None
    """
