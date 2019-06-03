import base64

from thriftpy.protocol import TBinaryProtocol
from thriftpy.protocol import TBinaryProtocolFactory
from thriftpy.transport import TFramedTransportFactory
from thriftpy.transport import TMemoryBuffer
from thriftpy.rpc import make_client

from .thrift.scribe import scribe_thrift


def _build_log_message(span):
    trans = TMemoryBuffer()
    protocol = TBinaryProtocol(trans=trans)
    span.write(protocol)
    return base64.b64encode(trans.getvalue())


class ScribeWriter(object):
    def __init__(self, host, port,  category='zipkin', timeout=None):
        self.category = category
        self.host = host
        self.port = port
        self.timeout = timeout
        self.protocol_factory = TBinaryProtocolFactory(strict_read=False, strict_write=False)
        self.transport_factory = TFramedTransportFactory()

    def __span_to_entry(self, span):
        data = _build_log_message(span)
        message = b"\\n".join([r for r in data.split(b"\n") if r != b""]) + b"\n"
        return scribe_thrift.LogEntry(category=self.category, message=message)

    def write_multiple(self, spans):
        entries = [self.__span_to_entry(span) for span in spans]
        # TODO(will): The old implementation used to open and close transport here, with the new
        # client based API this seems like the only way to get parity. Not sure if we would rather
        # try persistent connections + reconnecting in the long run.
        client = make_client(scribe_thrift.scribe,
                             host=self.host,
                             port=self.port,
                             timeout=self.timeout,
                             proto_factory=self.protocol_factory,
                             trans_factory=self.transport_factory)
        client.Log(entries)
        client.close()

    def write(self, span):
        self.write_multiple([span])
