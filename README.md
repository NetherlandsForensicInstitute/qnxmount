# QNX Filesystems
QNX filesystem parsers to mount non-standard images (read only).
Mounting is based on fuse, and only tested on Linux machines.

## Getting started
Set up your python virtual environment and activate the environment:
```commandline
python3 -m venv venv
source ./venv/bin/activate
```
Install the dependencies with:
```commandline
pip install git+https://gitlab-ci-token:{token}@git.eminjenv.nl/vakgroep-automotive/filesystems-and-ftls/qnx-filesystems.git
```

Or clone and install.
```commandline
git clone git+https://gitlab-ci-token:{token}@git.eminjenv.nl/vakgroep-automotive/filesystems-and-ftls/qnx-filesystems.git
pip install .
```

## Usage
Run the parser script (used on HDD/SSD/eMMC):
```shell
python3 -m qnxmount {fs_type} [options] mountpoint image
```

For example, a specific mounter (qnx6) is called with:
```shell
python3 -m qnxmount qnx6 -o OFFSET mountpoint image
```

Now navigate to the given mount point with your favourite terminal or file browser to access the file system.

## Testing

If you want to run test, first install the test dependencies:
```commandline
pip install .[test]
```

The folder **tests** contains functional tests to test the different parsers.
To run these tests you need a file system image and an accompanying tar archive.
The tests run are functional tests that check whether the parsed data from the test image is equal to the data stored in the archive.
Default test_images are located in the folders **test_data**.
If you want to test your own image replace the files **test_image.bin** and **test_image.tar.gz** with your own.

A test image can be created by running the script `make_test_fs.sh` inside a QNX VM.
Update the script with the (edge) cases you want to check and run the command below.
This should create an _image.bin_ and _image.tar.gz_ into the specified directory.
These can be used as test files.
```shell
make_test_fs.sh /path/to/output/directory
```

To run the tests in this repo navigate to the main directory of the repo and run:
```shell
pytest
```

[//]: # (Usually, tests can be run by directly calling `pytest tests --image ... --tar ...`, however this method fails here.)
[//]: # (The reason is that the tests are located in a separate subfolder from the **qnx6_file_system.py**. )
[//]: # (The qnx6_file_system module cannot be imported because it is not located in the tests directory.)
[//]: # (When python3 is called it adds '.' to the PATH and since the qnx6_file_system module is located in the working directory they can be found.)
