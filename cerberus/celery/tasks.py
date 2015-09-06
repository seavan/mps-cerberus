# encoding: utf-8

import os
import json
import tempfile

from copy import deepcopy
from shutil import rmtree
from functools import partial
from os.path import splitext, join, basename

from celery import shared_task

from cerberus.audio import *
from cerberus.system import *
from cerberus.storages import *
from cerberus.services import *

from .emits import *
from .logger import *

class Context(object):
    def __init__(self, message, config):
        self.message = message
        self.config = config
        self.db = redis.StrictRedis(host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'],
                    decode_responses=True)
        self.dirs_to_remove = []
        self.files_to_remove = []

        self.progress = partial(emit_progress, self.message)

    def fail(self, exc):
        return emit_fail(self.db, self.config['redis']['queue_name'],
                    self.message, exc)

    def success(self, params={}):
        return emit_success(self.db, self.config['redis']['queue_name'],
                    self.message, params)

    def mktemp(self, suffix=None):
        f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        self.files_to_remove.append(f)
        return f

    def mkdtemp(self):
        d = tempfile.mkdtemp()
        self.dirs_to_remove.append(d)
        return d

    def clean(self):
        try:
            if not self.config['keep_data']:
                for x in self.files_to_remove:
                    os.unlink(x.name)

                for x in self.dirs_to_remove:
                    rmtree(x)
        except:
            pass

@shared_task
def parse_metadata(message, config):
    """
    Celery Task. Извлекает метаданные из аудио файла

    :param message:
    :param config:
    :return None:
    """

    ctx = Context(message, config)
    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = ctx.mktemp(suffix=splitext(params['input_audio'])[1])

        storage.download_to(params['input_audio'], input_audio_temp.name)

        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        metadata = get_metadata(input_audio_temp.name)
    except Exception as e:
        ctx.fail(e)
        raise
    finally:
        ctx.clean()

    ctx.success(metadata)


@shared_task
def transcode_a(message, config):
    """
    Задача Celery. Выполняет транскодирование audio файла в mp3 с указанным
    настройками.

    :param message:
    :param config:
    :return: None
    """

    ctx = Context(message, config)
    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = ctx.mktemp(suffix=splitext(params['input_audio'])[1])
        output_audio_temp = ctx.mktemp(suffix=splitext(params['output_audio'])[1])

        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        cmd = config['ffmpeg_command_template'].format(
                                input_audio=input_audio_temp.name,
                                output_audio=output_audio_temp.name)
        info("run command `{0}`".format(cmd))
        run_ffmpeg(cmd, progress_handler=ctx.progress)

        storage.upload(output_audio_temp.name, params['output_video'])

    except Exception as e:
        ctx.fail(e)
        raise
    finally:
        ctx.clean()

    ctx.success()


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

    ctx = Context(message, config)
    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        storage = create_storage(config['storage'])

        input_audio_temp = ctx.mktemp(suffix=splitext(params['input_audio'])[1])
        input_picture_temp = ctx.mktemp(suffix=splitext(params['input_picture'])[1])
        output_video_temp = ctx.mktemp(suffix=splitext(params['output_video'])[1])

        storage.download_to(params['input_audio'], input_audio_temp.name)
        info("input_audio downloaded to `{0}`".format(input_audio_temp.name))

        storage.download_to(params['input_picture'], input_picture_temp.name)
        info("input_picture downloaded to `{0}`".format(input_picture_temp.name))

        cmd = config['ffmpeg_command_template'].format(
                                input_audio=input_audio_temp.name,
                                input_picture=input_picture_temp.name,
                                output_video=output_video_temp.name)
        info("run command `{0}`".format(cmd))
        run_ffmpeg(cmd, progress_handler=ctx.progress)

        storage.upload(output_video_temp.name, params['output_video'])

    except Exception as e:
        ctx.fail(e)
        raise
    finally:
        ctx.clean()

    ctx.success()


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

    ctx = Context(message, config)
    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        temp_dir = ctx.mkdtemp()
        input_file_temp = join(temp_dir, basename(params['input_file']))

        storage = create_storage(config['storage'])
        storage.download_to(params['input_file'], input_file_temp)

        service = create_service(params['service'], service_config)

        upload_params = deepcopy(params)
        upload_params.pop('input_file')
        upload_params.pop('service')
        upload_params['filename'] = input_file_temp

        metadata = service.upload(**upload_params)
    except Exception as e:
        ctx.fail(e)
        raise
    finally:
        ctx.clean()

    ctx.success(metadata)

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

    ctx = Context(message, config)
    params = message['params']

    info("start task with params: {0}, config: {1}".format(params, config))

    try:
        service = create_service(params['service'], service_config)

        delete_params = deepcopy(params)
        delete_params.pop('service')

        service.delete(**delete_params)
    except Exception as e:
        ctx.fail(e)
        raise
    finally:
        ctx.clean()

    ctx.success()
