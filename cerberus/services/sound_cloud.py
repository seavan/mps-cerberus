# encoding: utf-8

import soundcloud

from cerberus.exceptions import *
from .interface import BaseService

class SoundCloud(BaseService):
    def __init__(self, config):
        self.config = config
        self.c = soundcloud.Client(client_id=self.config['client_id'],
                           client_secret=self.config['client_secret'],
                           username=self.config['username'],
                           password=self.config['password'])

    def upload(self, filename=None, title=None):
        try:
            resource = self.c.post('/tracks', track={
                    'title': title,
                    'asset_data': open(filename, 'rb')
                })

            track = resource.obj
            return {'track_id': track['id']}
        except Exception as e:
            reraise(ServiceUploadError)

    def delete(self, track_id=None):
        try:
            self.c.delete('/tracks/{0}'.format(track_id))
        except Exception as e:
            reraise(ServiceDeleteError)
