# encoding: utf-8

from os.path import join

import requests

DEFAULT_CONFIG = {
  'type': 'webdav',
  'url': 'http://127.0.0.1:80'
}

class WebDavStorage(object):
    def __init__(self, url=None):
        self.url = url

    def download(self, src):
        r = requests.get(join(self.url, src))
        return r.content

    def download_to(self, src, dst):
        content = self.download(src)

        # TODO: написать потоковое сохранение данных на диск
        with open(dst, 'w') as f:
            f.write(content)

    def upload(self, src, dst):
        requests.put(join(self.url, dst), data=file(src))
