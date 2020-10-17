\connect pspace

CREATE TABLE users (
    uid text PRIMARY KEY,
    password text
);

GRANT ALL PRIVILEGES ON users TO pspace;
