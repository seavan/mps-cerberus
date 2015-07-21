# encoding: utf-8

from .webdav import WebDavStorage

__all__ = ['WebDavStorage', 'create_storage']

class UnknownStorage(Exception):
    pass

def create_storage(config):

    config['type'] == 'webdav':
        storage = WebDavStorage(url=config['url'])
    else:
        raise UnknownStorage(config['type'])
