# encoding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import sys
import yaml

from optparse import OptionParser

from celery import Celery

from .utils import *
from .cerberus  import Cerberus

__all__ = ('run_script', 'celery')

__version__ = "0.1.0"
__author__ = "Eduard Snesarev"

default_config = {
  'http': {
    'bind': '127.0.0.1',
    'port': '8080'
  },

  'celery': {
  }
}

def run_script():
    p = OptionParser()
    p.add_option('-c', '--config', dest="config_path", help="path to config.yml")
    (opt, args) = p.parse_args()

    if opt.config_path:
        try:
            config = yaml.load(file(opt.config_path))
        except (OSError, IOError):
            print("error: could not open config `{0}`".format(opt.config_path))
            sys.exit(1)
        except yaml.YAMLError:
            print("error: could not parse config `{0}`".format(opt.config_path))
            sys.exit(1)
    else:
        print("error: missing required argument '-c|--config', see {0} -h".format(sys.argv[0]))
        sys.exit(1)

    config = merge(default_config, config)
    app = Celery('cerberus.celery', broker='redis://localhost/0', backend='redis://localhost')

    try:
        o = Cerberus(config, app)
        o.run()
    except KeyboardInterrupt:
        sys.exit(1)
