# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Parser(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.qnx6_bootblock = Parser.Bootblock(self._io, self, self._root)

    class DirEntryLongname(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.zeros = self._io.read_bytes(3)
            self.index = self._io.read_u4le()
            self.checksum = self._io.read_u4le()
            self.more_zeros = self._io.read_bytes(16)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name

            self._m_name = 0
            return getattr(self, '_m_name', None)


    class Shortname(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (self._io.read_bytes_term(0, False, True, False)).decode(u"UTF-8")


    class DirEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.inode_number = self._io.read_u4le()
            self.length = self._io.read_u1()
            _on = self.length
            if _on == 255:
                self._raw_content = self._io.read_bytes(27)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Parser.DirEntryLongname(_io__raw_content, self, self._root)
            else:
                self._raw_content = self._io.read_bytes(27)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Parser.Shortname(_io__raw_content, self, self._root)


    class Superblock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x22\x11\x19\x68":
                raise kaitaistruct.ValidationNotEqualError(b"\x22\x11\x19\x68", self.magic, self._io, u"/types/superblock/seq/0")
            self.crc = self._io.read_u4le()
            self.serial = self._io.read_u8le()
            self.ctime = self._io.read_u4le()
            self.atime = self._io.read_u4le()
            self.flag = self._io.read_u4le()
            self.version1 = self._io.read_u2le()
            self.version2 = self._io.read_u2le()
            self.volumeid = self._io.read_bytes(16)
            self.blocksize = self._io.read_u4le()
            self.num_inodes = self._io.read_u4le()
            self.free_inodes = self._io.read_u4le()
            self.num_blocks = self._io.read_u4le()
            self.free_blocks = self._io.read_u4le()
            self.allocgroup = self._io.read_u4le()
            self.inodes = Parser.Rootnode(self._io, self, self._root)
            self.bitmap = Parser.Rootnode(self._io, self, self._root)
            self.longfile = Parser.Rootnode(self._io, self, self._root)
            self.iclaim = Parser.Rootnode(self._io, self, self._root)
            self.iextra = Parser.Rootnode(self._io, self, self._root)
            self.migrate_blocks = self._io.read_u4le()
            self.scrub_block = self._io.read_u4le()
            self.spare = self._io.read_bytes(32)


    class Inode(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.size = self._io.read_u8le()
            self.uid = self._io.read_u4le()
            self.gid = self._io.read_u4le()
            self.ftime = self._io.read_u4le()
            self.mtime = self._io.read_u4le()
            self.atime = self._io.read_u4le()
            self.ctime = self._io.read_u4le()
            self.mode = self._io.read_u2le()
            self.ext_mode = self._io.read_u2le()
            self.pointers = []
            for i in range(16):
                self.pointers.append(Parser.BlockPointer(self._io, self, self._root))

            self.level = self._io.read_u1()
            self.status = self._io.read_bytes(1)
            self.unknown = self._io.read_bytes(2)
            self.zeros = []
            for i in range(6):
                self.zeros.append(self._io.read_u4le())



    class Rootnode(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.size = self._io.read_u8le()
            self.pointers = []
            for i in range(16):
                self.pointers.append(Parser.BlockPointer(self._io, self, self._root))

            self.level = self._io.read_u1()
            self.mode = self._io.read_bytes(1)
            self.spare = self._io.read_bytes(6)


    class BlockPointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ptr = self._io.read_u4le()

        @property
        def raw_body(self):
            if hasattr(self, '_m_raw_body'):
                return self._m_raw_body

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.data_start + (self.ptr * self._root.blocksize)))
            self._m_raw_body = io.read_bytes(self._root.blocksize)
            io.seek(_pos)
            return getattr(self, '_m_raw_body', None)

        @property
        def body_as_pointer_list(self):
            if hasattr(self, '_m_body_as_pointer_list'):
                return self._m_body_as_pointer_list

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.data_start + (self.ptr * self._root.blocksize)))
            self._m_body_as_pointer_list = []
            for i in range(self._root.blocksize // 4):
                self._m_body_as_pointer_list.append(Parser.BlockPointer(io, self, self._root))

            io.seek(_pos)
            return getattr(self, '_m_body_as_pointer_list', None)


    class Bootblock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xEB\x10\x90\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xEB\x10\x90\x00", self.magic, self._io, u"/types/bootblock/seq/0")
            self.offset_qnx6fs = self._io.read_u4le()
            self.sblk0 = self._io.read_u4le()
            self.sblk1 = self._io.read_u4le()

        @property
        def superblock0(self):
            if hasattr(self, '_m_superblock0'):
                return self._m_superblock0

            io = self._root._io
            _pos = io.pos()
            io.seek((self.sblk0 * 512))
            self._m_superblock0 = Parser.Superblock(io, self, self._root)
            io.seek(_pos)
            return getattr(self, '_m_superblock0', None)

        @property
        def superblock1(self):
            if hasattr(self, '_m_superblock1'):
                return self._m_superblock1

            io = self._root._io
            _pos = io.pos()
            io.seek((self.sblk1 * 512))
            self._m_superblock1 = Parser.Superblock(io, self, self._root)
            io.seek(_pos)
            return getattr(self, '_m_superblock1', None)

        @property
        def superblock0_raw(self):
            if hasattr(self, '_m_superblock0_raw'):
                return self._m_superblock0_raw

            io = self._root._io
            _pos = io.pos()
            io.seek((self.sblk0 * 512))
            self._m_superblock0_raw = io.read_bytes(512)
            io.seek(_pos)
            return getattr(self, '_m_superblock0_raw', None)

        @property
        def superblock1_raw(self):
            if hasattr(self, '_m_superblock1_raw'):
                return self._m_superblock1_raw

            io = self._root._io
            _pos = io.pos()
            io.seek((self.sblk1 * 512))
            self._m_superblock1_raw = io.read_bytes(512)
            io.seek(_pos)
            return getattr(self, '_m_superblock1_raw', None)


    class Longname(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = self._io.read_u2le()
            self.name = (self._io.read_bytes(self.length)).decode(u"UTF-8")


    class Directory(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(Parser.DirEntry(self._io, self, self._root))
                i += 1



    @property
    def sizeof_inode(self):
        if hasattr(self, '_m_sizeof_inode'):
            return self._m_sizeof_inode

        self._m_sizeof_inode = 128
        return getattr(self, '_m_sizeof_inode', None)

    @property
    def blocksize(self):
        if hasattr(self, '_m_blocksize'):
            return self._m_blocksize

        self._m_blocksize = self.qnx6_bootblock.superblock0.blocksize
        return getattr(self, '_m_blocksize', None)

    @property
    def abs_data_start_padding(self):
        """Kaitai does not support abs()."""
        if hasattr(self, '_m_abs_data_start_padding'):
            return self._m_abs_data_start_padding

        self._m_abs_data_start_padding = ((self.blocksize - 12288) if self.blocksize > 12288 else (12288 - self.blocksize))
        return getattr(self, '_m_abs_data_start_padding', None)

    @property
    def data_start(self):
        """https://github.com/RunZeJustin/qnx660/blob/47c4158e3993d7536170b649e6c1e09552318fb4/target/qnx6/usr/include/sys/fs_qnx6.h."""
        if hasattr(self, '_m_data_start'):
            return self._m_data_start

        self._m_data_start = (12288 + (0 if self.blocksize <= 4096 else self.abs_data_start_padding))
        return getattr(self, '_m_data_start', None)


