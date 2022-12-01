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

    class Extent(KaitaiStruct):
        def __init__(self, i, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.i = i
            self._read()

        def _read(self):
            pass

        @property
        def text_offset(self):
            if hasattr(self, '_m_text_offset'):
                return self._m_text_offset

            self._m_text_offset = (((self.header.text_offset_hi << 16) + self.header.text_offset_lo) << self._parent._parent.align_pow2)
            return getattr(self, '_m_text_offset', None)

        @property
        def text(self):
            if hasattr(self, '_m_text'):
                return self._m_text

            _pos = self._io.pos()
            self._io.seek(self.text_offset)
            self._m_text = self._io.read_bytes(self.header.text_size)
            self._io.seek(_pos)
            return getattr(self, '_m_text', None)

        @property
        def as_dir_entry(self):
            if hasattr(self, '_m_as_dir_entry'):
                return self._m_as_dir_entry

            _pos = self._io.pos()
            self._io.seek(self.text_offset)
            self._raw__m_as_dir_entry = self._io.read_bytes(self.header.text_size)
            _io__raw__m_as_dir_entry = KaitaiStream(BytesIO(self._raw__m_as_dir_entry))
            self._m_as_dir_entry = Parser.DirEntry(_io__raw__m_as_dir_entry, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_as_dir_entry', None)

        @property
        def header(self):
            if hasattr(self, '_m_header'):
                return self._m_header

            _pos = self._io.pos()
            self._io.seek((self._root.unit_size - (32 * (self.i + 1))))
            self._raw__m_header = self._io.read_bytes(32)
            _io__raw__m_header = KaitaiStream(BytesIO(self._raw__m_header))
            self._m_header = Parser.ExtentHeader(_io__raw__m_header, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_header', None)

        @property
        def special_text(self):
            if hasattr(self, '_m_special_text'):
                return self._m_special_text

            _pos = self._io.pos()
            self._io.seek(self.text_offset)
            self._raw__m_special_text = self._io.read_bytes(self.header.text_size)
            _io__raw__m_special_text = KaitaiStream(BytesIO(self._raw__m_special_text))
            self._m_special_text = Parser.SpecialExtentP(self.i, _io__raw__m_special_text, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_special_text', None)


    class UnitInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.struct_size = self._io.read_u2le()
            self.endian = self._io.read_bytes(1)
            self.pad = self._io.read_bytes(1)
            if not self.pad == b"\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\xFF", self.pad, self._io, u"/types/unit_info/seq/2")
            self.unit_pow2 = self._io.read_u2le()
            self.reserve = self._io.read_bytes(2)
            if not self.reserve == b"\xFF\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\xFF\xFF", self.reserve, self._io, u"/types/unit_info/seq/4")
            self.erase_count = self._io.read_u4le()
            self.boot = Parser.ExtentPtr(self._io, self, self._root)

        @property
        def unit_size(self):
            if hasattr(self, '_m_unit_size'):
                return self._m_unit_size

            self._m_unit_size = (1 << self.unit_pow2)
            return getattr(self, '_m_unit_size', None)


    class ExtentPtr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.logi_unit = self._io.read_u2le()
            self.index = self._io.read_u2le()


    class SpecialExtentP(KaitaiStruct):
        def __init__(self, idx, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.idx = idx
            self._read()

        def _read(self):
            _on = self.idx
            if _on == 0:
                self.body = Parser.UnitInfo(self._io, self, self._root)
            elif _on == 4:
                self.body = Parser.DirEntry(self._io, self, self._root)
            elif _on == 1:
                self.body = Parser.UnitLogi(self._io, self, self._root)
            elif _on == 3:
                self.body = Parser.DirEntry(self._io, self, self._root)
            elif _on == 2:
                self.body = Parser.BootInfo(self._io, self, self._root)


    class Stat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.struct_size = self._io.read_u2le()
            self.mode = self._io.read_u2le()
            self.uid = self._io.read_u4le()
            self.gid = self._io.read_u4le()
            self.mtime = self._io.read_u4le()
            self.ctime = self._io.read_u4le()


    class UnitLogi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.struct_size = self._io.read_u2le()
            self.logi = self._io.read_u2le()
            self.age = self._io.read_u4le()
            self.pad = self._io.read_bytes((self.struct_size - 24))
            self.md5 = self._io.read_bytes(16)


    class DirEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.struct_size = self._io.read_u2le()
            self.moves = self._io.read_u1()
            self.namelen = self._io.read_u1()
            self.first = Parser.ExtentPtr(self._io, self, self._root)
            self.name = (self._io.read_bytes_term(0, False, True, True)).decode(u"UTF-8")
            self.name_pad = self._io.read_bytes((((self.namelen + 3) & 252) - self.namelen))
            self.stat = Parser.Stat(self._io, self, self._root)


    class ExtentHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status0 = Parser.HeaderStatus(self._io, self, self._root)
            self.status1 = self._io.read_u4le()
            self.status2 = self._io.read_u4le()
            self.ecc = self._io.read_bytes(6)
            self.reserve = self._io.read_bytes(1)
            if not self.reserve == b"\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\xFF", self.reserve, self._io, u"/types/extent_header/seq/4")
            self.text_offset_hi = self._io.read_u1()
            self.text_offset_lo = self._io.read_u2le()
            self.text_size = self._io.read_u2le()
            self.next = Parser.ExtentPtr(self._io, self, self._root)
            self.super = Parser.ExtentPtr(self._io, self, self._root)


    class HeaderStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_write = self._io.read_bits_int_le(1) != 0
            self.no_next = self._io.read_bits_int_le(1) != 0
            self.no_super = self._io.read_bits_int_le(1) != 0
            self.no_split = self._io.read_bits_int_le(1) != 0
            self.condition = self._io.read_bits_int_le(3)
            self.ext_last = self._io.read_bits_int_le(1) != 0
            self.type = self._io.read_bits_int_le(2)
            self.basic = self._io.read_bits_int_le(1) != 0
            self.pad = self._io.read_bits_int_le(21)

        @property
        def is_file(self):
            if hasattr(self, '_m_is_file'):
                return self._m_is_file

            self._m_is_file = self.type == 3
            return getattr(self, '_m_is_file', None)

        @property
        def is_dir(self):
            if hasattr(self, '_m_is_dir'):
                return self._m_is_dir

            self._m_is_dir = self.type == 2
            return getattr(self, '_m_is_dir', None)

        @property
        def is_sys(self):
            if hasattr(self, '_m_is_sys'):
                return self._m_is_sys

            self._m_is_sys = self.type == 1
            return getattr(self, '_m_is_sys', None)


    class BootInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.struct_size = self._io.read_u2le()
            self.rev_major = self._io.read_u1()
            self.rev_minor = self._io.read_u1()
            self.sig = self._io.read_bytes(8)
            if not self.sig == b"\x51\x53\x53\x4C\x5F\x46\x33\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x51\x53\x53\x4C\x5F\x46\x33\x53", self.sig, self._io, u"/types/boot_info/seq/3")
            self.unit_index = self._io.read_u2le()
            self.unit_total = self._io.read_u2le()
            self.unit_spare = self._io.read_u2le()
            self.align_pow2 = self._io.read_u2le()
            self.root = Parser.ExtentPtr(self._io, self, self._root)

        @property
        def is_valid(self):
            if hasattr(self, '_m_is_valid'):
                return self._m_is_valid

            self._m_is_valid =  ((self.struct_size == 24) and (self.rev_major == 3) and (self.rev_minor == 0)) 
            return getattr(self, '_m_is_valid', None)


    class Units(KaitaiStruct):
        def __init__(self, align_pow2, num_units, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.align_pow2 = align_pow2
            self.num_units = num_units
            self._read()

        def _read(self):
            self._raw_unit_list = []
            self.unit_list = []
            for i in range(self.num_units):
                self._raw_unit_list.append(self._io.read_bytes(self._root.unit_size))
                _io__raw_unit_list = KaitaiStream(BytesIO(self._raw_unit_list[i]))
                self.unit_list.append(Parser.Unit(_io__raw_unit_list, self, self._root))



    class Unit(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

        @property
        def raw(self):
            if hasattr(self, '_m_raw'):
                return self._m_raw

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_raw = self._io.read_bytes(self._root.unit_size)
            self._io.seek(_pos)
            return getattr(self, '_m_raw', None)

        @property
        def extents(self):
            if hasattr(self, '_m_extents'):
                return self._m_extents

            self._m_extents = []
            i = 0
            while True:
                _ = Parser.Extent(i, self._io, self, self._root)
                self._m_extents.append(_)
                if _.header.status0.ext_last:
                    break
                i += 1
            return getattr(self, '_m_extents', None)

        @property
        def info(self):
            if hasattr(self, '_m_info'):
                return self._m_info

            self._m_info = self.extents[0].special_text.body
            return getattr(self, '_m_info', None)

        @property
        def logi(self):
            if hasattr(self, '_m_logi'):
                return self._m_logi

            self._m_logi = self.extents[1].special_text.body
            return getattr(self, '_m_logi', None)


    @property
    def unit_size(self):
        if hasattr(self, '_m_unit_size'):
            return self._m_unit_size

        self._m_unit_size = self.unit_shortcut.unit_size
        return getattr(self, '_m_unit_size', None)

    @property
    def unit_shortcut(self):
        """Needed for bootstrapping the unit size value."""
        if hasattr(self, '_m_unit_shortcut'):
            return self._m_unit_shortcut

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_unit_shortcut = Parser.UnitInfo(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_unit_shortcut', None)

    @property
    def units(self):
        """Dummy values to satisfy the compiler, we will manually instantiate it anyway."""
        if hasattr(self, '_m_units'):
            return self._m_units

        self._m_units = Parser.Units(1, 1, self._io, self, self._root)
        return getattr(self, '_m_units', None)


