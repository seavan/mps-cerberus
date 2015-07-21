# encoding: utf-8

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import yaml

from celery import Celery

from cerberus.utils import merge

try:
    config_path = os.environ['CERBERUS_WORKER_CONFIG_PATH']
except KeyError:
    print("error: set up CERBERUS_WORKER_CONFIG_PATH environment variable")
    sys.exit(1)

default_config = {
  'celery': {
    'CELERY_RESULT_BACKEND': 'redis://localhost',
    'BROKER_URL': 'redis://localhost/0'
  }
}

try:
    config = yaml.load(file(config_path, 'r'))
except (OSError, IOError) as e:
    print("error: couldn't open config `{0}`".format(config_path))
    sys.exit(1)
except yaml.YAMLError:
    print("error: couldn't parse config `{0}`".format(config_path))
    sys.exit(1)

config = merge(default_config, config)

app = Celery('cerberus.celery')
app.conf.update(**config['celery'])

if __name__ == '__main__':
    app.start()
