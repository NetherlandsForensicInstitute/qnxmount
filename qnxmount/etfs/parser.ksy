meta:
  id: parser
  file-extension: .bin
  title: etfs_parser
  endian: le
  xref:
    header: https://github.com/RunZeJustin/qnx660/blob/47c4158e3993d7536170b649e6c1e09552318fb4/target/qnx6/usr/include/fs/etfs.h

instances:
  pages:
    pos: 0
    type: pages(2048,9)  # Dummy values to satisfy compiler, initialize later
  fid_root:
    value: 0
  fid_ftable:
    value: 1
  fid_badblks:
    value: 2
  fid_counts:
    value: 3
  fid_lostfound:
    value: 4
  fid_reserved:
    value: 5
  fid_firstfile:
    value: 6
    
types:
  pages:
    params:
      - id: pagesize
        type: u4
      - id: num_pages
        type: u4
    seq:
      - id: pages
        type: page(pagesize)
        repeat: expr
        repeat-expr: num_pages
        
  page:
    params:
      - id: pagesize
        type: u4
    seq:
      - id: data
        size: pagesize
        type: userdata
      - id: transaction
        type: transaction

  userdata:
    instances:
      as_ftable:
        pos: 0
        type: ftable
      raw:
        pos: 0
        size-eos: true

  ftable:
    seq:
      - id: entries
        type: ftable_entry
        repeat: eos
        
  transaction:
    seq:
      - id: fid		
        type: u4
        doc: File id 
      - id: cluster
        type: u4
        doc: Cluster offset in file
      - id: nclusters
        type: u2
        doc: Number of contiguous clusters for this transaction
      - id: tacode
        type: trans_code
        doc: Code for transaction area 
      - id: dacode
        type: trans_code
        doc: Code for data area
      - id: sequence
        type: u4
        doc: Sequence for this transaction
        
  trans_code:
    seq:
      - id: code
        type: u1
    instances:
      ok:
        value: code & 0x0f == 0
      ecc:
        value: code & 0x0f == 1
      erased:
        value: code & 0x0f == 2
      foxes:
        value: code & 0x0f == 3
      dataerr:
        value: code & 0x0f == 5
      deverr:
        value: code & 0x0f == 6
      badblk:
        value: code & 0x0f == 7
        
  ftable_entry:
    seq:
    - id: efid
      type: u2
      doc: File id of extra info attached to this file
    - id: pfid
      type: u2
      doc: File id of parent to this file
    - id: body
      type:
        switch-on: entry_type
        cases:
          0: file_entry
          1: extname_entry
          _: no_entry
    instances:
      is_extension:
        value: 'efid == 0x8000'
      test:
        value: '(efid & 0x8000) == 0x8000'
      has_no_parent:
        value: 'pfid == 0xffff'
        doc: These are deleted files or not-initialised entries.
      entry_type:
        value: 'is_extension.to_i + has_no_parent.to_i * 2'
        doc: Dummy variable to switch on.
      full_name:
        value: 0 # will be overwritten in code
      is_solo:
        value: 'efid == 0x0000'
      is_valid:
        value: 'efid != 0xffff' # check if true

  file_entry:
    seq:
    - id: mode
      type: u4
      doc: File mode
    - id: uid
      type: u4
      doc: User ID of owner
    - id: gid
      type: u4
      doc: Group ID of owner
    - id: atime
      type: u4
      doc: Time of last access
    - id: mtime
      type: u4
      doc: Time of last modification 
    - id: ctime
      type: u4 
      doc: Time of last change
    - id: size
      type: u4
      doc: File size (always 0 for directories) 
    - id: name
      size: 32  # ETFS_FNAME_SHORT_LEN
      type: strz
      encoding: utf-8

  extname_entry:
    seq:
      - id: name
        size: 59
        type: strz
        encoding: utf-8
      - id: type
        type: u1
    instances:
      is_valid:
        value: type == 0

  no_entry: {}
