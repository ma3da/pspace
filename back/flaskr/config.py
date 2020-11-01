# Config is loaded at start.
import sssml
import os
import logging

logger = logging.getLogger(__name__)
_CONFIG = {}


def _read_env(pfx="_PSPACE"):
    return {k[len(pfx):]: v for k, v in os.environ.items() if k.startswith(pfx)}


def _read_file(fp):
    with open(fp) as f:
       return sssml.load(f)


def load_config(fp=None):
    logger.info(f"loading conf from {os.path.abspath(fp)}")
    if fp:
        _CONFIG.update(_read_file(fp))
    _CONFIG.update(_read_env())


def get(key, default=None, _raise=False):
    """Returns value for key in global config.
    :default: Value to be returned if key is missing.
    :_raise: Raise an error if key is missing.
    """
    if _raise:
        try:
            return _CONFIG[key]
        except KeyError:
            raise KeyError(f"{key} not found in global config.")

    return _CONFIG.get(key, default)
