# encoding: utf-8

import os
import json

import bottle
import eventlet
import jsonschema

from .logger import *
from .celery.tasks import *

def json_response(*args, **kwargs):
    r = bottle.HTTPResponse(*args, **kwargs)
    r.add_header('Content-Type', 'application/json')
    return r

class Cerberus(object):
    def __new__(cls, *args, **kwargs):
        obj = super(Cerberus, cls).__new__(cls, *args, **kwargs)
        bottle.post("/")(obj.http_api_handler)
        return obj

    def __init__(self, config, app):
        self.config = config

        schema_filename = schema_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'schemas', 'schemas',
            'publish_task.json')
        self.schema = json.loads(file(schema_filename, 'r').read())
        self.app = app

    def http_api_handler(self):
        try:
            message = bottle.request.json
        except Exception as e:
            error("invalid request: malformed json")
            r = json_response(status=400)
            return r

        if message is None:
            error("invalid request: no Content-Type header")
            r = json_response(status=400)
            return r

        try:
            jsonschema.validate(message, self.schema)
        except Exception as e:
            error("invalid request: doesn't match by schema")
            r = json_response(status=400)
            return r

        if message['type'] == "TRANSCODE_AV":
            transcode_av.delay(message,
                storage_config=self.config['transcode']['storage'],
                redis_config=self.config['transcode']['redis'])

        elif message['type'] == "UPLOAD_TO":
            upload_to.delay(message['params'],
                service_config=self.config['service'],
                storage_config=self.config['storage'])

        elif message['type'] == "DELETE_FROM":
            delete_from.delay(message['params'],
                service_config=self.config['service'])

        else:
            r = json_response(status=400)
            return r

        r = json_response(status=200)
        return r

    def run_http_server(self):
        bottle.run(host=self.config['http']['bind'],
            port=int(self.config['http']['port']), server='eventlet')

    def run(self):
        self.run_http_server()
