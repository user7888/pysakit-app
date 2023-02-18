DROP TABLE IF EXISTS stops_new, stops, users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT
);

CREATE TABLE stops (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT,
    hsl_code TEXT, 
    name TEXT, 
    owner INTEGER REFERENCES users, 
    visible BOOLEAN
);