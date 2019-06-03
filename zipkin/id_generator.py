import random

from .zipkin_data import ZipkinId, ZipkinTraceId


class BaseIdGenerator(object):
    def generate_trace_id(self):
        raise NotImplementedError

    def generate_span_id(self):
        raise NotImplementedError


class SimpleIdGenerator(BaseIdGenerator):
    @staticmethod
    def generate_id():
        return ZipkinId.from_binary(random.randrange(ZipkinId.MIN_VAL, ZipkinId.MAX_VAL))

    def generate_trace_id(self):
        low = random.randrange(ZipkinTraceId.MIN_VAL, ZipkinTraceId.MAX_VAL)
        high = random.randrange(ZipkinTraceId.MIN_VAL, ZipkinTraceId.MAX_VAL)
        return ZipkinTraceId.from_binary(low=low, high=high)

    def generate_span_id(self):
        return self.generate_id()


default = SimpleIdGenerator()
