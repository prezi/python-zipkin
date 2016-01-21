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

    def write(self, span):
        data = self.__build_log_message(span)
        message = "\\n".join([r for r in data.split("\n") if r != ""]) + "\n"
        self.transport.open()
        entry = Scribe.LogEntry(category=self.category, message=message)
        self.client.Log([entry])
        self.transport.close()

    def __build_log_message(self, span):
        trans = TTransport.TMemoryBuffer()
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(trans=trans)
        span.write(protocol)
        return base64.b64encode(trans.getvalue())