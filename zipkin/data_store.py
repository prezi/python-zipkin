import threading
import functools

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
        if not self.get().is_tracing():
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


def _clear_and_retry_on_attribute_error(method):
    @functools.wraps(method)
    def f(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except AttributeError:
            self.clear()
            return method(self, *args, **kwargs)
    return f


class ThreadLocalDataStore(BaseDataStore):
    thread_local_data = threading.local()

    @_clear_and_retry_on_attribute_error
    def get(self):
        return self.thread_local_data.zipkin_data

    @_clear_and_retry_on_attribute_error
    def set(self, data):
        self.thread_local_data.zipkin_data = data

    @_clear_and_retry_on_attribute_error
    def _record_annotation(self, annotation):
        self.thread_local_data.annotations.append(annotation)

    @_clear_and_retry_on_attribute_error
    def _record_binary_annotation(self, annotation):
        self.thread_local_data.binary_annotations.append(annotation)

    @_clear_and_retry_on_attribute_error
    def get_annotations(self):
        return self.thread_local_data.annotations

    @_clear_and_retry_on_attribute_error
    def get_binary_annotations(self):
        return self.thread_local_data.binary_annotations

    @_clear_and_retry_on_attribute_error
    def set_rpc_name(self, name):
        self.thread_local_data.rpc_name = name

    @_clear_and_retry_on_attribute_error
    def get_rpc_name(self):
        return self.thread_local_data.rpc_name

    @classmethod
    def clear(cls):
        cls.thread_local_data = threading.local()
        cls.thread_local_data.zipkin_data = ZipkinData()
        cls.thread_local_data.annotations = []
        cls.thread_local_data.binary_annotations = []
        cls.thread_local_data.rpc_name = None


default = ThreadLocalDataStore()
