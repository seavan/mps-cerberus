# encoding: utf-8

from .youtube import YouTube

from cerberus.exceptions import UnknownService

__all__ = ['YouTube', 'create_service']

def create_service(name, config, storage):

    if name == 'youtube':
        service = YouTube(config['youtube'], storage)
    else:
        raise UnknownService("unknown service `{0}`".format(name))

    return service
