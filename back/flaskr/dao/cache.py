from .util import do_nothing
from typing import Iterator
import json
import time
import functools


def _decode(val):
    """ bytes -> 'decoded str', * -> * """
    if val is not None:
        if isinstance(val, bytes):
            return val.decode("utf8")
        return val


def record_access(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        self._last_access = time.perf_counter()
        return f(self, *args, **kwargs)
    return wrapper


class Cache:
    key_src = "src"
    key_processed = "proc"
    key_raw = "raw"

    def __init__(self, client):
        self.client = client
        self._last_access = time.perf_counter()

    @property
    def last_access(self):
        return self._last_access

    def elapsed_since_last_access(self) :
        return time.perf_counter() - self._last_access

    @record_access
    def _get(self, hsh, key):
        return _decode(self.client.hget(hsh, key))

    @record_access
    def _mget(self, hsh, keys) -> Iterator:
        return map(_decode, self.client.hmget(hsh, keys))

    def _set(self, hsh, key, val):
        return self.client.hset(hsh, key, val)

    def get_src(self, word):
        return self._get(word, self.key_src)

    def set_src(self, word, src):
        return self._set(word, self.key_src, src)

    def get_processed(self, word):
        result = self._get(word, self.key_processed)
        if result is not None:
            return json.loads(result)

    def set_processed(self, word, processed):
        processed = json.dumps(processed)
        return self._set(word, self.key_processed, processed)

    def get_raw(self, word):
        return self._get(word, self.key_raw)

    def set_raw(self, word, raw):
        return self._set(word, self.key_raw, raw)

    def get_both(self, word):
        """-> (raw, processed)"""
        r, p =  self._mget(word, (self.key_raw, self.key_processed))
        if p is not None:
            p = json.loads(p)
        return r, p



class DummyCache:
    def __init__(self):
        for key in ("src", "processed", "raw"):
            setattr(self, f"get_{key}", do_nothing)
            setattr(self, f"set_{key}", do_nothing)

