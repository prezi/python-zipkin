from unittest2.case import TestCase
from mock import patch, Mock, sentinel

from zipkin.data_store import BaseDataStore, ThreadLocalDataStore
from zipkin.zipkin_data import ZipkinData
from zipkin._thrift.zipkinCore.ttypes import Annotation, BinaryAnnotation

from zipkin.tests.helpers import ZipkinTestHelpers


__all__ = ['BaseDataStoreTestCase', 'ThreadLocalDataStoreTestCase']


class BaseDataStoreTestCase(TestCase):
    def setUp(self):
        self.store = BaseDataStore()
        self.store._record_annotation = Mock()
        self.store._record_binary_annotation = Mock()

    def test_record_noop_if_not_sampled(self):
        self.store.get = lambda: ZipkinData(sampled=False)
        self.store._record_annotation = Mock()
        self.store._record_binary_annotation = Mock()
        self.store.record(Mock())
        self.assertFalse(self.store._record_annotation.called)
        self.assertFalse(self.store._record_binary_annotation.called)

    def test_record_delegates_if_sampled(self):
        self.store.get = lambda: ZipkinData(sampled=True)
        annotation = Mock(spec=Annotation)
        binary_annotation = Mock(spec=BinaryAnnotation)
        self.store.record(annotation)
        self.store.record(binary_annotation)
        self.store._record_annotation.assert_called_once_with(annotation)
        self.store._record_binary_annotation.assert_called_once_with(binary_annotation)


class ThreadLocalDataStoreTestCase(ZipkinTestHelpers, TestCase):
    def setUp(self):
        self.local_patcher = patch('zipkin.data_store.ThreadLocalDataStore.thread_local_data')
        self.mock_local = self.local_patcher.start()

    def tearDown(self):
        self.local_patcher.stop()

    def test_get_without_set_returns_empty_zipkin_data(self):
        store = ThreadLocalDataStore()
        store.clear()
        self.assertZipkinDataEquals(ZipkinData(), store.get())

    def test_get_returns_what_was_set(self):
        store = ThreadLocalDataStore()
        data = Mock()
        store.set(data)
        self.assertEqual(data, store.get())

    def test_set_writes_to_threadlocal_storage(self):
        data = Mock()
        ThreadLocalDataStore().set(data)
        self.assertEqual(self.mock_local.zipkin_data, data)

    def test_annotations(self):
        annotations = [Mock(spec=Annotation), Mock(spec=Annotation)]
        binary_annotations = [Mock(spec=BinaryAnnotation), Mock(spec=BinaryAnnotation)]
        store = ThreadLocalDataStore()
        store.clear()
        store.set(ZipkinData(sampled=True))
        for annotation in annotations + binary_annotations:
            store.record(annotation)
        self.assertListEqual(annotations, store.get_annotations())
        self.assertListEqual(binary_annotations, store.get_binary_annotations())

    def test_rpc_name(self):
        store = ThreadLocalDataStore()
        store.clear()
        self.assertIsNone(store.get_rpc_name())
        store.set_rpc_name(sentinel.rpc_name)
        self.assertEqual(store.get_rpc_name(), sentinel.rpc_name)

    def test_clear(self):
        annotations = [Mock(spec=Annotation), Mock(spec=Annotation)]
        binary_annotations = [Mock(spec=BinaryAnnotation), Mock(spec=BinaryAnnotation)]
        store = ThreadLocalDataStore()
        store.set(ZipkinData(sampled=True, trace_id=Mock()))
        store.set_rpc_name(Mock())
        for annotation in annotations + binary_annotations:
            store.record(annotation)
        store.clear()
        self.assertListEqual([], store.get_annotations())
        self.assertListEqual([], store.get_binary_annotations())
        self.assertZipkinDataEquals(ZipkinData(), store.get())
        self.assertIsNone(store.get_rpc_name())

    def test_dont_freak_out_if_thread_local_store_is_gone(self):
        store = ThreadLocalDataStore()
        ThreadLocalDataStore.thread_local_data = object()
        self.assertIsNone(store.get_rpc_name())
        self.assertZipkinDataEquals(ZipkinData(), store.get())
