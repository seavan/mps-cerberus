# encoding: utf-8

class BaseStorage(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")

    def upload(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")

    def download(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")

    def download_to(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")
