if [ ! -e /dev/hd0t77 ]
  then
    devb-ram ram capacity=819200 &
    dinit -q -h /dev/hd0t77
    mkdir /ram
    mount /dev/hd0t77 /ram
fi

mountpoint=/etfs
# kill already running devf-ram processes
for p in $(ps -A | grep fs-etfs-ram | awk '//{print $1}')
do
  kill $p
done

# Create empty ETFS image
mketfs /tmp/etfs.bld /ram/start_image.etfs

# Start flash driver emulated in RAM
mkdir $mountpoint
fs-etfs-ram -C 1 -e -c 0 -m $mountpoint -D size=1M
etfsctl -i
etfsctl -d /dev/etfs2 -S -e -w /ram/start_image.etfs -c

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
touch this_file_is_32_characters_long_

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
rm /ram/test_image.tar
tar -czvf /ram/test_image.tar.gz *

etfsctl -d /dev/etfs2 -S -R /ram/test_image.bin -c
