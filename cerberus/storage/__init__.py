# encoding: utf-8

from cerberus.utils import merge

from .webdav import WebDavStorage
from .webdav import DEFAULT_CONFIG as webdav_default_config

__all__ = ['WebDavStorage', 'create_storage']

class UnknownStorage(Exception):
    pass

def create_storage(storage_config):

    storage_config['type'] == 'webdav':
        config = merge(webdav_default_config, storage_config)
        storage = WebDavStorage(url=config['url'])
    else:
        raise UnknownStorage(storage_config['type'])
