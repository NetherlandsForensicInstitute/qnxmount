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
        pass

    class Userdata(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

        @property
        def as_ftable(self):
            if hasattr(self, '_m_as_ftable'):
                return self._m_as_ftable

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_as_ftable = Parser.Ftable(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_as_ftable', None)

        @property
        def raw(self):
            if hasattr(self, '_m_raw'):
                return self._m_raw

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_raw = self._io.read_bytes_full()
            self._io.seek(_pos)
            return getattr(self, '_m_raw', None)


    class NoEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


    class FtableEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.efid = self._io.read_u2le()
            self.pfid = self._io.read_u2le()
            _on = self.entry_type
            if _on == 0:
                self.body = Parser.FileEntry(self._io, self, self._root)
            elif _on == 1:
                self.body = Parser.ExtnameEntry(self._io, self, self._root)
            else:
                self.body = Parser.NoEntry(self._io, self, self._root)

        @property
        def has_no_parent(self):
            """These are deleted files or not-initialised entries."""
            if hasattr(self, '_m_has_no_parent'):
                return self._m_has_no_parent

            self._m_has_no_parent = self.pfid == 65535
            return getattr(self, '_m_has_no_parent', None)

        @property
        def is_extension(self):
            if hasattr(self, '_m_is_extension'):
                return self._m_is_extension

            self._m_is_extension = self.efid == 32768
            return getattr(self, '_m_is_extension', None)

        @property
        def full_name(self):
            if hasattr(self, '_m_full_name'):
                return self._m_full_name

            self._m_full_name = 0
            return getattr(self, '_m_full_name', None)

        @property
        def test(self):
            if hasattr(self, '_m_test'):
                return self._m_test

            self._m_test = (self.efid & 32768) == 32768
            return getattr(self, '_m_test', None)

        @property
        def is_solo(self):
            if hasattr(self, '_m_is_solo'):
                return self._m_is_solo

            self._m_is_solo = self.efid == 0
            return getattr(self, '_m_is_solo', None)

        @property
        def is_valid(self):
            if hasattr(self, '_m_is_valid'):
                return self._m_is_valid

            self._m_is_valid = self.efid != 65535
            return getattr(self, '_m_is_valid', None)

        @property
        def entry_type(self):
            """Dummy variable to switch on."""
            if hasattr(self, '_m_entry_type'):
                return self._m_entry_type

            self._m_entry_type = (int(self.is_extension) + (int(self.has_no_parent) * 2))
            return getattr(self, '_m_entry_type', None)


    class TransCode(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = self._io.read_u1()

        @property
        def deverr(self):
            if hasattr(self, '_m_deverr'):
                return self._m_deverr

            self._m_deverr = (self.code & 15) == 6
            return getattr(self, '_m_deverr', None)

        @property
        def dataerr(self):
            if hasattr(self, '_m_dataerr'):
                return self._m_dataerr

            self._m_dataerr = (self.code & 15) == 5
            return getattr(self, '_m_dataerr', None)

        @property
        def erased(self):
            if hasattr(self, '_m_erased'):
                return self._m_erased

            self._m_erased = (self.code & 15) == 2
            return getattr(self, '_m_erased', None)

        @property
        def ok(self):
            if hasattr(self, '_m_ok'):
                return self._m_ok

            self._m_ok = (self.code & 15) == 0
            return getattr(self, '_m_ok', None)

        @property
        def ecc(self):
            if hasattr(self, '_m_ecc'):
                return self._m_ecc

            self._m_ecc = (self.code & 15) == 1
            return getattr(self, '_m_ecc', None)

        @property
        def foxes(self):
            if hasattr(self, '_m_foxes'):
                return self._m_foxes

            self._m_foxes = (self.code & 15) == 3
            return getattr(self, '_m_foxes', None)

        @property
        def badblk(self):
            if hasattr(self, '_m_badblk'):
                return self._m_badblk

            self._m_badblk = (self.code & 15) == 7
            return getattr(self, '_m_badblk', None)


    class Page(KaitaiStruct):
        def __init__(self, pagesize, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.pagesize = pagesize
            self._read()

        def _read(self):
            self._raw_data = self._io.read_bytes(self.pagesize)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = Parser.Userdata(_io__raw_data, self, self._root)
            self.transaction = Parser.Transaction(self._io, self, self._root)


    class Pages(KaitaiStruct):
        def __init__(self, pagesize, num_pages, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.pagesize = pagesize
            self.num_pages = num_pages
            self._read()

        def _read(self):
            self.pages = []
            for i in range(self.num_pages):
                self.pages.append(Parser.Page(self.pagesize, self._io, self, self._root))



    class Ftable(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(Parser.FtableEntry(self._io, self, self._root))
                i += 1



    class FileEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = self._io.read_u4le()
            self.uid = self._io.read_u4le()
            self.gid = self._io.read_u4le()
            self.atime = self._io.read_u4le()
            self.mtime = self._io.read_u4le()
            self.ctime = self._io.read_u4le()
            self.size = self._io.read_u4le()
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"utf-8")


    class Transaction(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fid = self._io.read_u4le()
            self.cluster = self._io.read_u4le()
            self.nclusters = self._io.read_u2le()
            self.tacode = Parser.TransCode(self._io, self, self._root)
            self.dacode = Parser.TransCode(self._io, self, self._root)
            self.sequence = self._io.read_u4le()


    class ExtnameEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(59), 0, False)).decode(u"utf-8")
            self.type = self._io.read_u1()

        @property
        def is_valid(self):
            if hasattr(self, '_m_is_valid'):
                return self._m_is_valid

            self._m_is_valid = self.type == 0
            return getattr(self, '_m_is_valid', None)


    @property
    def fid_firstfile(self):
        if hasattr(self, '_m_fid_firstfile'):
            return self._m_fid_firstfile

        self._m_fid_firstfile = 6
        return getattr(self, '_m_fid_firstfile', None)

    @property
    def pages(self):
        if hasattr(self, '_m_pages'):
            return self._m_pages

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_pages = Parser.Pages(2048, 9, self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_pages', None)

    @property
    def fid_badblks(self):
        if hasattr(self, '_m_fid_badblks'):
            return self._m_fid_badblks

        self._m_fid_badblks = 2
        return getattr(self, '_m_fid_badblks', None)

    @property
    def fid_ftable(self):
        if hasattr(self, '_m_fid_ftable'):
            return self._m_fid_ftable

        self._m_fid_ftable = 1
        return getattr(self, '_m_fid_ftable', None)

    @property
    def fid_root(self):
        if hasattr(self, '_m_fid_root'):
            return self._m_fid_root

        self._m_fid_root = 0
        return getattr(self, '_m_fid_root', None)

    @property
    def fid_counts(self):
        if hasattr(self, '_m_fid_counts'):
            return self._m_fid_counts

        self._m_fid_counts = 3
        return getattr(self, '_m_fid_counts', None)

    @property
    def fid_lostfound(self):
        if hasattr(self, '_m_fid_lostfound'):
            return self._m_fid_lostfound

        self._m_fid_lostfound = 4
        return getattr(self, '_m_fid_lostfound', None)

    @property
    def fid_reserved(self):
        if hasattr(self, '_m_fid_reserved'):
            return self._m_fid_reserved

        self._m_fid_reserved = 5
        return getattr(self, '_m_fid_reserved', None)


