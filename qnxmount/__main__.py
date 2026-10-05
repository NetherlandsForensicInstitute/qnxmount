import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

import qnxmount.efs.mount as efs
import qnxmount.etfs.mount as etfs
import qnxmount.qnx6.mount as qnx6
from qnxmount.logger import setup_logging

LOGGER = logging.getLogger("qnxmount")


def mount(args):
    LOGGER.info(f"Selected mounter type: {args.type}")
    LOGGER.info(f"Mounting image {args.image} on mount point {args.mount_point}")
    if args.type == "qnx6":
        qnx6.mount(args.image, args.mount_point, args.offset)
    elif args.type == "efs":
        efs.mount(args.image, args.mount_point)
    elif args.type == "etfs":
        etfs.mount(args.image, args.mount_point, args.offset, args.page_size)
    LOGGER.info(f"Unmounting image {args.image} from mount point {args.mount_point}")


if __name__ == "__main__":
    parent_parser = ArgumentParser(description="The parent parser", add_help=False)
    parent_parser.add_argument("image", type=Path, help="Path to image containing qnx file system")
    parent_parser.add_argument("mount_point", type=Path, help="Path to mount point")

    main_parser = ArgumentParser(prog="qnxmount")
    subparsers = main_parser.add_subparsers(title="file system types", required=True, dest="type")
    parser_qnx6 = subparsers.add_parser("qnx6", parents=[parent_parser], help="Parser for HDD/eMMC images")
    parser_qnx6.add_argument(
        "-o", "--offset", type=lambda x: int(x, 0), help="Offset of qnx partition in image", default=0
    )
    parser_efs = subparsers.add_parser("efs", parents=[parent_parser], help="Parser for NOR flash images")
    parser_etfs = subparsers.add_parser("etfs", parents=[parent_parser], help="Parser for NAND flash images")
    parser_etfs.add_argument(
        "-o", "--offset", type=lambda x: int(x, 0), help="Offset of qnx partition in image", default=0
    )
    parser_etfs.add_argument(
        "-s", "--page_size", type=lambda x: int(x, 0), help="Size of pages (clusters)", default=2048
    )

    args = main_parser.parse_args()

    setup_logging(LOGGER)

    if not args.image.exists():
        LOGGER.info(f"Image file {args.image} not found, exiting.")
        sys.exit(-1)

    if not args.mount_point.exists():
        LOGGER.info(f"Mount point {args.mount_point} not found, exiting.")
        sys.exit(-2)

    sys.exit(mount(args))
