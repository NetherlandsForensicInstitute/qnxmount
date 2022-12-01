if [ ! -e /dev/hd0t77 ]
  then
    devb  -ram ram capacity=819200 &
    dinit -q -h /dev/hd0t77
    mkdir /ram
    mount /dev/hd0t77 /ram
fi

mountpoint=/mnt/test123

# kill already running devf-ram processes
for p in $(ps -A | grep devf-ram | awk '//{print $1}')
do
  kill $p
done

# Create empty EFS image
mkefs /tmp/efs.bld /ram/image.efs

# Start flash driver emulated in RAM, 2M size, 128k blocksize
devf-ram -s0,2M,,,128k
# Erase flash device
flashctl -p /dev/fs0 -ev
# Copy image into flash
cp -V /ram/image.efs /dev/fs0

# Start creating files 
cd $mountpoint
dd bs=1 count=16 < /dev/urandom > this_file_is_small
dd bs=4k count=16 < /dev/urandom > this_file_is_large
dd bs=1k if=/dev/urandom of=this_file_is_large seek=5 count=10 conv=notrunc
dd bs=1 count=16 < /dev/urandom > this_file_is_removed
cp this_file_is_removed this_file_is_a_copy
rm this_file_is_removed
dd bs=1 count=100 < /dev/urandom > this_file_is_not_renamed
mv this_file_is_not_renamed this_file_is_renamed
mkfifo this_is_a_fifo

mkdir directory_1
mkdir directory_2
mkdir directory_1/directory_1_1
cd directory_1/directory_1_1
echo "This is a test file system!" > message.txt
cd ..
ln -s directory_1_1/message.txt link_message.txt
dd bs=1 count=100 < /dev/urandom > this_file_is_moved
mv this_file_is_moved ../this_file_is_moved
cd ..
ln -s directory_1/link_message.txt link_link_message.txt
ln -s ../directory_2 link_directory_2

cd directory_2
touch read_only
chmod 444 read_only
touch full_permission
chmod 777 full_permission
touch standard_file
touch root_only
chmod 700 root_only
touch executable
chmod 111 executable
touch descending
chmod 764 descending
touch the_weird_one
chmod 002 the_weird_one
touch another_owner
chown nobody another_owner

cd ..
mkdir copy_of_directory_2
cp -r directory_2 copy_of_directory_2

cd $mountpoint

# For some reason tar does not play nice with efs/devf-ram when handling directories
# Manually appending everything to the tar does work
rm /ram/test_image.tar
for f in $(find | tail +1 | sed -r s:^\.\/::) 
do 
  tar rvf /ram/test_image.tar --no-recursion $f;
done
gzip /ram/test_image.tar

sync

dd if=/dev/fs0 of=/ram/test_image.bin

