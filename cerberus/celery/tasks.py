# encoding: utf-8

import os
import json
import functools

from celery import shared_task

from os.path import splitext
from tempfile import NamedTemporaryFile as TempFile

from cerberus.audio import *
from cerberus.system import *
from cerberus.storages import *
from cerberus.services import *

from .emits import *
from .logger import *

@shared_task
def parse_metadata(message, config):
    """
    Celery Task. Извлекает метаданные из аудио файла

    :param message:
    :param config:
    :return None:
    """

    redis_db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'],
                    decode_responses=True)

    success = functools.partial(emit_success, redis_db,
                        config['redis']['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        config['redis']['queue_name'], message)

    params = message['params']

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])

        storage.download_to(params['input_audio'], input_audio_temp.name)

        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        metadata = get_metadata(input_audio_temp.name)
        for x in [input_audio_temp]:
            os.unlink(x.name)
    except Exception as e:
        fail()
        raise e

    success(metadata)


@shared_task
def transcode_a(message, config):
    """
    Задача Celery. Выполняет транскодирование audio файла в mp3 с указанным
    настройками.

    :param message:
    :param config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'])

    progress = functools.partial(emit_progress, message)

    success = functools.partial(emit_success, redis_db,
                        config['redis']['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        config['redis']['queue_name'], message)

    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])
        output_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['output_audio'])[1])


        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        cmd = config['ffmpeg_command_template'].format(
                                input_audio=input_audio_temp.name,
                                output_audio=output_audio_temp.name)
        info("run command `{0}`".format(cmd))
        run_ffmpeg(cmd, progress_handler=progress)

        storage.upload(output_audio_temp.name, params['output_video'])

        if not config['keep_data']:
            for x in [input_audio_temp, output_audio_temp]:
                os.unlink(x.name)
    except Exception as e:
        fail()
        raise e

    success()


@shared_task
def transcode_av(message, config):
    """
    Задача Celery. Выполняет транскодирование audio файла и изображения в mp4 с
    указанными настройками. Видео файлы используются для публикации на
    сервисах типа YouTube, Vimeo и т.п.

    :param message:
    :param config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'])

    progress = functools.partial(emit_progress, message)

    success = functools.partial(emit_success, redis_db,
                        config['redis']['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        config['redis']['queue_name'], message)

    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = TempFile(delete=False,
                            suffix=splitext(params['input_audio'])[1])
        input_picture_temp = TempFile(delete=False,
                            suffix=splitext(params['input_picture'])[1])
        output_video_temp = TempFile(delete=False,
                            suffix=splitext(params['output_video'])[1])


        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        storage.download_to(params['input_picture'], input_picture_temp.name)
        info("input_picture downloaded to `{0}`".format(input_picture_temp.name))

        cmd = config['ffmpeg_command_template'].format(
                                input_audio=input_audio_temp.name,
                                input_picture=input_picture_temp.name,
                                output_video=output_video_temp.name)
        info("run command `{0}`".format(cmd))
        run_ffmpeg(cmd, progress_handler=progress)

        storage.upload(output_video_temp.name, params['output_video'])

        if not config['keep_data']:
            for x in [input_audio_temp, input_picture_temp, output_video_temp]:
                os.unlink(x.name)
    except Exception as e:
        fail()
        raise e

    success()


@shared_task
def upload(message, config, service_config):
    """
    Задача Celery. Выполняет публикацию материала на указанный
    сервис.

    :param message:
    :param config:
    :param service_config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'])

    success = functools.partial(emit_success, redis_db,
                        config['redis']['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        config['redis']['queue_name'], message)

    params = message['params']

    try:
        storage = create_storage(config['storage'])
        service = create_service(params['service'], service_config, storage)
        service.upload(params['filename'],
            title=params['description'],
            category=params['category'],
            keywords=params['keywords'])
    except Exception as e:
        fail()
        raise e

    success()

@shared_task
def delete(message, config, service_config):
    """
    Задача Celery. Выполняет удаление ранее опубликованного материала с
    указанного сервиса.

    :param message:
    :param config:
    :param service_config:
    :return: None
    """

    redis_db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'])

    success = functools.partial(emit_success, redis_db,
                        config['redis']['queue_name'], message)

    fail = functools.partial(emit_fail, redis_db,
                        config['redis']['queue_name'], message)

    params = message['params']

    try:
        service = create_service(params['service'], service_config)
        service.delete(params['video_id'])
    except Exception as e:
        fail()
        raise e
