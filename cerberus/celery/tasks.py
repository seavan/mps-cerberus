# encoding: utf-8

from celery import shared_task

@shared_task
def validate(params):
    pass

@shared_task
def transcode(params):
    pass

@shared_task
def upload_to(params):
    pass

@shared_task
def delete_from(params):
    pass
