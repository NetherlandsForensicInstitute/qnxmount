from pathlib import Path
from qnxmount.etfs.parser import Parser
from functools import lru_cache
from collections import defaultdict
import logging

LOGGER = logging.getLogger(__name__)


class ETFS:
    """This class implements the basic functionality to create a Kaitai io stream.

    Args:
        stream: Kaitaistream containing the qnx6 file system.
        pagesize (int): page size.

    Attributes:
        stream: Kaitaistream containing the qnx6 file system.
        parser (Parser): Parser class automatically generated from .ksy file.
        page_size (int): page size.
        current_pages: 
        ftable: File table of the file system.
        dir_tree: Directory tree of the file system.
        path_to_fid: Dictionary to map a file path to a fid.
    """
    def __init__(self, stream, pagesize=2048):
        self.stream = stream
        self.parser = Parser(self.stream)

        transaction_size = 16
        self.page_size = pagesize
        assert self.stream._io.size() % (pagesize + transaction_size) == 0, 'size of memory map invalid'
        num_pages = self.stream._io.size() // (pagesize + transaction_size)
        self.parser._m_pages = self.parser.Pages(pagesize, num_pages, self.parser._io, _root=self.parser)
        self.current_pages = self.get_current_file_pages()

        self.ftable = self.build_ftable()
        self.set_full_file_names()
        self.dir_tree = self.build_dir_tree()

        self.path_to_fid = {self.get_path(fid): fid for fid, entry in enumerate(self.ftable) if ((entry is not None) and (entry.full_name is not None))}

    def read_dir(self, path):
        return self.dir_tree[path]

    def build_dir_tree(self):
        tree = defaultdict(set)
        for fid, entry in enumerate(self.ftable):
            if entry is None or entry.full_name is None:
                continue
            path = self.get_path(fid)
            if fid != 0:
                tree[path.parent].add(fid)
        return tree

    @lru_cache(maxsize=128)
    def get_path(self, fid: int):
        if fid == 0:
            return Path('/')

        entry = self.ftable[fid]
        if self.ftable[entry.pfid] is None:
            parent_path = Path('/recovered_files')
        else:
            parent_path = self.get_path(entry.pfid)
        return parent_path / Path(entry.full_name)

    @lru_cache(maxsize=256)
    def read_file(self, fid):
        current_pages = self.current_pages[fid]
        data = b''
        for cluster in range(0 if not current_pages else max(current_pages) + 1):
            if cluster not in current_pages:
                LOGGER.warning(f"cluster {cluster} not found for {self.get_path(fid)} (fid {fid}). Replaced with 0xff.")
                data += b'\xff' * self.page_size
            else:
                data += current_pages[cluster].data.raw
        return data

    def set_full_file_names(self):
        for fid, entry in enumerate(self.ftable):
            if entry is None:
                continue
            if entry.is_extension or not entry.is_valid:
                entry._m_full_name = None

            elif entry.is_solo:
                entry._m_full_name = entry.body.name

            else:
                if self.ftable[entry.efid] is not None:
                    extension = self.ftable[entry.efid]
                    assert extension.is_extension
                    assert extension.pfid == fid
                    entry._m_full_name = entry.body.name + extension.body.name
                else:
                    entry._m_full_name = entry.body.name

    def get_current_file_pages(self):
        pages = defaultdict(lambda: defaultdict(lambda: defaultdict(None)))
        for page in self.parser.pages.pages:
            transaction = page.transaction
            if transaction.fid == 0xffff:
                continue
            pages[transaction.fid][transaction.cluster][transaction.sequence] = page

        for fid, clusters in pages.items():
            for cluster, sequences in clusters.items():
                # assume that for equal sequences the one with the highest offset is the most recent one
                # not sure if correct
                pages[fid][cluster] = sequences[max(sequences)]

        return pages

    def build_ftable(self):
        ftable = []
        ftable_pages = self.current_pages[self.parser.fid_ftable]
        for cluster in range(max(ftable_pages) + 1):
            if cluster not in ftable_pages:
                for _ in range(self.page_size // 64):
                    ftable.append(None)
                continue
            page = ftable_pages[cluster]
            for entry in page.data.as_ftable.entries:
                ftable.append(entry)
        return ftable

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('image', type=Path, help='Path to EFS binary')
    parser.add_argument('-s', '--page_size', type=lambda x: int(x, 0), help='Size of pages (clusters)', default=2048)
    args = parser.parse_args()

    etfs = ETFS(args.image, 0, args.page_size)

    exit(0)


