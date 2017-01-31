import random

from zipkin.zipkin_data import ZipkinId


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
        return self.generate_id()

    def generate_span_id(self):
        return self.generate_id()


default = SimpleIdGenerator()
