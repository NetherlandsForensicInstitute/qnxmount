from pathlib import Path
from stat import S_ISDIR, S_ISLNK, S_ISREG, S_ISFIFO, S_ISCHR, S_ISBLK


def test_compare_parsing_of_image_with_tar(efs_image, efs_tar):
    for member in efs_tar.getmembers():
        dir_entry = efs_image.get_dir_entry_from_path(Path(member.name))
        
        assert_attributes_equal(member, dir_entry)
        if member.isreg():  # for regular files check if contents equal
            assert efs_tar.extractfile(member).read() == efs_image.read_file(dir_entry)
    
        
def assert_attributes_equal(tar_entry, image_entry):
    assert tar_entry.mode & 0o7777 == image_entry.stat.mode & 0o7777
    assert tar_entry.mtime == image_entry.stat.mtime
    assert tar_entry.uid == image_entry.stat.uid
    assert tar_entry.gid == image_entry.stat.gid
    assert tar_entry.isdir() == S_ISDIR(image_entry.stat.mode)
    assert tar_entry.issym() == S_ISLNK(image_entry.stat.mode)
    assert tar_entry.isreg() == S_ISREG(image_entry.stat.mode)
    assert tar_entry.isfifo() == S_ISFIFO(image_entry.stat.mode)
    assert tar_entry.isblk() == S_ISBLK(image_entry.stat.mode)
    assert tar_entry.ischr() == S_ISCHR(image_entry.stat.mode)

