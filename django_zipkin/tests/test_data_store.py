from unittest2.case import TestCase
from mock import patch, Mock

from django_zipkin.data_store import ThreadLocalDataStore
from django_zipkin.zipkin_data import ZipkinData

from helpers import DjangoZipkinTestHelpers


__all__ = ['ThreadLocalDataStoreTestCase']


class ThreadLocalDataStoreTestCase(DjangoZipkinTestHelpers, TestCase):
    def setUp(self):
        self.threading_local_patcher = patch('django_zipkin.data_store.threading.local')
        self.mock_threading_local = self.threading_local_patcher.start()

    def tearDown(self):
        self.threading_local_patcher.stop()

    def test_get_returns_what_is_in_threadlocal_storage(self):
        self.assertEqual(self.mock_threading_local.return_value.zipkin_data, ThreadLocalDataStore().get())

    def test_get_without_set_returns_empty_zipkin_data(self):
        self.mock_threading_local.return_value = object()
        self.assertZipkinDataEquals(ZipkinData(), ThreadLocalDataStore().get())

    def test_set_writes_to_threadlocal_storage(self):
        data = Mock()
        ThreadLocalDataStore().set(data)
        self.assertEqual(self.mock_threading_local.return_value.zipkin_data, data)
