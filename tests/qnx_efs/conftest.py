import pytest
import tarfile
from qnxmount.efs.interface import scan_partitions
from pathlib import Path

@pytest.fixture(scope="session")
def efs_image():
    image_path = Path(__file__).parent / "test_data/test_image.bin"
    if image_path is None or not image_path.exists():
        pytest.skip()
    return next(scan_partitions(image_path))


@pytest.fixture(scope="session")
def efs_tar():
    tar_path = Path(__file__).parent / "test_data/test_image.tar.gz"
    if tar_path is None or not tarfile.is_tarfile(tar_path):
        pytest.skip()
    return tarfile.open(tar_path)


