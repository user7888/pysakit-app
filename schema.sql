DROP TABLE IF EXISTS stops, users, routes, stops_and_users, routes_and_stops, transport_categories;

CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT
);

CREATE TABLE transport_categories (
    id SERIAL PRIMARY KEY, 
    category TEXT
);

CREATE TABLE stops (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT UNIQUE,
    hsl_code TEXT, 
    name TEXT, 
    description TEXT,
    category_id INTEGER REFERENCES transport_categories
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY, 
    hsl_id TEXT UNIQUE,
    short_name TEXT,
    long_name TEXT,
    category_id INTEGER REFERENCES transport_categories
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

INSERT INTO transport_categories (category) VALUES
('BUS'),
('TRAM'),
('SUBWAY'),
('RAIL'),
('FERRY');