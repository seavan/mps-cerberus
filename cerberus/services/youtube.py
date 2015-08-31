# encoding: utf-8

import os

import gdata.youtube
import gdata.youtube.service

from cerberus.exceptions import *
from .interface import BaseService

class YouTube(BaseService):
    def __init__(self, config):
        self.config = config

        self.y = gdata.youtube.service.YouTubeService()

        self.y.email = self.config['email']
        self.y.password = self.config['password']
        self.y.source = self.config['source']
        self.y.ProgrammaticLogin()
        self.y.developer_key = self.config['developer_key']

    def upload(self, *args, **kwargs):
        try:
            self._upload(*args, **kwargs)
        except Exception as e:
            _raise(ServiceUploadError)

    def _upload(self, filename="", title="", description="" ,category="", keywords=[]):
        media_group = gdata.media.Group(
          title=gdata.media.Title(text=title),
          description=gdata.media.Description(description_type='plain', text=description),
          keywords=gdata.media.Keywords(text=", ".join(keywords)),
          category=[gdata.media.Category(
              text=category,
              scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
              label=category)],
          player=None
        )

        # TODO: Добавить гео-локацию
        # where = gdata.geo.Where()
        # where.set_location(())

        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group)
        uploaded_video_entry = self.y.InsertVideoEntry(video_entry, filename)

        # XXX: По-моему это не лучший способ добыть video_id
        return {'video_id': os.path.basename(uploaded_video_entry.id.text)}

    def delete(self, video_id):
        try:
            self.y.DeleteVideoEntry(video_id)
        except Exception as e:
            _raise(ServiceDeleteError)
