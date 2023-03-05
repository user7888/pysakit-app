from sqlalchemy import text
from db import db
import requests
import json

def add_routes(stop):
    # stop[0] = stop primary key
    # stop[1] = stop id for HSL api

    # Get routes related to new stop
    # from HSL api.
    query = """{
        stop(id: "HSL:"""+f'{stop[1]}"'+""") {
            name
            patterns {
                id
                code
                directionId
                headsign
                route {
                    gtfsId
                    shortName
                    longName
                    mode
                }
            }
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    stop_query = json.loads(response.text)
    categories = {'BUS': 1, 'TRAM': 2, 'SUBWAY': 3, 'RAIL': 4, 'FERRY': 5}

    # Add routes related to the newly added stop.
    routes = stop_query['data']['stop']['patterns']
    for route in routes:
        hsl_id = route['code']
        short_name = route['route']['shortName']
        long_name = route['route']['longName']
        mode = categories[route['route']['mode']]

        # Check if route already exists.
        sql = text('SELECT hsl_id FROM routes WHERE hsl_id=:hsl_id')
        result = db.session.execute(sql, {'hsl_id': hsl_id})
        found = result.fetchone()
        if found:
            continue
        
        # Insert route document into
        # database.
        sql = text('INSERT INTO routes (hsl_id, short_name, long_name, category_id) ' \
                   'VALUES (:hsl_id, :short_name, :long_name, :category_id)')
        db.session.execute(sql, {'hsl_id': hsl_id, 'short_name': short_name, 'long_name': long_name, 'category_id': mode})
        db.session.commit()
        # Update routes_and_stops table.
    add_routes_and_stops(stop, routes, hsl_id)
    return
    
def add_routes_and_stops(stop, routes, hsl_id):
    # Check if the routes_and_stops
    # table needs to be updated.
    sql = text('SELECT COUNT(*) ' \
               'FROM routes_and_stops ' \
                'WHERE stop_id=:stop_id')
    result = db.session.execute(sql, {'stop_id': stop[0]})
    found = result.fetchone()
    if found[0] == 0:
        for route in routes:
            route_id = route['code']
            stop_id = stop[0]

            sql = 'SELECT id ' \
                  'FROM routes ' \
                  'WHERE hsl_id=:route_id'
            result = db.session.execute(text(sql), {'route_id': route_id})
            route_id = result.fetchone()

            sql = text('INSERT INTO routes_and_stops (stop_id, route_id) '\
                       'VALUES (:stop_id, :route_id)')
            db.session.execute(sql, {'stop_id': stop_id, 'route_id': route_id[0]})
            db.session.commit()
    return