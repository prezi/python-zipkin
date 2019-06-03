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
        s = s.zfill(16)
        return cls(cls.STRUCT.unpack(binascii.unhexlify(s))[0])


class ZipkinTraceId(object):
    '''ZipkinTraceId repesents as 128 bit Zipkin Trace ID made up of 2 x 64-bit
    signed numbers'''

    MAX_VAL = 2 ** 63 - 1
    MIN_VAL = -MAX_VAL

    STRUCT = struct.Struct('!qq')

    def __init__(self, low, high):
        if low < self.MIN_VAL or low > self.MAX_VAL:
            raise ValueError(
                "low bytes %d are not in the allowed range of [%d, %d]" %
                (low, self.MIN_VAL, self.MAX_VAL))
        if high < self.MIN_VAL or high > self.MAX_VAL:
            raise ValueError(
                "high bytes %d are not in the allowed range of [%d, %d]"
                % (high, self.MIN_VAL, self.MAX_VAL))

        self.low = low
        self.high = high

    def get_binary_low_bytes(self):
        '''Return the low 64bit number of the Trace ID. Originally Trace IDs
        were 64bits and thus this number would represent the entire Trace ID'''
        return self.low

    def get_binary_high_bytes(self):
        '''Return the high 64bit number of the Trace ID, if set. Originally,
        Trace IDs were 64bits and thus the high-order 64bits may be all 0'''
        return self.high

    def get_hex(self):
        # NB: high-order bytes get packed first
        return binascii.hexlify(self.STRUCT.pack(self.high, self.low))

    @classmethod
    def from_binary(cls, low, high):
        if low is None or high is None:
            return None
        return cls(low=low, high=high)

    @classmethod
    def from_hex(cls, s):
        if s is None:
            return None
        s = s.zfill(32)
        high, low = cls.STRUCT.unpack(binascii.unhexlify(s))
        return cls(low=low, high=high)


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
