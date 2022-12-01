from pathlib import Path
from stat import S_ISDIR, S_ISLNK, S_ISREG, S_ISFIFO, S_ISCHR, S_ISBLK


def test_compare_parsing_of_image_with_tar(etfs_image, etfs_tar):
    for member in etfs_tar.getmembers():
        path = Path(member.name)
        if not path.is_absolute():
            path = Path('/') / path
        fid = etfs_image.path_to_fid[path]
        dir_entry = etfs_image.ftable[fid]

        assert_attributes_equal(member, dir_entry)
        if member.isreg():  # for regular files check if contents equal
            assert etfs_tar.extractfile(member).read() == etfs_image.read_file(fid)[:dir_entry.body.size]


def assert_attributes_equal(tar_entry, image_entry):
    assert tar_entry.mode & 0o7777 == image_entry.body.mode & 0o7777
    assert tar_entry.mtime == image_entry.body.mtime
    assert tar_entry.uid == image_entry.body.uid
    assert tar_entry.gid == image_entry.body.gid
    assert tar_entry.isdir() == S_ISDIR(image_entry.body.mode)
    assert tar_entry.issym() == S_ISLNK(image_entry.body.mode)
    assert tar_entry.isreg() == S_ISREG(image_entry.body.mode)
    assert tar_entry.isfifo() == S_ISFIFO(image_entry.body.mode)
    assert tar_entry.isblk() == S_ISBLK(image_entry.body.mode)
    assert tar_entry.ischr() == S_ISCHR(image_entry.body.mode)

