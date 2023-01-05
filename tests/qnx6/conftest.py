import pytest
import tarfile
from pathlib import Path

@pytest.fixture(scope="session")
def image_path():
    image_path = Path(__file__).parent / "test_data/test_image.bin"
    if image_path is None or not image_path.exists():
        pytest.skip()
    return image_path


@pytest.fixture(scope="session")
def tar_path():
    tar_path = Path(__file__).parent / "test_data/test_image.tar.gz"
    if tar_path is None or not tarfile.is_tarfile(tar_path):
        pytest.skip()
    return tar_path


