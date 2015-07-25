# encoding: utf-8

import tempfile

import gdata.youtube
import gdata.youtube.service

from .interface import BaseService

class YouTube(BaseService):
    def __init__(self, config, storage=None):
        self.config = config

        self.y = gdata.youtube.service.YouTubeService()

        self.y.email = self.config['email']
        self.y.password = self.config['password']
        self.y.source = self.config['source']
        self.y.ProgrammaticLogin()

        self.storage = storage

    def upload(self, filename="", title="", category="", keywords=[]):
        media_group = gdata.media.Group(
            description=gdata.media.Description(description_type='plain',
                text=title),
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

        # TODO: Сделать потоковое сохранение файла на диск
        content = self.storage.download(filename)
        video_file_location = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        video_file_location.write(content)

        self.y.InsertVideoEntry(video_entry, video_file_location.name)

    def delete(self, video_id):
        self.y.DeleteVideoEntry(video_id)
