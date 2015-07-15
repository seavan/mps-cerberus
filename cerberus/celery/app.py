from __future__ import absolute_import

from celery import Celery

app = Celery('cerberus.celery', broker='redis://localhost/0', backend='redis://localhost')

if __name__ == '__main__':
    app.start()
