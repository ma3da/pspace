from sqlalchemy.sql import select
from .tables import DEF_SRC
from .util import do_nothing


class DefinitionSrcDAO:
    """ Record structure: (word, src) """

    def __init__(self, engine, cache):
        self.engine = engine
        self.cache = cache

    def get(self, word):
        """Returns the src for word if present, or None.

        Error if more than one record found.
        """
        cached = self.cache.get_src(word)
        if cached is not None:
            return cached

        with self.engine.connect() as conn:
            s = select([DEF_SRC.c.src]).where(DEF_SRC.c.word == word)
            result = conn.execute(s)
            row = result.fetchone()
            if row is not None:
                self.cache.set_src(word, row[0])
                return row[0]

    def iter_words(self, limit=None):
        """Iterates over the words already saved.
        :limit: Stop iterating after `limit` words.
        """
        with self.engine.connect() as conn:
            s = select([DEF_SRC.c.word])
            if limit:
                s = s.limit(limit)
            result = conn.execute(s)
            for row in result:
                yield row[0]  # conn management..?

    def write(self, word, src) -> None:
        """Writes a record for word, overwriting if it already exists.
        """
        fetched = self.get(word)
        with self.engine.connect() as conn:
            if fetched is None:
                s = DEF_SRC.insert().values(word=word, src=src)
            else:
                s = (DEF_SRC.update()
                     .where(DEF_SRC.c.word == word)
                     .values(word=word, src=src))
            conn.execute(s)


class DefinitionSrcDummyDAO:
    def __init__(self, cache):
        self.cache = cache
        self.get = do_nothing
        self.write = do_nothing
