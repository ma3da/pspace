from .util import do_nothing
from typing import Iterator
import json


def _decode(val):
    """ bytes -> 'decoded str', * -> * """
    if val is not None:
        if isinstance(val, bytes):
            return val.decode("utf8")
        return val


class Cache:
    key_src = "src"
    key_processed = "proc"
    key_raw = "raw"

    def __init__(self, client):
        self.client = client

    def _get(self, hsh, key):
        return _decode(self.client.hget(hsh, key))

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

