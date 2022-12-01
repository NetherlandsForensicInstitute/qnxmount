from pathlib import Path
from qnxmount.efs.parser import Parser
from kaitaistruct import KaitaiStream
from functools import lru_cache
import mmap
import re
import logging

LOGGER = logging.getLogger(__name__)


class KaitaiIO:
    """This class implements the basic functionality to create a Kaitai io stream.

    Args:
        path (Path): Path to the image.
        offset (int): Offset in the image to start the Kaitai stream at.

    Attributes:
        path (Path): Path to the image.
        f: File handle.
        mm (mmap): Memory map of the file.
        stream (KaitaiStream): Kaitai data stream of memory-mapped file.
    """
    def __init__(self, path, offset=0):
        self.path = path
        self.f = open(self.path, 'rb')
        self.mm = mmap.mmap(self.f.fileno(), length=0, offset=offset, access=mmap.ACCESS_READ)
        self.stream = KaitaiStream(self.mm)

    def __del__(self):
        self.stream.close()
        self.mm.close()
        self.f.close()


class EFS(KaitaiIO):
    """This class implements the logic of the EFS file system and uses the
    structures in the class :class:`Parser`.

    Args:
        path (Path): Path to image.
        boot: Bootinfo object of the EFS.
        offset: Start of first unit of the partition in image.

    Attributes:
        boot (Parser.BootInfo): Boot info.
        parser (Parser): Kaitai generated parser object.
        logi_map (Dict[int, Parser.Unit]: Logic mapping of units.
        root (Parser.DirEntry): Root of partition.
    """
    def __init__(self, path: Path, boot: Parser.BootInfo, offset: int = 0):
        super().__init__(path, offset)
        self.boot = boot
        self.parser = Parser(self.stream)
        self.parser._m_units = self.parser.Units(boot.align_pow2, boot.unit_total, self.parser._io, _root=self.parser)
        self.logi_map = self.get_logi_map()
        root_ext = self.get_ext_ptr(self.boot.root)
        self.root = root_ext.as_dir_entry

    def get_logi_map(self):
        """Create a mapping of units in logical order.

        Returns:
            Dict[int, EfsParset.Unit]: Dictionary with logical mapping.
        """
        logi_map = {unit.logi.logi: unit for unit in self.parser.units.unit_list if not is_spare(unit)}
        assert list(sorted(logi_map.keys())) == list(range(1, self.boot.unit_total - self.boot.unit_spare + 1)), 'Not all units are accounted for!'
        return logi_map

    def get_ext_ptr(self, ptr: Parser.ExtentPtr) -> Parser.Extent:
        """Get extent from extent pointer.

        Args:
            ptr: Extent pointer

        Returns:
            Parser.Extent: Extent
        """
        extent = self.logi_map[ptr.logi_unit].extents[ptr.index]
        while not extent.header.status0.no_super:
            ptr = extent.header.super
            extent = self.get_ext_ptr(ptr)
        return extent

    def get_extents(self, dir_entry: Parser.DirEntry):
        """Get all extents from a directory entry.

        Args:
            dir_entry (Parser.DirEntry): Directory entry.

        Yields:
            Parser.Extent: All relevant extents in the directory entry.
        """
        extent = self.get_ext_ptr(dir_entry.first)
        yield extent

        while not extent.header.status0.no_next:
            extent = self.get_ext_ptr(extent.header.next)
            yield extent

    def read_dir(self, dir_entry: Parser.DirEntry):
        """Read a directory.

        Args:
            dir_entry (Parser.DirEntry): Directory entry.

        Yields:
            Parser.DirEntry: Extent parsed as a directory entry.
        """
        for extent in self.get_extents(dir_entry):
            if not extent.header.text_size:
                break
            yield extent.as_dir_entry

    def stat(self, dir_entry: Parser.DirEntry):
        """Return stat info of a directory entry.

        Args:
            dir_entry (Parser.DirEntry): Directory entry.

        Returns:
            int: Mode.
        """
        mode = dir_entry.stat.mode
        return mode

    def read_file(self, dir_entry: Parser.DirEntry):
        """Read contents of a file.

        Args:
            dir_entry (Parser.DirEntry): Directory entry.

        Returns:
            bytes: Full file content.
        """
        return b''.join(extent.text for extent in self.get_extents(dir_entry))

    @lru_cache(maxsize=128)
    def get_dir_entry_from_path(self, path: Path) -> Parser.DirEntry:
        """Get dir entry from path.

        Args:
            path (Path): path.

        Returns:
            Parser.DirEntry: Directory entry.
        """
        if not path.name:
            return self.root
        parent_entry = self.get_dir_entry_from_path(path.parent)
        for entry in self.read_dir(parent_entry):
            if entry.name == path.name:
                return entry


def scan_partitions(path):
    """Scans a flash image for valid EFS partitions based on the boot_info.

    Args:
        path(Path): Path to the image.

    Yields:
        EFS: An initialized EFS parser object for each valid partition found.
    """
    kaitai_io = KaitaiIO(path)
    sig_pattern = re.compile(b'QSSL_F3S', re.MULTILINE)
    for hit in re.finditer(sig_pattern, kaitai_io.mm):
        stream = kaitai_io.stream
        stream.seek(hit.start() - 4)
        boot = Parser.BootInfo(stream)
        if not boot.is_valid:
            continue

        boot_unit_start = hit.start() & 0xfffff000
        stream.seek(boot_unit_start)
        unit_info = Parser.UnitInfo(stream)

        # TODO maybe add stricter checking if partition is valid
        start_offset = boot_unit_start - boot.unit_index * unit_info.unit_size
        LOGGER.info(f'Valid partition found at {hex(start_offset)} (with boot entry located at {hex(hit.start())})')
        yield EFS(kaitai_io.path, boot, offset=start_offset)


def is_spare(unit: Parser.Unit):
    """Check if EFS unit is a spare unit.

    Args:
        unit (Parser.Unit): EFS unit.

    Returns:
        bool: Boolean answer.
    """
    if ((len(unit.extents) == 1) or
            (len(unit.extents) == 2 and unit.extents[1].header.status1 == 0xffffffff)):
        return True
    return False
