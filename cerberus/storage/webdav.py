# encoding: utf-8

from os.path import join

import requests

class WebDavStorage(object):
    def __init__(self, url=None):
        self.url = url

    def download(self, filename):
        r = requests.get(join(self.url, src))
        return r.body
