import base64
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from zipkin._thrift.scribe import Scribe


class ScribeWriter(object):
    def __init__(self, host, port,  category='zipkin'):
        socket = TSocket.TSocket(host=host, port=port)
        self.transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(
            trans=self.transport, strictRead=False, strictWrite=False)
        self.client = Scribe.Client(iprot=protocol, oprot=protocol)
        self.category = category

    def __span_to_entry(span):
        data = self.__build_log_message(span)
        message = "\\n".join([r for r in data.split("\n") if r != ""]) + "\n"
        return Scribe.LogEntry(category=self.category, message=message)

    def write_multiple(self, spans):
        entries = [self.__span_to_entry(span) for span in spans]
        self.transport.open()
        self.client.Log(entries)
        self.transport.close()

    def write(self, span):
        self.write_multiple([span])

    def __build_log_message(self, span):
        trans = TTransport.TMemoryBuffer()
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(trans=trans)
        span.write(protocol)
        return base64.b64encode(trans.getvalue())
