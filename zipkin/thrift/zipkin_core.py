import os
import sys
import thriftpy

thrift_dir = os.path.dirname(os.path.realpath(__file__))
thrift_file = open(os.path.join(thrift_dir, 'zipkinCore.thrift'), 'r')


# This is a hack to support python3 as ply expects a string result from file.read()
class FileDecoder(object):
    def __init__(self, file):
        self.file = file

    def read(self):
        byte_string = self.file.read()
        if isinstance(byte_string, str):
            return byte_string
        return byte_string.decode('utf-8')

if sys.version_info >= (3, 0):
    thrift_file = FileDecoder(thrift_file)

ttypes = thriftpy.load_fp(FileDecoder(thrift_file), module_name='zipkin_core_thrift')
