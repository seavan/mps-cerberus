# encoding: utf-8

from .youtube import YouTube
from .sound_cloud import SoundCloud

from cerberus.exceptions import UnknownService

__all__ = ['create_service', 'YouTube', 'SoundCloud']

def create_service(name, config):

    if name == 'youtube':
        service = YouTube(config['youtube'])
    elif name == 'soundcloud':
        service = SoundCloud(config['soundcloud'])
    else:
        raise UnknownService("unknown service `{0}`".format(name))

    return service
