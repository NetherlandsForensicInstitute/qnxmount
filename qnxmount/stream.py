from kaitaistruct import KaitaiStream
import mmap

class Stream:
    def __init__(self, path, offset=0):
        self.path = path
        self.offset = offset

    def __enter__(self):
        self.f = open(self.path, 'rb')
        self.mm = mmap.mmap(self.f.fileno(), length=0, access=mmap.ACCESS_READ, offset=self.offset)
        self.stream = KaitaiStream(self.mm)
        return self.stream

    def __exit__(self, type, value, traceback):
        self.stream.close()
        self.mm.close()
        self.f.close()