import logging
import subprocess
import sys
from getpass import getuser
from pathlib import Path
from socket import gethostname

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata  # https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def setup_logging(logger, loglevel=logging.INFO):
    logger.setLevel(loglevel)
    logger.addHandler(get_console_handler())
    # logger.propagate = False

    logger.info("Logging started")
    logger.info("Python version: %s", sys.version)
    logger.info("Script started by %s on %s", getuser(), gethostname())
    logger.info("Called with sys.argv:\n %s", " ".join(sys.argv))
    version = get_version()
    if version is not None:
        logger.info("Current qnxmount version: %s", version)
        return logger

    rev_hash = get_git_revision_hash(Path(sys.argv[0]).parent)
    if rev_hash:
        logger.info("Current commit hash: %s", rev_hash)
    else:
        logger.warning("This script is not in a git repository!")

    return logger


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_version():
    try:
        return metadata.version("qnxmount")
    except (ModuleNotFoundError, metadata.PackageNotFoundError) as e:
        return None


def get_git_revision_hash(git_dir):
    try:
        output = subprocess.check_output(["git", "-C", str(git_dir), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return output.decode("utf8").rstrip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None
