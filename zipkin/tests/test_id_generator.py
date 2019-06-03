from unittest2.case import TestCase

from zipkin.zipkin_data import ZipkinId, ZipkinTraceId
from zipkin.id_generator import SimpleIdGenerator


__all__ = ['SimpleIdGeneratorTestCase']


class SimpleIdGeneratorTestCase(TestCase):
    def setUp(self):
        self.generator = SimpleIdGenerator()

    def test_trivial(self):
        span_id = self.generator.generate_span_id()
        trace_id = self.generator.generate_trace_id()
        self.assertIsInstance(span_id, ZipkinId)
        self.assertIsInstance(trace_id, ZipkinTraceId)
        self.assertNotEqual(span_id.get_binary(),
                            trace_id.get_binary_low_bytes())
        self.assertNotEqual(span_id.get_binary(),
                            trace_id.get_binary_high_bytes())
