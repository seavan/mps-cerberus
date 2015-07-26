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

__version__ = "0.2.5"
__author__ = "Eduard Snesarev"

default_config = {
  'http': {
    'bind': '127.0.0.1',
    'port': '8080'
  },

  'celery': {
    'CELERY_RESULT_BACKEND': 'redis://localhost',
    'BROKER_URL': 'redis://localhost/0'
  },

  'tasks': {
    'transcode_av': {
      'keep_data': False,
      'ffmpeg_command_template': '/usr/bin/ffmpeg -y -loop 1 -i {input_picture} -i {input_audio} -shortest -vcodec libx264 -acodec aac -strict experimental {output_video}',
      'storage': {
        'type': 'webdav',
        'url': 'http://127.0.0.1:80'
      },
      'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'queue_name': 'transcode_av:result'
      }
    },
    'transcode_a': {
      'keep_data': False,
      'ffmpeg_command_template': '/usr/bin/ffmpeg -i {input_audio} -f mp2 {output_audio}',
      'storage': {
        'type': 'webdav',
        'url': 'http://127.0.0.1:80'
      },
      'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'queue_name': 'transcode_a:result'
      }
    },
    'upload': {
      'storage': {
        'type': 'webdav',
        'url': 'http://127.0.0.1:80'
      },
      'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'queue_name': 'upload:result'
      }

    },
    'delete': {
      'storage': {
        'type': 'webdav',
        'url': 'http://127.0.0.1:80'
      },
      'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'queue_name': 'delete:result'
      }

    },
    'parse_metadata': {
      'keep_data': False,
      'storage': {
        'type': 'webdav',
        'url': 'http://127.0.0.1:80'
      },
      'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 1,
        'queue_name': 'parse_metadata:result'
      }
    }
  },

  'services': {
    'youtube': {
      'login': None,
      'password': None,
      'developer_key': None,
      'source': None
    }
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
    app = Celery('cerberus.celery')
    app.conf.update(**config['celery'])

    try:
        o = Cerberus(config, app)
        o.run()
    except KeyboardInterrupt:
        sys.exit(1)
