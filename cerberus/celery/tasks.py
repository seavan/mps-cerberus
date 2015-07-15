# encoding: utf-8

from celery import shared_task

from cerberus.storage import *
from cerberus.services import *

@shared_task
def validate(params):
    pass

@shared_task
def transcode(params):
    pass

@shared_task
def upload_to(params, storage_config, service_config):

    if storage_config['type'] == 'webdav':
        storage = WebDavStorage(url=storage_config['url'])

    if params['service'] == 'youtube':
        config = service_config['youtube']
        uploader = YouTube(config, storage)

    uploader.upload(filename=params['filename'],
        description=params['description'],
        category=params['category'])

@shared_task
def delete_from(params):
    pass
