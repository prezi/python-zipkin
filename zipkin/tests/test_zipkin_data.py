from unittest2.case import TestCase
from zipkin.zipkin_data import ZipkinId, ZipkinTraceId


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
        self.assertEqual(zid.get_hex(), b'000000000000002a')

    def test_from_binary(self):
        val = 2 * 63 - 1
        self.assertEqual(ZipkinId.from_binary(val).get_binary(), val)

    def test_from_hex(self):
        cases = [
            ('ffffffffffffffff', -1),
            ('c564d8606f4400', 55561450905617408),
            ('aa', 170)
        ]
        for hex, expected_binary in cases:
            zid = ZipkinId.from_hex(hex)
            self.assertEqual(zid.get_binary(), expected_binary, hex)
            self.assertEqual(zid.get_hex(), hex.zfill(16).encode())

    def test_None_input(self):
        self.assertIsNone(ZipkinId.from_hex(None))
        self.assertIsNone(ZipkinId.from_binary(None))


class ZipkinTraceIdTestCase(TestCase):
    def test_raises_excepion_if_value_is_too_big(self):
        with self.assertRaises(ValueError):
            ZipkinTraceId(2 ** 63, 2)
        with self.assertRaises(ValueError):
            ZipkinTraceId(2, 2 ** 63)
        with self.assertRaises(ValueError):
            ZipkinTraceId(2, -(2 ** 63))
        with self.assertRaises(ValueError):
            ZipkinTraceId(-(2 ** 63), 2)

    def test_getters(self):
        low, high = 42, 24
        zid = ZipkinTraceId(low=low, high=high)
        self.assertEqual(zid.get_binary_low_bytes(), low)
        self.assertEqual(zid.get_binary_high_bytes(), high)
        self.assertEqual(zid.get_hex(), b'0000000000000018000000000000002a')

    def test_from_hex(self):
        cases = [
            ('ffffffffffffffffffffffffffffffff', (-1, -1)),
            ('c564d8606f4400', (0, 55561450905617408)),
            ('aa', (0, 170)),
            ('0000000000000018000000000000002a', (24, 42))
        ]
        for hex, (expected_high, expected_low) in cases:
            zid = ZipkinTraceId.from_hex(hex)
            self.assertEqual(zid.get_binary_high_bytes(), expected_high, hex)
            self.assertEqual(zid.get_binary_low_bytes(), expected_low, hex)
            self.assertEqual(zid.get_hex(), hex.zfill(32).encode())

    def test_None_input(self):
        self.assertIsNone(ZipkinTraceId.from_hex(None))
        self.assertIsNone(ZipkinTraceId.from_binary(None, 123))
        self.assertIsNone(ZipkinTraceId.from_binary(123, None))
