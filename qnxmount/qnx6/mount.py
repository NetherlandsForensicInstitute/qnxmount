import errno
import logging
import stat
from pathlib import Path, PurePath

from fuse import FUSE, FuseOSError, Operations

from qnxmount.qnx6.interface import QNX6FS

LOGGER = logging.getLogger(__name__)


class FuseQNX6(Operations):
    """Fuse implementation of the qnx6 file system.

    Args:
        image (Path): Path to the image containing the qnx6 file system.
        offset (int): Start of the qnx6 file system in the image.
    """

    def __init__(self, image, offset):
        self.qnx6fs = QNX6FS(image, offset)

    def getattr(self, path, fh=None):
        """Get directory with inode information.

        Args:
            path (PurePath): Path to inode
            fh:

        Returns:
            dict: dictionary with keys identical to the stat C structure of stat(2).
        """
        LOGGER.debug(f"getattr({path=})")
        path = PurePath(path)
        inode_number = self.qnx6fs.get_inode_number_from_path(path)
        if inode_number is None:
            raise FuseOSError(errno.ENOENT)

        inode = self.qnx6fs.get_inode(inode_number)
        return dict(
            st_size=inode.size,
            st_nlink=1,
            st_mode=inode.mode,
            st_ctime=inode.ctime,
            st_mtime=inode.mtime,
            st_uid=inode.uid,
            st_gid=inode.gid,
        )

    def readdir(self, path, fh):
        """Read content from directory inode.

        Args:
            path (PurePath): Path to inode.
            fh: file handle.

        Returns:
            dict: dictionary with keys identical to the stat C structure of stat(2).
        """
        LOGGER.debug(f"readdir({path=})")
        path = PurePath(path)
        directory = self.qnx6fs.get_dir_from_path(path)
        for entry in directory.entries:
            yield entry.content.name

    def read(self, path, size, offset, fh):
        """Read content from an inode.

        Args:
            path (PurePath): Path to inode.
            size (int): size of content to be read.
            offset (int): starting offset in the file.
            fh: file handle.

        Returns:
            bytes: Raw inode content.
        """
        LOGGER.debug(f"read({path=}, {size=}, {offset=})")
        path = PurePath(path)
        inode_number = self.qnx6fs.get_inode_number_from_path(path)
        if not inode_number:
            raise FuseOSError(errno.ENOENT)

        inode = self.qnx6fs.get_inode(inode_number)
        if inode and stat.S_ISREG(inode.mode):
            return self.qnx6fs.read_file(inode, offset, size)
        raise FuseOSError(errno.EIO)

    def readlink(self, path):
        """Read content from a link given the path.

        Args:
            path (PurePath): Path to inode.

        Returns:
            str: symlink target
        """
        LOGGER.debug(f"readlink({path=})")
        path = PurePath(path)
        inode_number = self.qnx6fs.get_inode_number_from_path(path)
        if not inode_number:
            raise FuseOSError(errno.ENOENT)

        inode = self.qnx6fs.get_inode(inode_number)
        if inode and stat.S_ISLNK(inode.mode):
            link_raw = self.qnx6fs.read_file(inode)
            return link_raw.decode("utf8")
        raise FuseOSError(errno.ENOENT)


def mount(image, mount_point, offset):
    qnx6 = FuseQNX6(image, offset)
    FUSE(qnx6, str(mount_point), nothreads=True, foreground=True)
