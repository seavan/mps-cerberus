# encoding: utf-8

from os.path import join

import requests
from requests.exceptions import *

from cerberus.exceptions import *
from .interface import BaseStorage

class WebDavStorage(BaseStorage):
    def __init__(self, url=None):
        self.url = url

    def download(self, src):
        src = src[1:] if src.startswith('/') else src
        try:
            r = requests.get(join(self.url, src))
        except ConnectionError as e:
            reraise(StorageDownloadError)

        return r.content

    def download_to(self, src, dst):
        try:
            content = self.download(src)

            # TODO: написать потоковое сохранение данных на диск
            with open(dst, 'w') as f:
                f.write(content)
        except Exception as e:
            reraise(StorageDownloadError)

    def upload(self, src, dst):
        dst = dst[1:] if dst.startswith('/') else dst
        try:
            requests.put(join(self.url, dst), data=file(src))
        except Exception as e:
            reraise(StorageDownloadError)
