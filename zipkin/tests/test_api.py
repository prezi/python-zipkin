from unittest2 import TestCase, skip
from mock import patch, Mock, sentinel

from zipkin._thrift.zipkinCore.ttypes import AnnotationType
from zipkin.api import ZipkinApi
from zipkin.data_store import BaseDataStore
from zipkin.id_generator import SimpleIdGenerator
from zipkin.zipkin_data import ZipkinData, ZipkinId


__all__ = ['ZipkinApiTestCase']


class ZipkinApiTestCase(TestCase):
    def setUp(self):
        self.time_patcher = patch('zipkin.api.time')
        self.mock_time = self.time_patcher.start()
        self.store = Mock(spec=BaseDataStore)
        self.api = ZipkinApi(store=self.store)

    def tearDown(self):
        self.time_patcher.stop()

    def test_ipv4_to_long(self):
        self.assertEqual(self.api._ipv4_to_long('127.0.0.1'), 2130706433)

    def test_build_annotation(self):
        value = Mock()
        annotation = self.api._build_annotation(value)
        self.assertEqual(annotation.timestamp, self.mock_time.time.return_value * 1000 * 1000)
        self.assertEqual(annotation.value, value.encode('utf-8'))
        self.assertEqual(annotation.host, self.api.endpoint)

    def test_record_event(self):
        with patch.object(self.api, '_build_annotation') as mock_build_annotation:
            value = Mock()
            self.api.record_event(value)
            mock_build_annotation.assert_called_once_with(value)
            self.store.record.assert_called_once_with(mock_build_annotation.return_value)

    def test_binary_annotation_type(self):
        cases = {
            'foo': AnnotationType.STRING,
            True: AnnotationType.BOOL,
            False: AnnotationType.BOOL,
            5: AnnotationType.I64,      # TODO: make type detection more granular
            2**9: AnnotationType.I64,   # TODO: make type detection more granular
            2**17: AnnotationType.I64,  # TODO: make type detection more granular
            2**33: AnnotationType.I64,  # TODO: make type detection more granular
            3.14: AnnotationType.DOUBLE
        }
        for value, expected_type in cases.items():
            self.assertEqual(self.api._binary_annotation_type(value), expected_type, value)

    def test_format_binary_annotation_value(self):
        cases = {
            AnnotationType.STRING: [(b'foo', b'foo'), (u'foo', b'foo')],
            # TODO: add cases for smaller ints when type detection is made more granular
            AnnotationType.BOOL: [(True, '1'), (False, '0')],
            AnnotationType.I64: [(-42, b'\xff\xff\xff\xff\xff\xff\xff\xd6'), (42, b'\x00\x00\x00\x00\x00\x00\x00*')],
            AnnotationType.DOUBLE: [(3.14, b'@\t\x1e\xb8Q\xeb\x85\x1f')]
        }
        for type, pairs in cases.items():
            for input, expected in pairs:
                self.assertEqual(self.api._format_binary_annotation_value(input, type), expected, input)

    def test_build_binary_annotation(self):
        annotation = self.api._build_binary_annotation('awesome', True)
        self.assertEqual(annotation.key, 'awesome')
        self.assertEqual(annotation.value, '1')
        self.assertEqual(annotation.annotation_type, AnnotationType.BOOL)
        self.assertEqual(annotation.host, self.api.endpoint)

    def test_record_key_value(self):
        with patch.object(self.api, '_build_binary_annotation') as mock_build_binary_annotation:
            key, value = Mock(), Mock()
            self.api.record_key_value(key, value)
            mock_build_binary_annotation.assert_called_once_with(key, value)
            self.store.record.assert_called_once_with(mock_build_binary_annotation.return_value)

    def test_set_rpc_name(self):
        self.api.set_rpc_name(sentinel.rpc_name)
        self.store.set_rpc_name.assert_called_once_with(sentinel.rpc_name)

    def test_build_span(self):
        timestamp, duration = Mock(), Mock()
        binary_annotations = [self.api._build_binary_annotation('awesome', True)]
        annotations = [
            self.api._build_annotation('sr'),
            self.api._build_annotation('ss'),
        ]
        self.store.get_annotations.return_value = annotations
        self.store.get_binary_annotations.return_value = binary_annotations
        span = self.api._build_span(timestamp, duration)
        self.assertEqual(span.id, self.store.get.return_value.span_id.get_binary.return_value)
        self.assertEqual(span.trace_id, self.store.get.return_value.trace_id.get_binary.return_value)
        self.assertEqual(span.parent_id, self.store.get.return_value.parent_span_id.get_binary.return_value)
        self.assertEqual(span.name, self.store.get_rpc_name.return_value)
        self.assertEqual(span.annotations, annotations)
        self.assertEqual(span.binary_annotations, binary_annotations)
        self.assertEqual(span.timestamp, timestamp)
        self.assertEqual(span.duration, duration)

    def test_nonascii_input(self):
        timestamp, duration = Mock(), Mock()
        uri_in = u'\ufffd\ufffd/\x01'
        uri_out = uri_in.encode('utf-8')
        self.store.get.return_value = ZipkinData(
            trace_id=ZipkinId(42),
            span_id=ZipkinId(4242),
            parent_span_id=ZipkinId(1773),
            sampled=True
        )
        self.store.get_binary_annotations.return_value = [self.api._build_binary_annotation('http.uri', uri_in)]
        self.store.get_annotations.return_value = [self.api._build_annotation(uri_in)]
        self.store.get_rpc_name.return_value = 'test-rpc-name'
        self.assertEqual(self.api._build_span(timestamp, duration).annotations[0].value, uri_out)
        self.assertEqual(self.api._build_span(timestamp, duration).binary_annotations[0].value, uri_out)

    @skip("To be migrated into test for ScribeWriter")
    def test_integration(self):
        self.api.endpoint.ipv4 = 2130706433
        binary_annotations = [self.api._build_binary_annotation('awesome', True)]
        annotations = [
            self.api._build_annotation('sr'),
            self.api._build_annotation('ss'),
        ]
        self.store.get_annotations.return_value = annotations
        self.store.get_binary_annotations.return_value = binary_annotations
        self.store.get.return_value = ZipkinData(
            trace_id=ZipkinId(42),
            span_id=ZipkinId(4242),
            parent_span_id=ZipkinId(1773),
            sampled=True
        )
        self.store.get_rpc_name.return_value = 'test-name'
        self.mock_time.time.return_value = 1024
        self.assertEqual(self.api.build_log_message(), self.api.build_log_message())
        self.assertEqual(
            self.api.build_log_message(),
            '''CgABAAAAAAAAACoLAAMAAAAJdGVzdC1uYW1lCgAEAAAAAAAAEJIKAAUAAAAAAAAG7Q8AB'''
            '''gwAAAACCgABAAAAAAAAAAELAAIAAAACc3IMAAMIAAF/AAABAAAKAAEAAAAAAAAAAQsAAgAAAAJzcwwAAwgAAX8AAAEAAA8ACAwAAAABCwABAAAAB'''
            '''2F3ZXNvbWULAAIAAAABMQgAAwAAAAAMAAQIAAF/AAABAAACAAkAAA==''')
