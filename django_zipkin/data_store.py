import threading
from django_zipkin.zipkin_data import ZipkinData


class BaseDataStore(object):
    def set(self, data):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError


class ThreadLocalDataStore(BaseDataStore):
    def __init__(self):
        self.thread_local_data = threading.local()

    def get(self):
        try:
            return self.thread_local_data.zipkin_data
        except AttributeError:
            return ZipkinData()

    def set(self, data):
        self.thread_local_data.zipkin_data = data


default = ThreadLocalDataStore()  # TODO make the default class configurable
