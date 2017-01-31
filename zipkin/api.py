import struct
import socket
import time

from zipkin.data_store import default as default_store
from zipkin._thrift.zipkinCore.ttypes import Annotation, BinaryAnnotation, Endpoint, AnnotationType, Span


class ZipkinApi(object):
    def __init__(self, service_name=None, store=None, writer=None):
        self.store = store or default_store
        self.endpoint = Endpoint(
            ipv4=self._get_my_ip(),
            port=None,
            service_name=service_name
        )
        self.writer = writer

    def record_event(self, message):
        self.store.record(self._build_annotation(message))

    def record_key_value(self, key, value):
        self.store.record(self._build_binary_annotation(key, value))

    def set_rpc_name(self, name):
        self.store.set_rpc_name(name)

    def submit_span(self, timestamp_in_microseconds, duration_in_microseconds):
        self.writer.write(self._build_span(timestamp_in_microseconds, duration_in_microseconds))
        self.store.clear()

    def _get_my_ip(self):
        try:
            return self._ipv4_to_long(socket.gethostbyname(socket.gethostname()))
        except Exception:
            return None

    def _build_span(self, timestamp_in_microseconds, duration_in_microseconds):
        zipkin_data = self.store.get()
        return Span(
            id=zipkin_data.span_id.get_binary(),
            trace_id=zipkin_data.trace_id.get_binary(),
            parent_id=zipkin_data.parent_span_id.get_binary() if zipkin_data.parent_span_id is not None else None,
            name=self.store.get_rpc_name(),
            annotations=self.store.get_annotations(),
            binary_annotations=self.store.get_binary_annotations(),
            timestamp=timestamp_in_microseconds,
            duration=duration_in_microseconds
        )

    def _build_annotation(self, value):
        # if isinstance(value, unicode):
            # value = value.encode('utf-8')
        if not isinstance(value, bytes):
            value = value.encode('utf-8')
        return Annotation(time.time() * 1000 * 1000, value, self.endpoint)

    def _build_binary_annotation(self, key, value):
        annotation_type = self._binary_annotation_type(value)
        formatted_value = self._format_binary_annotation_value(value, annotation_type)
        return BinaryAnnotation(key, formatted_value, annotation_type, self.endpoint)

    @classmethod
    def _binary_annotation_type(cls, value):
        # if isinstance(value, str) or isinstance(value, unicode)
        if isinstance(value, str):
            return AnnotationType.STRING
        if isinstance(value, float):
            return AnnotationType.DOUBLE
        if isinstance(value, bool):
            return AnnotationType.BOOL
        if isinstance(value, int) or isinstance(value, long):
            # TODO: make this more granular to preserve network bytes
            return AnnotationType.I64

    @classmethod
    def _format_binary_annotation_value(cls, value, type):
        number_formats = {
            AnnotationType.I16: 'h',
            AnnotationType.I32: 'i',
            AnnotationType.I64: 'q',
            AnnotationType.DOUBLE: 'd'
        }
        if type == AnnotationType.STRING:
            # if isinstance(value, unicode):
                # return value.encode('utf-8')
            # return str(value)
            if isinstance(value, bytes):
                return value
            return value.encode('utf-8')

        if type == AnnotationType.BOOL:
            if value:
                return '1'
            else:
                return '0'
        if type in number_formats:
            return struct.pack('!' + number_formats[type], value)
        return 'zipkin_cat failed to serialize type %s value %s' % (type, value)

    @staticmethod
    def _ipv4_to_long(ip):
        packed_ip = socket.inet_aton(ip)
        return struct.unpack("!i", packed_ip)[0]


api = ZipkinApi(store=default_store)
