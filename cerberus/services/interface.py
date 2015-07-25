# encoding: utf-8

class BaseService(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")

    def upload(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Should have implemented this")
