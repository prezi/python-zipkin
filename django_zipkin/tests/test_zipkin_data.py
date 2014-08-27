from unittest2.case import TestCase
from django_zipkin.zipkin_data import ZipkinId


__all__ = ['ZipkinIdTestCase']


class ZipkinIdTestCase(TestCase):
    def test_raises_excepion_if_value_is_too_big(self):
        with self.assertRaises(ValueError):
            ZipkinId(2 ** 63)
        with self.assertRaises(ValueError):
            ZipkinId(-(2 ** 63))

    def test_getters(self):
        val = 42
        zid = ZipkinId(val)
        self.assertEqual(zid.get_binary(), val)
        self.assertEqual(zid.get_hex(), '000000000000002a')

    def test_from_binary(self):
        val = 2 * 63 - 1
        self.assertEqual(ZipkinId.from_binary(val).get_binary(), val)

    def test_from_hex(self):
        hex = 'ffffffffffffffff'
        zid = ZipkinId.from_hex(hex)
        self.assertEqual(zid.get_binary(), -1)
        self.assertEqual(zid.get_hex(), hex)

    def test_None_input(self):
        self.assertIsNone(ZipkinId.from_hex(None))
        self.assertIsNone(ZipkinId.from_binary(None))
