meta:
  id: parser
  file-extension: .bin
  title: qnx6_parser
  endian: le

seq:
  - id: qnx6_bootblock
    type: bootblock

types:
  bootblock:
    seq:
      - id: magic
        contents: [0xeb, 0x10, 0x90 ,0x00]
      - id: offset_qnx6fs
        type: u4
      - id: sblk0
        type: u4
      - id: sblk1
        type: u4

    instances:
      superblock0:
        io: _root._io
        pos: sblk0*512
        type: superblock
      superblock1:
        io: _root._io
        pos: sblk1*512
        type: superblock
      superblock0_raw:
        io: _root._io
        pos: sblk0*512
        size: 512
      superblock1_raw:
        io: _root._io
        pos: sblk1*512
        size: 512

  superblock:
    seq:
      - id: magic
        contents: [0x22, 0x11, 0x19, 0x68]
      - id: crc
        type: u4
      - id: serial
        type: u8
      - id: ctime
        type: u4
      - id: atime
        type: u4
      - id: flag
        type: u4
      - id: version1
        type: u2
      - id: version2
        type: u2
      - id: volumeid
        size: 16 #check
      - id: blocksize
        type: u4
      - id: num_inodes
        type: u4
      - id: free_inodes
        type: u4
      - id: num_blocks
        type: u4
      - id: free_blocks
        type: u4
      - id: allocgroup
        type: u4
      - id: inodes
        type: rootnode
      - id: bitmap
        type: rootnode
      - id: longfile
        type: rootnode
      - id: iclaim
        type: rootnode
      - id: iextra
        type: rootnode
      - id: migrate_blocks
        type: u4
      - id: scrub_block
        type: u4
      - id: spare
        size: 32

  rootnode:
    seq:
      - id: size
        type: u8
      - id: pointers
        type: block_pointer
        repeat: expr
        repeat-expr: 16
      - id: level
        type: u1
      - id: mode
        size: 1
      - id: spare
        size: 6

  inode:
    seq:
      - id: size
        type: u8
      - id: uid
        type: u4
      - id: gid
        type: u4
      - id: ftime
        type: u4
      - id: mtime
        type: u4
      - id: atime
        type: u4
      - id: ctime
        type: u4
      - id: mode
        type: u2
      - id: ext_mode
        type: u2
      - id: pointers
        type: block_pointer
        repeat: expr
        repeat-expr: 16
      - id: level
        type: u1
      - id: status
        size: 1
      - id: unknown
        size: 2
      - id: zeros
        type: u4
        repeat: expr
        repeat-expr: 6

  block_pointer:
    seq:
      - id: ptr
        type: u4
    instances:
      raw_body:
        io: _root._io
        pos: _root.data_start + ptr * _root.blocksize
        size: _root.blocksize
      body_as_pointer_list:
        io: _root._io
        pos: _root.data_start + ptr * _root.blocksize
        type: block_pointer
        repeat: expr
        repeat-expr: _root.blocksize / 4

  directory:
    seq:
      - id: entries
        type: dir_entry
        repeat: eos

  dir_entry:
    seq:
      - id: inode_number
        type: u4
      - id: length
        type: u1
      - id: content
        size: 27
        type:
          switch-on: length
          cases:
            0xff: dir_entry_longname
            _: shortname

  dir_entry_longname:
    seq:
      - id: zeros
        size: 3
      - id: index
        type: u4
      - id: checksum
        type: u4
      - id: more_zeros
        size: 16
    instances:
      name:
        value: 0

  shortname:
    seq:
      - id: name
        type: strz
        eos-error: false
        encoding: UTF-8

  longname:
    seq:
      - id: length
        type: u2
      - id: name
        type: str
        size: length
        encoding: UTF-8


instances:
  sizeof_inode:
    value: sizeof<inode>
  blocksize:
    value: qnx6_bootblock.superblock0.blocksize
  abs_data_start_padding:
    value: '(blocksize > 0x3000) ? blocksize - 0x3000 : 0x3000 - blocksize'
    doc: Kaitai does not support abs()
  data_start:
    value: '0x3000 + ((blocksize <= 0x1000) ? 0 : abs_data_start_padding)'
    doc: 'https://github.com/RunZeJustin/qnx660/blob/47c4158e3993d7536170b649e6c1e09552318fb4/target/qnx6/usr/include/sys/fs_qnx6.h'



