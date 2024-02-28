import stat
from functools import lru_cache
from pathlib import Path

import crcmod
from kaitaistruct import BytesIO, KaitaiStream

from qnxmount.qnx6.parser import Parser


class QNX6FS:
    """This class implements the logic of the qnx6 file system and uses the
    structures in the class :class:`Parser`.

    Args:
        stream: Kaitaistream containing the qnx6 file system.

    Attributes:
        stream (KaitaiStream): Kaitai data stream of qnx6 file system.
        parser (Parser): Parser class automatically generated from .ksy file.
        blocksize (int): Block size.
        active_superblock (Parser.Superblock): Active superblock.
    """

    def __init__(self, stream):
        self.cache = dict()
        self.stream = stream
        self.parser = Parser(self.stream)
        self.check_superblock_crc()

        self.blocksize = self.parser.blocksize
        if self.parser.qnx6_bootblock.superblock0.serial >= self.parser.qnx6_bootblock.superblock1.serial:
            self.active_superblock = self.parser.qnx6_bootblock.superblock0
        else:
            self.active_superblock = self.parser.qnx6_bootblock.superblock1

    def add_to_cache(self, path: Path, inode_number: int) -> None:
        self.cache[path] = inode_number

    def get_dir_from_path(self, path):
        """Get directory content from its path.

        Args:
            path (Union[Path, PurePath]): Path to directory.

        Returns:
            Parser.Directory: Parsed directory.
        """
        inode_number = self.get_inode_number_from_path(path)
        return self.get_dir(inode_number)

    @lru_cache(maxsize=4096)
    def get_inode_number_from_path(self, path):
        """Get the inode number from a path.

        Args:
            path (Union[Path, PurePath]): Path to object.

        Returns:
            int: Inode number.
        """
        if not path.name:
            return 1
        if path in self.cache:
            return self.cache[path]

        inode_number = self.get_inode_number_from_path(path.parent)
        directory = self.get_dir(inode_number)
        for entry in directory.entries:
            if entry.content.name == path.name:
                self.add_to_cache(path, entry.inode_number)
                return entry.inode_number

        return None

    def get_longname(self, index):
        """Get longname from its index.

        Args:
            index (int): index in the longfile inode.

        Returns:
            Parser.Longname: Longname object.
        """
        longname_raw = self.read_file(
            self.active_superblock.longfile, offset=index * self.parser.blocksize, size=self.parser.blocksize
        )
        longname = self.parser.Longname(KaitaiStream(BytesIO(longname_raw)), _root=self.parser._root)
        return longname

    def get_dir(self, inode_number):
        """Get directory content from its inode number.

        Args:
            inode_number (int): Inode number of the directory.

        Returns:
            Parser.Directory: Parsed directory.
        """
        assert inode_number >= 1, "Inode number smaller than 1 not allowed!"
        dir_raw = self.read_dir(inode_number)
        directory = self.parser.Directory(KaitaiStream(BytesIO(dir_raw)), _root=self.parser._root)

        valid_entries = []
        for entry in filter(lambda x: x.inode_number != 0, directory.entries):
            if not entry.content.name:
                longname = self.get_longname(entry.content.index)
                entry.content._m_name = longname.name
                entry.length = longname.length
            valid_entries.append(entry)

        directory.entries = valid_entries
        return directory

    def read_dir(self, inode_number):
        """Read raw directory content from its inode number.

        Args:
            inode_number (int): Inode number of the directory.

        Returns:
            bytes: Raw directory content.
        """
        assert inode_number >= 1, "Inode number smaller than 1 not allowed!"
        dir_inode = self.get_inode(inode_number)
        assert stat.S_ISDIR(dir_inode.mode), "Inode is not a directory!"
        dir_raw = self.read_file(dir_inode)

        return dir_raw

    def get_inode(self, inode_number):
        """Retrieve inode from its inode number.

        Args:
            inode_number (int): Inode number of the directory.

        Returns:
            Parser.Inode: Parsed inode.
        """
        # inode_number 1 is the root ("/") directory
        assert inode_number >= 1, "Inode number smaller than 1 not allowed!"

        inode_raw = self.read_file(
            self.active_superblock.inodes,
            offset=(inode_number - 1) * self.parser.sizeof_inode,
            size=self.parser.sizeof_inode,
        )

        return self.parser.Inode(KaitaiStream(BytesIO(inode_raw)), _root=self.parser._root)

    def read_file(self, inode, offset=0, size=None):
        """Read raw content from an inode.

        Args:
            inode (Parser.Inode): Inode number of the directory.
            offset (int): starting offset in file.
            size (int): size of content to be read.

        Returns:
            bytes: Raw inode content.
        """
        if size is None:
            size = inode.size - offset
        elif offset + size > inode.size:
            size = inode.size - offset
        # assert (offset <= inode.size and size <= inode.size - offset), 'Attempting to read beyond file size!'

        file_content = b""
        o = offset
        while (len(file_content) - offset % self.blocksize) < size:
            file_content += self.parse_block_pointer(inode, o).raw_body
            o += self.blocksize

        return file_content[offset % self.blocksize : offset % self.blocksize + size]

    def parse_block_pointer(self, inode, offset):
        """Get pointer to the data of the inode on the given offset.

        The inodes have space for 16 pointers to data blocks. When these file size is larger than
        16 blocks, the file system uses a layered method. The initial 16 pointers point to a block
        of pointers that point to data blocks (level 1). Level 0 is when the 16 pointers directly
        point to data blocks. The maximum level for an inode is 2.

        Args:
            inode (Parser.Inode): Inode object.
            offset: offset in the content of the inode.

        Returns:
            Parser.BlockPointer: Pointer to the data block at the given offset.
        """

        def bytes_in_unit(level):
            return self.blocksize * (self.blocksize // 4) ** (inode.level - level)

        idx = offset // bytes_in_unit(0)
        pointer = inode.pointers[idx]

        for lvl in range(inode.level):
            offset = offset % bytes_in_unit(lvl)
            idx = offset // bytes_in_unit(lvl + 1)
            pointer = pointer.body_as_pointer_list[idx]

        return pointer

    def check_superblock_crc(self):
        """Assert superblock integrity."""
        superblock0 = {
            "raw": self.parser.qnx6_bootblock.superblock0_raw,
            "object": self.parser.qnx6_bootblock.superblock0,
        }
        superblock1 = {
            "raw": self.parser.qnx6_bootblock.superblock1_raw,
            "object": self.parser.qnx6_bootblock.superblock1,
        }

        crc32_func = crcmod.mkCrcFun(0x104C11DB7, initCrc=0, rev=False)

        for superblock in [superblock0, superblock1]:
            assert len(superblock["raw"]) == 512, "Incorrect superblock size!"
            assert superblock["object"].crc == crc32_func(superblock["raw"][8:]), "Incorrect superblock CRC!"
