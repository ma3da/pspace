CREATE USER pspace;
CREATE DATABASE pspace;

ALTER DATABASE pspace OWNER TO pspace;

\connect pspace

CREATE TABLE definition_sources (
    word text PRIMARY KEY,
    src text
);

ALTER TABLE definition_sources OWNER TO pspace;
