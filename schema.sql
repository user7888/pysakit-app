DROP TABLE IF EXISTS stops_new, stops, users, routes, stops_and_users, routes_and_stops;

CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT
);

CREATE TABLE stops (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT UNIQUE,
    hsl_code TEXT, 
    name TEXT, 
    description TEXT
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT UNIQUE,
    short_name TEXT,
    long_name TEXT,
    mode TEXT
);

CREATE TABLE stops_and_users (
    id SERIAL PRIMARY KEY, 
    stop_id INTEGER REFERENCES stops,
    user_id INTEGER REFERENCES users, 
    visible BOOLEAN
);

CREATE TABLE routes_and_stops (
    id SERIAL PRIMARY KEY, 
    stop_id INTEGER REFERENCES stops, 
    route_id INTEGER REFERENCES routes
);



