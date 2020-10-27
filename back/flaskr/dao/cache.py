from .util import do_nothing

class Cache:
    key_src = "src"
    key_processed = "proc"
    key_raw = "raw"

    def __init__(self, client):
        self.client = client

    def _get(self, hsh, key):
        r = self.client.hget(hsh, key)
        if r is not None:
            if isinstance(r, bytes):
                r = r.decode("utf8")
            return r

    def _set(self, hsh, key, val):
        return self.client.hset(hsh, key, val)

    def get_src(self, word):
        return self._get(word, self.key_src)

    def set_src(self, word, src):
        return self._set(word, self.key_src, src)

    def get_processed(self, word):
        return self._get(word, self.key_processed)

    def set_processed(self, word, processed):
        return self._set(word, self.key_processed, processed)

    def get_raw(self, word):
        return self._get(word, self.key_raw)

    def set_raw(self, word, raw):
        return self._set(word, self.key_raw, raw)


class DummyCache:
    def __init__(self):
        for key in ("src", "processed", "raw"):
            setattr(self, f"get_{key}", do_nothing)
            setattr(self, f"set_{key}", do_nothing)

