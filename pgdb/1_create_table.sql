\connect pspace

CREATE TABLE definition_sources (
    word text PRIMARY KEY,
    src text
);

GRANT ALL PRIVILEGES ON definition_sources TO pspace;
