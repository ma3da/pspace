from sqlalchemy import Table, Column, String, MetaData

metadata = MetaData()

DEF_SRC = Table("definition_sources", metadata,
    Column("word", String, primary_key=True),
    Column("src", String),
)

USERS = Table("users", metadata,
    Column("uid", String, primary_key=True),
    Column("password", String),
)
