# encoding: utf-8

import tempfile

import gdata.youtube
import gdata.youtube.service

class YouTube(object):
    def __init__(self, config, storage):
        self.config = config

        self.y = youtube.service.YouTubeService()

        self.y.email = self.config['email']
        self.y.password = self.config['password']
        self.y.source = self.config['source']
        self.y.ProgrammaticLogin()

        self.storage = storage

    def upload(self, title, filename):
        media_group = gdata.media.Group(
            description=gdata.media.Description(description_type='plain',
                text=title),
            keywords=gdata.media.Keywords(),
            category=[[]gdata.media.Category(
                text='Music',
                scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                label='Music')],
            player=None
        )

        # TODO: Добавить гео-локацию
        # where = gdata.geo.Where()
        # where.set_location(())

        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group,
            geo=where)

        # TODO: Сделать потоковое сохранение файла на диск
        content = self.storage.download(filename)
        video_file_location = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        video_file_location.write(content)

        self.y.InsertVideoEntry(video_entry, video_file_location.name)

    def delete(self):
        pass
