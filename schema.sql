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

CREATE TABLE routes (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT,
    short_name TEXT,
    long_name TEXT, 
);

CREATE TABLE stops_and_users (
    id SERIAL PRIMARY KEY, 
    stop INTEGER REFERENCES stops 
    user INTEGER REFERENCES users, 
    visible BOOLEAN
);

CREATE TABLE routes_and_stops (
    id SERIAL PRIMARY KEY, 
    stop INTEGER REFERENCES stops 
    route INTEGER REFERENCES routes,
);



