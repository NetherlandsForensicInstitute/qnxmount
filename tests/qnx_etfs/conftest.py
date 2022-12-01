import pytest
import tarfile
from qnxmount.etfs.interface import ETFS
from pathlib import Path

@pytest.fixture(scope="session")
def etfs_image():
    image_path = Path(__file__).parent / "test_data/test_image.bin"
    if image_path is None or not image_path.exists():
        pytest.skip()
    return ETFS(image_path, pagesize=1024)


@pytest.fixture(scope="session")
def etfs_tar():
    tar_path = Path(__file__).parent / "test_data/test_image.tar.gz"
    if tar_path is None or not tarfile.is_tarfile(tar_path):
        pytest.skip()
    return tarfile.open(tar_path)


