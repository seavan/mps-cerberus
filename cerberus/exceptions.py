# encoding: utf-8

import sys

def _raise(exc):
    trace = sys.exc_info()[2]
    raise exc, None, trace

class UnknownStorage(Exception):
    pass

class StorageDownloadError(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 601
        self.message = 'Storage download error'

        super(Exception, self).__init__(*args, **kwargs)

class StorageUploadError(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 602
        self.message = 'Storage upload error'

        super(Exception, self).__init__(*args, **kwargs)


class UnknownService(Exception):
    pass

class ServiceUploadError(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 701
        self.message = 'Service upload error'

        super(ServiceUploadError, self).__init__(*args, **kwargs)

class ServiceDeleteError(Exception):
    def __init__(self, *args, **kwargs):
        self.code = 702
        self.message = 'Service delete error'

        super(ServiceDeleteError, self).__init__(*args, **kwargs)
