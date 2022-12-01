import pytest
import tarfile
from qnxmount.qnx6.interface import QNX6FS
from pathlib import Path

@pytest.fixture(scope="session")
def qnx6_image():
    image_path = Path(__file__).parent / "test_data/test_image.bin"
    if image_path is None or not image_path.exists():
        pytest.skip()
    return QNX6FS(image_path)


@pytest.fixture(scope="session")
def qnx6_tar():
    tar_path = Path(__file__).parent / "test_data/test_image.tar.gz"
    if tar_path is None or not tarfile.is_tarfile(tar_path):
        pytest.skip()
    return tarfile.open(tar_path)


