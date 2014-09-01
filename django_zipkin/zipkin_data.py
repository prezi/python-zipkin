import struct
import binascii


class ZipkinId(object):
    """
    Thrift uses a binary representation of trace and span ids
    HTTP headers use a hexadecimal representation of the same
    This class encapsulates converting between the two

    The number is a signed 64-bit integer.
    """
    MAX_VAL = 2 ** 63 - 1
    MIN_VAL = -MAX_VAL

    STRUCT = struct.Struct('!q')

    def __init__(self, n):
        if n < self.MIN_VAL or n > self.MAX_VAL:
            raise ValueError("%d is not in the allowed range of [%d, %d]" % (n, self.MIN_VAL, self.MAX_VAL))
        self.n = n

    def get_binary(self):
        return self.n

    def get_hex(self):
        return binascii.hexlify(self.STRUCT.pack(self.n))

    @classmethod
    def from_binary(cls, n):
        if n is None:
            return None
        return cls(n)

    @classmethod
    def from_hex(cls, s):
        if s is None:
            return None
        if len(s) % 2 != 0:
            s = '0%s' % s
        return cls(cls.STRUCT.unpack(s.decode('hex'))[0])


class ZipkinData(object):
    """
    The tracing data being passed between services via HTTP headers
    """
    def __init__(self, trace_id=None, span_id=None, parent_span_id=None, sampled=False, flags=False):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.sampled = sampled
        self.flags = flags

    def is_tracing(self):
        return self.sampled or self.flags