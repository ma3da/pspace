import sqlalchemy
from sqlalchemy.sql import select, insert, update
from flaskr.tables import DEF_SRC


class DefinitionSrcDao:
    """ Record structure: (word, src) """

    def __init__(self, dbname, user, pwd, host=None, port=None):
        self.dbname = dbname
        self.engine = sqlalchemy.create_engine(
            f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}")

    def get(self, word):
        """Returns the src for word if present, or None.

        Error if more than one record found.
        """
        with self.engine.connect() as conn:
            s = select([DEF_SRC.c.src]).where(DEF_SRC.c.word == word)
            result = conn.execute(s)
            row = result.fetchone()
            if row is not None:
                return row[0]

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

    def close(self):
        self.engine.dispose()


class DummyDao:
    def get(self, *a, **ka):
        return None

    def write(self, *a, **ka):
        pass

    def close(self):
        pass
