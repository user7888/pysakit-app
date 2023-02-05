CREATE TABLE stops_new (id SERIAL PRIMARY KEY, hsl_id TEXT, owner TEXT, visible BOOLEAN);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);