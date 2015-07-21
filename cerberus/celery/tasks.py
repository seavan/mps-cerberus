# encoding: utf-8

import json
import functools

from celery import shared_task

from os.path import splitext
from tempfile import NamedTemporaryFile as TempFile

from cerberus.audio import *
from cerberus.system import *
from cerberus.storage import *
from cerberus.services import *

from .emits import *
from .logger import *

class CerberusTaskFail(Exception):
    pass

@shared_task
def parse_metadata(message, storage_config, redis_config):

    redis_db = redis.StrictRedis(host=redis_config['host'],
                    port=redis_config['port'],
                    db=redis_config['db'])

    success = functools.partial(emit_success, redis_db,
                        redis_config['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        redis_config['queue_name'], message)

    params = message['params']

    try:
        storage = create_storage(storage_config)
    except Exception as e:
        fail()
        raise CerberusTaskFail("unknown storage type `{0}`".format(
            storage_config['type']))

    input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])

    try:
        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not download files from storage: {0}".format(e))

    try:
        metadata = parse_metadata(input_audio_temp)
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not parse file {0}: {1}".format(
            params['input_audio'], e))

    success(metadata)

@shared_task
def transcode_a(message, storage_config, redis_config):
    """
    Задача Celery. Выполняет транскодирование audio файла в mp3 с указанным
    настройками.

    :param params:
    :param storage_config:
    :param redis_config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=redis_config['host'],
                    port=redis_config['port'],
                    db=redis_config['db'])

    progress = functools.partial(emit_progress, message)

    success = functools.partial(emit_success, redis_db,
                        redis_config['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        redis_config['queue_name'], message)

    params = message['params']

    # XXX: Вынести в основной конф. файл
    FFMPEG_COMMAND_TEMPLATE = "/usr/bin/ffmpeg -i {input_audio} -f mp2 {output_audio}"

    info("start task with params: {0}, storage_config: {1}".format(params,
        storage_config))

    try:
        storage = create_storage(storage_config)
    except Exception as e:
        fail()
        raise CerberusTaskFail("unknown storage type `{0}`".format(
            storage_config['type']))

    input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])
    output_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['output_audio'])[1])


    try:
        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not download files from storage: {0}".format(e))

    cmd = FFMPEG_COMMAND_TEMPLATE.format(
                                input_audio=input_audio_temp.name,
                                output_audio=output_audio_temp.name)
    info("run command `{0}`".format(cmd))
    run_ffmpeg(cmd, progress_handler=progress)

    try:
        storage.upload(output_audio_temp.name, params['output_video'])
    except Exception as e:
        fail()
        raise CerberusTaskFail("could not upload files to storage")

    success()


@shared_task
def transcode_av(message, storage_config, redis_config):
    """
    Задача Celery. Выполняет транскодирование audio файла и изображения в mp4 с
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

    progress = functools.partial(emit_progress, message)

    success = functools.partial(emit_success, redis_db,
                        redis_config['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        redis_config['queue_name'], message)

    params = message['params']

    # XXX: Вынести в основной конф. файл
    FFMPEG_COMMAND_TEMPLATE = ('/usr/bin/ffmpeg -y -loop 1 '
        '-i {input_picture} -i {input_audio} -shortest '
        '-vcodec libx264 -acodec aac -strict experimental {output_video}')

    info("start task with params: {0}, storage_config: {1}".format(params,
        storage_config))

    try:
        storage = create_storage(storage_config)
    except Exception as e:
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
def parse(params, storage_config, redis_config):
    """
    Задача Celery. Выполняет парсинг ID3 тегов в mp3 файле и
    публикует полученные данные.

    :param params:
    :param storage_config:
    :param redis_config:
    """
    pass

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

    try:
        storage = create_storage(storage_config)
    except Exception as e:
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
