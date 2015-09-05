# encoding: utf-8

import os
import json

import redis
import requests
import jsonschema

from .logger import *

schema_filename = schema_filename = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'schemas', 'schemas',
    'callback_task.json')

schema = json.loads(file(schema_filename, 'r').read())

def emit_progress(message, progress):
    event = {
        'id': message['id'],
        'callback_uri': message['callback_uri'],
        'type': 'PROGRESS',
        'params': {
          'progress': progress
        }
    }

    try:
        jsonschema.validate(event, schema)
    except Exception as e:
        error("invalid event: doesn't match by schema, event: {0}".format(event))
        error("error: {0}".format(e))
        return

    # XXX: Убрать хардкод timeout
    info("emit event to {0}: {1}".format(event['callback_uri'], event))
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

    try:
        jsonschema.validate(event, schema)
    except Exception as e:
        error("invalid event: doesn't match by schema, event: {0}".format(event))
        error("error: {0}".format(e))
        return


    info("emit event to {0}: {1}".format(queue, event))
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

    try:
        jsonschema.validate(event, schema)
    except Exception as e:
        error("invalid event: doesn't match by schema, event: {0}".format(event))
        error("error: {0}".format(e))
        return

    info("emit event to {0}: {1}".format(queue, event))
    db.rpush(queue, json.dumps(event, ensure_ascii=False).encode('utf-8'))
