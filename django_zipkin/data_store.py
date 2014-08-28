import threading

from utils import import_class
import defaults as settings
from zipkin_data import ZipkinData
from _thrift.zipkinCore.ttypes import Annotation, BinaryAnnotation


class BaseDataStore(object):
    def set(self, data):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def _record_annotation(self, annotation):
        raise NotImplementedError

    def _record_binary_annotation(self, annotation):
        raise NotImplementedError

    def record(self, annotation):
        if not self.get().sampled:
            return
        if isinstance(annotation, Annotation):
            self._record_annotation(annotation)
        elif isinstance(annotation, BinaryAnnotation):
            self._record_binary_annotation(annotation)
        else:
            raise ValueError("Argument to %s.record must be an instance of Annotation or BinaryAnnotation" % self.__class__.__name__)

    def set_rpc_name(self, name):
        raise NotImplementedError

    def get_rpc_name(self):
        raise NotImplementedError

    def get_annotations(self):
        raise NotImplementedError

    def get_binary_annotations(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class ThreadLocalDataStore(BaseDataStore):
    thread_local_data = threading.local()

    def get(self):
        return self.thread_local_data.zipkin_data

    def set(self, data):
        self.thread_local_data.zipkin_data = data

    def _record_annotation(self, annotation):
        self.thread_local_data.annotations.append(annotation)

    def _record_binary_annotation(self, annotation):
        self.thread_local_data.binary_annotations.append(annotation)

    def get_annotations(self):
        return self.thread_local_data.annotations

    def get_binary_annotations(self):
        return self.thread_local_data.binary_annotations

    def set_rpc_name(self, name):
        self.thread_local_data.rpc_name = name

    def get_rpc_name(self):
        return self.thread_local_data.rpc_name

    @classmethod
    def clear(cls):
        cls.thread_local_data.zipkin_data = ZipkinData()
        cls.thread_local_data.annotations = []
        cls.thread_local_data.binary_annotations = []
        cls.thread_local_data.rpc_name = None
ThreadLocalDataStore.clear()


default = import_class(settings.ZIPKIN_DATA_STORE_CLASS)()
