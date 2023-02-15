DROP TABLE IF EXISTS stops_new, users;
CREATE TABLE stops_new (id SERIAL PRIMARY KEY, hsl_id TEXT, name TEXT, owner TEXT, visible BOOLEAN);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);