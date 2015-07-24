# encoding: utf-8

from .webdav import WebDavStorage

from cerberus.exceptions import UnknownStorage

__all__ = ['WebDavStorage', 'create_storage']

def create_storage(config):

    if config['type'] == 'webdav':
        storage = WebDavStorage(url=config['url'])
    else:
        raise UnknownStorage(config['type'])

    return storage
