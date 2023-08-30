import tarfile
from pathlib import Path
from stat import S_ISBLK, S_ISCHR, S_ISDIR, S_ISFIFO, S_ISLNK, S_ISREG

from qnxmount.qnx6.interface import QNX6FS
from qnxmount.stream import Stream


def test_compare_parsing_of_image_with_tar(image_path, tar_path):
    with Stream(image_path) as stream, tarfile.open(tar_path) as qnx6_tar:
        qnx6_image = QNX6FS(stream)
        for member in qnx6_tar.getmembers():
            inode_number = qnx6_image.get_inode_number_from_path(Path(member.name))
            inode = qnx6_image.get_inode(inode_number)

            assert_inode_contents_equal(member, inode)
            if member.isreg():  # for regular files check if contents equal
                assert qnx6_tar.extractfile(member).read() == qnx6_image.read_file(inode)


def assert_inode_contents_equal(tar_inode, image_inode):
    assert tar_inode.uid == image_inode.uid
    assert tar_inode.gid == image_inode.gid
    assert tar_inode.mtime == image_inode.mtime
    assert tar_inode.isdir() == S_ISDIR(image_inode.mode)
    assert tar_inode.issym() == S_ISLNK(image_inode.mode)
    assert tar_inode.isreg() == S_ISREG(image_inode.mode)
    assert tar_inode.isfifo() == S_ISFIFO(image_inode.mode)
    assert tar_inode.isblk() == S_ISBLK(image_inode.mode)
    assert tar_inode.ischr() == S_ISCHR(image_inode.mode)
    """
    Mode bits are saved differently in tar files than in regular inodes.
    The permission, setuid, setgid and reserved bits are masked when the mode is saved to tar.
    The other bits (such as whether the file is a directory) are saved elsewhere.
    Directly comparing the modes would therefore result in an assertion error.
    To account for this the mode bits are masked with 0o7777.
    For more info on how tar saves mode bits see https://www.gnu.org/software/tar/manual/html_node/Standard.html
    and for qnx6 https://www.qnx.com/developers/docs/7.1/#com.qnx.doc.neutrino.lib_ref/topic/s/stat_struct.html.
    """
    assert tar_inode.mode & 0o7777 == image_inode.mode & 0o7777  # permissions, setuid, setgid, reserved bit


def test_read_file_on_large_regular_file(image_path, tar_path):
    with Stream(image_path) as stream, tarfile.open(tar_path) as qnx6_tar:
        qnx6_image = QNX6FS(stream)

        for member in qnx6_tar.getmembers():
            if member.isreg() and member.size > qnx6_image.blocksize:
                inode_number = qnx6_image.get_inode_number_from_path(Path(member.name))
                inode = qnx6_image.get_inode(inode_number)

                offset = max(17, member.size % qnx6_image.blocksize)

                def tar_raw_bytes(o, s):
                    return qnx6_tar.extractfile(member).read()[o : o + s]

                def image_raw_bytes(o, s):
                    return qnx6_image.read_file(inode, offset=o, size=s)

                assert tar_raw_bytes(offset, qnx6_image.blocksize) == image_raw_bytes(offset, qnx6_image.blocksize)
                assert tar_raw_bytes(0, offset) == image_raw_bytes(0, offset)
                assert tar_raw_bytes(offset, qnx6_image.blocksize - offset) == image_raw_bytes(offset, qnx6_image.blocksize - offset)
                assert tar_raw_bytes(offset, offset) == image_raw_bytes(offset, offset)
