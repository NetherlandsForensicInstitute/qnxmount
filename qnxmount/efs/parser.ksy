meta:
  id: parser
  title: efs_parser
  endian: le
  bit-endian: le
  xref: 
    headers: 'https://github.com/RunZeJustin/qnx660/blob/47c4158e3993d7536170b649e6c1e09552318fb4/target/qnx6/usr/include/fs/f3s_spec.h'

instances:
  unit_size:
    value: unit_shortcut.unit_size
  unit_shortcut:
    pos: 0
    type: unit_info
    doc: Needed for bootstrapping the unit size value.
  units:
    type: units(1,1)
    doc: Dummy values to satisfy the compiler, we will manually instantiate it anyway.

types:
  units:
    params:
      - id: align_pow2
        type: u4
      - id: num_units
        type: u4
    seq:
      - id: unit_list
        size: _root.unit_size
        type: unit
        repeat: expr
        repeat-expr: num_units

  unit:
    instances:
      raw:
        pos: 0
        size: _root.unit_size
      extents:
        type: extent(_index)
        repeat: until
        repeat-until: '_.header.status0.ext_last'  # F3S_EXT_LAST
      info:
        value: extents[0].special_text.body
      logi:
        value: extents[1].special_text.body
#      boot:
#        value: extents[2].special_text.body
#      root:
#        value: extents[3].special_text.body
#      first:
#        value: extents[4].special_text.body

  extent:
    params:
      - id: i
        type: u4
    instances:
      header:
        pos: _root.unit_size - sizeof<extent_header> * (i + 1)
        size: sizeof<extent_header>
        type: extent_header
      text_offset:
        value: '((header.text_offset_hi << 16) + header.text_offset_lo) << _parent._parent.align_pow2'
      text:
        pos: text_offset
        size: header.text_size
      special_text:
        pos: text_offset
        size: header.text_size
        type: special_extent_p(i)
      as_dir_entry:
        pos: text_offset
        size: header.text_size
        type: dir_entry

  special_extent_p:
    params:
      - id: idx
        type: u4
    seq:
      - id: body
        type:
          switch-on: idx
          cases:
            0 : unit_info
            1 : unit_logi
            2 : boot_info
            3 : dir_entry
            4 : dir_entry
        doc: Can not cast index to enum

  extent_header:
    seq:
      - id: status0
        type: header_status
      - id: status1
        type: u4
      - id: status2
        type: u4
      - id: ecc
        size: 6
      - id: reserve
        contents: [0xff]
      - id: text_offset_hi
        type: u1
      - id: text_offset_lo
        type: u2
      - id: text_size
        type: u2
      - id: next
        type: extent_ptr
      - id: super
        type: extent_ptr

  header_status:
    seq:
      - id: no_write
        type: b1
      - id: no_next
        type: b1
      - id: no_super
        type: b1
      - id: no_split
        type: b1
      - id: condition
        type: b3
      - id: ext_last
        type: b1
      - id: type
        type: b2
      - id: basic
        type: b1
      - id: pad
        type: b21 # 5 + 16
    instances:
      is_file:
        value: 'type == 3'  # F3S_EXT_FILE
      is_dir:
        value: 'type == 2'  # F2S_EXT_DIR
      is_sys:
        value: 'type == 1'  # F2S_EXT_SYS

  extent_ptr:
    seq:
      - id: logi_unit
        type: u2
      - id: index
        type: u2
  
  unit_info:
    seq: 
      - id: struct_size
        type: u2
      - id: endian
        size: 1
      - id: pad
        contents: [0xff]
      - id: unit_pow2
        type: u2
      - id: reserve
        contents: [0xff, 0xff]
      - id: erase_count
        type: u4
      - id: boot
        type: extent_ptr
    instances:
      unit_size:
        value: 1 << unit_pow2

  unit_logi:
    seq:
      - id: struct_size
        type: u2
      - id: logi
        type: u2
      - id: age
        type: u4
      - id: pad
        size: struct_size - 0x18
        doc: Default struct size is 0x18.
      - id: md5
        size: 16

  boot_info:
    seq:
      - id: struct_size
        type: u2
      - id: rev_major
        type: u1
      - id: rev_minor
        type: u1
      - id: sig
        contents: 'QSSL_F3S'
      - id: unit_index
        type: u2
      - id: unit_total
        type: u2
      - id: unit_spare
        type: u2
      - id: align_pow2
        type: u2
      - id: root
        type: extent_ptr
    instances:
      is_valid:
        value: 'struct_size == 0x18 and rev_major == 3 and rev_minor == 0'

  stat:
    seq:
      - id: struct_size
        type: u2
      - id: mode
        type: u2
      - id: uid
        type: u4
      - id: gid
        type: u4
      - id: mtime
        type: u4
      - id: ctime
        type: u4

  dir_entry:
    seq:
      - id: struct_size
        type: u2
      - id: moves
        type: u1
      - id: namelen
        type: u1
      - id: first
        type: extent_ptr
      - id: name
        type: strz
        encoding: UTF-8
      - id: name_pad
        size: '((namelen + 3) & 0b11111100) - namelen'
        doc: Name with padding is 4-byte aligned.
      - id: stat
        type: stat
