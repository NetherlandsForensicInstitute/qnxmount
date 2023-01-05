import errno
import logging
from pathlib import Path

from fuse import FUSE, FuseOSError, Operations

from qnxmount.etfs.interface import ETFS
from qnxmount.stream import Stream

LOGGER = logging.getLogger(__name__)


class FuseETFS(Operations):
    """Fuse implementation of the ETFS file system.

    Args:
        stream: Kaitaistream containing the qnx6 file system.
    """

    def __init__(self, stream, pagesize):
        self.etfs = ETFS(stream, pagesize=pagesize)

    def getattr(self, path, fh=None):
        """Get directory with stat information.

        Args:
            path (Path): Path.
            fh: file handle.

        Returns:
            dict: dictionary with keys identical to the stat C structure of stat(2).
        """
        LOGGER.debug(f"getattr({path})")
        path = Path(path)

        if path not in self.etfs.path_to_fid:
            raise FuseOSError(errno.ENOENT)

        fid = self.etfs.path_to_fid[path]
        entry = self.etfs.ftable[fid]
        return dict(
            st_size=entry.body.size,
            st_nlink=1,
            st_mode=entry.body.mode,
            st_ctime=entry.body.ctime,
            st_mtime=entry.body.mtime,
            st_uid=entry.body.uid,
            st_gid=entry.body.gid,
        )

    def readdir(self, path, fh):
        """Read content from directory.

        Args:
            path (Path): Path to directory.
            fh: file handle.

        Returns:
            dict: dictionary with keys identical to the stat C structure of stat(2).
        """
        LOGGER.debug(f"readdir({path})")
        path = Path(path)

        if path in self.etfs.dir_tree:
            for fid in self.etfs.dir_tree[path]:
                entry = self.etfs.ftable[fid]
                yield entry.full_name

    def read(self, path, size, offset, fh):
        """Read content from an object.

        Args:
            path (Path): Path to object.
            size (int): size of content to be read.
            offset (int): starting offset in the file.
            fh: file handle.

        Returns:
            bytes: Raw file content.
        """
        LOGGER.debug(f"read({path}, {size}, {offset})")
        path = Path(path)

        if not path in self.etfs.path_to_fid:
            raise FuseOSError(errno.ENOENT)

        fid = self.etfs.path_to_fid[path]
        file = self.etfs.read_file(fid)
        return file[offset : offset + size]

    def readlink(self, path):
        """Read content from a link given the path.

        Args:
            path (Path): Path to symlink.

        Returns:
            str: symlink target
        """
        LOGGER.debug(f"readlink({path})")
        path = Path(path)

        if not path in self.etfs.path_to_fid:
            raise FuseOSError(errno.ENOENT)

        fid = self.etfs.path_to_fid[path]
        return self.etfs.read_file(fid).decode("utf-8")


def mount(image, mount_point, offset, pagesize):
    with Stream(image, offset) as stream:
        etfs = FuseETFS(stream, pagesize)
        FUSE(etfs, str(mount_point), nothreads=True, foreground=True)
