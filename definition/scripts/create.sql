CREATE DATABASE pspace;
ALTER DATABASE pspace OWNER TO pspace_user;

\connect pspace

CREATE TABLE definition_sources (
    word text PRIMARY KEY,
    src text
);

ALTER TABLE definition_sources OWNER TO pspace_user;
