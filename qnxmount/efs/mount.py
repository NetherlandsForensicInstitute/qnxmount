import errno
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict

from fuse import FUSE, FuseOSError, Operations

from qnxmount.efs.interface import EFS, scan_partitions

LOGGER = logging.getLogger(__name__)


class FuseEFS(Operations):
    """Fuse implementation of the EFS file system.

    Args:
        partitions (Dict[Path, EFS]): Dictionary of efs partitions
        fuse_mount_point (Path): Mount point of FUSE on the host OS.
        mount_point_dir_entries (Dict[Path, set]): Dictionary for paths contained in the
            mount point path of the partitions.
    """

    def __init__(self, partitions: Dict[Path, EFS], fuse_mount_point: Path):
        self.partitions = partitions
        self.fuse_mount_point = fuse_mount_point
        self.mount_point_dir_entries = self.build_dir_entry_tree()

    def build_dir_entry_tree(self):
        """Build a default tree for the dummy directory entries on the hard coded mount path to a partition.

        Returns:
            Dict[Path, set]: Dictionary with directory entries.
        """
        tree = defaultdict(set)
        for mount_point in self.partitions:
            path = mount_point
            while path.name:
                tree[path.parent].add(path.name)
                path = path.parent
        return tree

    def get_partition_mount_point(self, path):
        """Get mount point of the file system partition from a given path.

        Args:
            path (Path): Path in the file system.

        Returns:
            Path: Mount point of the partition.
        """
        for mount_point in self.partitions:
            if mount_point in path.parents or path == mount_point:
                return mount_point
        return None

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

        """
        Check if path is a valid prefix of a hard coded mount point.
        If so, return dummy attributes derived from the hosts mount point.
        """
        if path in self.mount_point_dir_entries:
            st = os.lstat(self.fuse_mount_point.parent)
            return dict(
                (key, getattr(st, key))
                for key in ("st_atime", "st_ctime", "st_gid", "st_mode", "st_mtime", "st_nlink", "st_size", "st_uid")
            )

        partition_mount_point = self.get_partition_mount_point(path)
        if partition_mount_point is not None:
            path = path.relative_to(partition_mount_point)
            partition = self.partitions[partition_mount_point]
            dir_entry = partition.get_dir_entry_from_path(path)
            if dir_entry:
                return dict(
                    st_size=len(partition.read_file(dir_entry)),
                    st_nlink=1,
                    st_mode=dir_entry.stat.mode,
                    st_ctime=dir_entry.stat.ctime,
                    st_mtime=dir_entry.stat.mtime,
                    st_uid=dir_entry.stat.uid,
                    st_gid=dir_entry.stat.gid,
                )

        raise FuseOSError(errno.ENOENT)

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

        """
        Check if path is a valid prefix of a hard coded mount point.
        If so, return the correct directory entries.
        """
        if path in self.mount_point_dir_entries:
            for entry in self.mount_point_dir_entries[path]:
                yield entry

        else:
            partition_mount_point = self.get_partition_mount_point(path)
            if partition_mount_point is not None:
                path = path.relative_to(partition_mount_point)
                partition = self.partitions[partition_mount_point]
                dir_entry = partition.get_dir_entry_from_path(path)
                for entry in partition.read_dir(dir_entry):
                    yield entry.name

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
        mountpoint = self.get_partition_mount_point(path)
        if mountpoint is None:
            return b""
        path = path.relative_to(mountpoint)
        partition = self.partitions[mountpoint]
        dir_entry = partition.get_dir_entry_from_path(path)
        return partition.read_file(dir_entry)[offset : offset + size]

    def readlink(self, path):
        """Read content from a link given the path.

        Args:
            path (Path): Path to symlink.

        Returns:
            str: symlink target
        """
        LOGGER.debug(f"readlink({path})")
        path = Path(path)
        mountpoint = self.get_partition_mount_point(path)
        if mountpoint is None:
            raise FuseOSError(errno.ENOENT)
        path = path.relative_to(mountpoint)
        partition = self.partitions[mountpoint]
        dir_entry = partition.get_dir_entry_from_path(path)
        return partition.read_file(dir_entry).decode("utf-8")


def initialise_fuse_efs(image, mount_point):
    """Initialise the FuseEFS object.

    Args:
        image (Path): Path to the image.
        mount_point (Path): Path to the mount point on the host system.

    Returns:
        FuseEFS: FuseEFS object.
    """
    partitions = dict()
    for partition in scan_partitions(image):
        mount_path = Path(partition.root.name)
        if not mount_path.is_absolute():
            mount_path = Path("/") / mount_path
        partitions[mount_path] = partition

    return FuseEFS(partitions, mount_point)


def mount(image, mount_point):
    efs = initialise_fuse_efs(image, mount_point)
    FUSE(efs, str(mount_point), nothreads=True, foreground=True)
