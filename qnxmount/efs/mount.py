import errno
import logging
import os
from pathlib import Path

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

    def __init__(self, partitions: list[Path, EFS], fuse_mount_point: Path):
        self.partitions = partitions
        self.fuse_mount_point = fuse_mount_point
        self.tree = self.build_dir_entry_tree()

    def build_dir_entry_tree(self):
        """Build a default tree for the dummy directory entries on the hard coded mount path to a partition.

        Returns:
            Dict[Path, set]: Dictionary with directory entries.
        """
        tree = dict()
        for partition in self.partitions:
            mountpoint = Path(partition.root.name)
            t = tree
            for path_part in mountpoint.parts[:-1]:
                if path_part not in t:
                    sub_t = dict()
                    t[path_part] = sub_t
                else:
                    sub_t = t[path_part]
                t = sub_t
            if mountpoint.parts:
                t[mountpoint.parts[-1]] = {"__parser__": partition}
            else:
                # No hardcoded mountpoint present in partition, use sane default
                t['/'] = {"__parser__": partition}
        return tree

    @staticmethod
    def _step_layer(path_part: str, layer: list):
        found_next_layer = False
        for item in layer:
            if isinstance(item, dict) and path_part in item:
                found_next_layer = True
                layer = item[path_part]
                break
        return found_next_layer, layer

    def _fake_stat(self):
        # Just return stat of actual host mountpoint
        st = os.lstat(self.fuse_mount_point.parent)
        return dict(
            (key, getattr(st, key))
            for key in (
                "st_atime",
                "st_ctime",
                "st_gid",
                "st_mode",
                "st_mtime",
                "st_nlink",
                "st_size",
                "st_uid",
            )
        )

    def _resolve(self, path: str):
        path = Path(path)
        tree = self.tree
        remaining_path = ""
        for i, part in enumerate(path.parts):
            if part in tree:
                tree = tree[part]
            else:
                remaining_path = "/".join(path.parts[i:])
                break
        return remaining_path, tree

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
        remaining_path, tree = self._resolve(path)
        if not remaining_path:
            return self._fake_stat()
        if "__parser__" in tree:
            partition = tree["__parser__"]
            dir_entry = partition.get_dir_entry_from_path(Path(f"/{remaining_path}"))
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
        remaining_path, tree = self._resolve(path)
        output = set()
        for entry, partition in tree.items():
            if entry == "__parser__" and isinstance(partition, EFS):
                dir_entry = partition.get_dir_entry_from_path(
                    Path(f"/{remaining_path}")
                )
                for e in partition.read_dir(dir_entry):
                    output.add(e.name)
            elif isinstance(partition, dict) and not remaining_path:
                output.add(entry)
        return list(output)

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
        remaining_path, tree = self._resolve(path)
        if not "__parser__" in tree:
            return b""
        partition = tree["__parser__"]
        dir_entry = partition.get_dir_entry_from_path(Path(f"/{remaining_path}"))
        if not dir_entry:
            return b""
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
        remaining_path, tree = self._resolve(path)
        if not "__parser__" in tree:
            return b""
        partition = tree["__parser__"]
        dir_entry = partition.get_dir_entry_from_path(Path(f"/{remaining_path}"))
        if not dir_entry:
            return b""
        return partition.read_file(dir_entry).decode("utf-8")


def initialise_fuse_efs(image, mount_point):
    """Initialise the FuseEFS object.

    Args:
        image (Path): Path to the image.
        mount_point (Path): Path to the mount point on the host system.

    Returns:
        FuseEFS: FuseEFS object.
    """
    partitions = list(scan_partitions(image))
    return FuseEFS(partitions, mount_point)


def mount(image, mount_point):
    efs = initialise_fuse_efs(image, mount_point)
    FUSE(efs, str(mount_point), nothreads=True, foreground=True)
