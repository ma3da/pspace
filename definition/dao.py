import psycopg2


class DefinitionSrcDao:
    """ Record structure: (word, src) """

    def __init__(self, dbname, user, pwd, host=None, table_name="definition_sources"):
        self.dbname = dbname
        self.table_name = table_name
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=pwd,
                                     host=host)

    def get(self, word):
        """Returns the src for word if present, or None.

        Error if more than one record found.
        """
        with self.conn as conn:
            with conn.cursor() as cur:
                cur.execute(f"select * from {self.table_name} where word = %s",
                            (word, ))
                fetched = cur.fetchall()
        if len(fetched) > 1:
            raise ValueError(f"Expected to fetch <= 1 record for word {word}, "
                             "but got {len(fetched)}. Ids: "
                             "{list(map(operator.itemgetter(0), fetched))}")
        return fetched[0][1] if fetched else None

    def write(self, word, src) -> None:
        """Writes a record for word, overwriting if it already exists.
        """
        fetched = self.get(word)
        with self.conn as conn:
            if fetched is None:
                with conn.cursor() as cur:
                    cur.execute(f"insert into {self.table_name} (word, src) values (%s, %s);", (word, src))
            else:
                with conn.cursor() as cur:
                    cur.execute(f"update {self.table_name} set src = %s where word = %s);", (src, word))

    def close(self):
        self.conn.close()
