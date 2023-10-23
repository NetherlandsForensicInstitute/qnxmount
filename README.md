# QNX Filesystems Mounter

## Project Discription

This project contains code to parse and mount (read only) QNX filesystems in non-standard images (HDD / SSD / eMMC).

Existing tools were not able to handle the exotic configurations of some of the filesystems that we encountered in vehicle forensics, for instance on blocksizes greater than 4K on qnx6 filesystems, or non-standard allignment on qnx efs filesystems.

The description of the binary data structure of these filesystems is done with [kaitai](https://kaitai.io/) and this description can be found in the `.ksy` files in the folders for each respective qnx filesystem ([qnx6](qnxmount/qnx6/parser.ksy), [etfs](qnxmount/etfs/parser.ksy), and [efs](qnxmount/efs/parser.ksy)). With Kaitai, a Python based parser was generated. Mounting with these parsers is based on fuse.

This project is only tested on Linux machines. 


## Getting started

Set up your Python virtual environment and activate the environment:
```commandline
python3 -m venv venv
source ./venv/bin/activate
```
Install qnxmount and fuse in the virtual environment:
```commandline
pip install qnxmount
sudo apt install fuse
```

<!-- Or clone this repo and install.
```commandline
pip install .
``` -->


## Usage

General use of the module is as follows:
```shell
python3 -m qnxmount {fs_type} [options] /image /mountpoint
```
where `fs_type` is the filesystem type (qnx6, etfs, or efs) and options are the options for that filesystem type.

The options are different for each filesystem type. An overview is given below. For more information use the help option. 
```shell
python3 -m qnxmount qnx6 [-o OFFSET] /image /mountpoint
python3 -m qnxmount etfs [-o OFFSET] [-s PAGE_SIZE] /image /mountpoint
python3 -m qnxmount efs /image /mountpoint
```

Note that the offset and page size can be entered in decimal, octal, binary, or hexadecimal format. For example, we can mount an image with a qnx6 filesystem at offset 0x1000 with:
```shell
python3 -m qnxmount qnx6 -o 0x1000 /image /mountpoint 
```
Using the option `-o 4096` would give the same result.

If mounting succeeds you will see the log message `"Mounting image /image on mount point /mountpoint"` appear and the process will hang. Navigate to the given mount point with another terminal session or a file browser to access the file system.

Unmounting can be done from the terminal with:
```shell
sudo umount /mountpoint
```
The logs will show show that the image was successfully unmounted and qnxmount will exit.

## Contributing and Testing

If you want develop the tool and run tests, first fork the repository. Contributions can be submitted as a merge request. 

To get started clone the forked repository and create a virtual environment. Install the test dependencies and fuse into the environment.
```commandline
pip install .[test]
sudo apt install fuse
```

The folder **tests** contains functional tests to test the different parsers.
To run these tests you need a file system image and an accompanying tar archive.
The tests run are functional tests that check whether the parsed data from the test image is equal to the data stored in the archive.
Default test_images are located in the folders **test_data**.
If you want to test your own image replace the files **test_image.bin** and **test_image.tar.gz** with your own.

A test image can be created by running the script `make_test_fs.sh` inside a QNX Virtual Machine.
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
