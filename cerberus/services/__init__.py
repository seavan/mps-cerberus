# encoding: utf-8

from .youtube import YouTube

from cerberus.exceptions import UnknownService

__all__ = ['create_service', 'YouTube']

def create_service(name, config):

    if name == 'youtube':
        service = YouTube(config['youtube'])
    else:
        raise UnknownService("unknown service `{0}`".format(name))

    return service
