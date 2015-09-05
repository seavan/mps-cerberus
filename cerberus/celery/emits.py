# encoding: utf-8

import json

import redis
import requests

from .logger import *

def emit_progress(message, progress):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'PROGRESS',
        'params': {
          'progress': progress
        }
    }

    # XXX: Убрать хардкод timeout
    info("progress: {0}".format(event))
    try:
        requests.post(message['callback_uri'],
            data=json.dumps(event, ensure_ascii=False), timeout=1)
    except Exception as e:
        warn("could not send progress event: {0}".format(e))

def emit_success(db, queue, message, params={}):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'SUCCESS',
        'params': params
    }

    info("{0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event, ensure_ascii=False).encode('utf-8'))

def emit_fail(db, queue, message, exception):
    if hasattr(exception, 'code') and hasattr(exception, 'message'):
        err_code = exception.code
        err_message = exception.message
    else:
        err_code = 600
        err_message = "Internal backend error"

    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'FAIL',
        'params': {
          'code': err_code,
          'message': err_message
        }
    }

    info("{0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event, ensure_ascii=False).encode('utf-8'))
