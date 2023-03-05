from db import db
from flask import session
from sqlalchemy import text
import datetime
import time
import requests
import json
import time

def get_stops(user_id):
    sql = 'SELECT S.id, S.hsl_id, S.hsl_code, S.name, S.description, C.category ' \
          'FROM stops S ' \
          'JOIN transport_categories C ON S.category_id=C.id, ' \
          'stops_and_users SU ' \
          'WHERE SU.user_id=:user_id ' \
          'AND SU.stop_id=S.id ' \
          'AND SU.visible'

    result = db.session.execute(text(sql), {'user_id': user_id})
    stop_list = result.fetchall()
    for stop in stop_list:
        print(stop)
    print(len(stop_list))
    return stop_list

# BUGS
def delete(stop_id, user_id):
    print("attemptind delete stop", stop_id, "user", user_id)
    sql = text('UPDATE stops_and_users ' \
               'SET visible=FALSE ' \
               'WHERE id=' \
                    '(SELECT id '\
                    'FROM stops_and_users '\
                    'WHERE visible=TRUE '\
                    'ORDER BY id DESC '\
                    'LIMIT 1) ' \
               'AND stops_and_users.stop_id= '\
                    '(SELECT id '\
                    'FROM stops '\
                    'WHERE hsl_id=:stop_id) ' \
               'AND stops_and_users.user_id=:user_id')

    db.session.execute(sql, {'user_id': user_id, 'stop_id': str(stop_id)})
    db.session.commit()
    return

def search(user_search):
    # name: transport stop name
    # code: transport stop code visible in stops
    # desc: transport stop street name
    # locationType: stop or station
    # vehicleMode: category
    query = """{
        stops(name: """+f'"{str(user_search)}"'+"""){
            gtfsId
            name
            code
            desc
            locationType
            vehicleMode
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    dict = json.loads(response.text)
    # Access the array from query. Each
    # transport stop is a dictionary.
    search_result = dict["data"]["stops"]
    for result in search_result:
        print(result)
    return search_result, len(search_result)

def insert_all_stops():
    sql = text('SELECT COUNT(*) FROM stops')
    result = db.session.execute(sql)
    found = result.fetchone()
    # The amount of stops in api
    # changes semi frequently.
    if found[0] > 8200:
        return

    query = """{
        stops{
            gtfsId
            name
            code
            desc
            vehicleMode
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    dict = json.loads(response.text)
    categories = {'BUS': 1, 'TRAM': 2, 'SUBWAY': 3, 'RAIL': 4, 'FERRY': 5}

    for element in dict['data']['stops']:
        new = {}
        new['hsl_id'] = element['gtfsId'].split(':')[1]
        new['hsl_code'] = element['code']
        new['name'] = element['name']
        new['description'] = element['desc']
        new['category'] = categories[element['vehicleMode']]

        sql = text('SELECT hsl_id FROM stops WHERE hsl_id=:hsl_id')
        result = db.session.execute(sql, {'hsl_id': new['hsl_id']})
        found = result.fetchone()
        if found:
            continue
        
        sql = text('INSERT INTO stops (hsl_id, hsl_code, name, description, category_id) ' \
                   'VALUES (:hsl_id, :hsl_code, :name, :description, :category)')

        db.session.execute(sql, {"hsl_id": element['gtfsId'].split(':')[1], \
                                 "hsl_code":element['code'],"name": element['name'], \
                                 "description": element['desc'], \
                                 "category": new['category']})
        db.session.commit()
        
    
    db.session.commit()
    return

def add_stop(hsl_code, user_id):
    print("stop was added using id:", user_id)
    # Add based on hsl_code.
    if len(hsl_code) == 5:
        # Find the stop from database.
        sql = 'SELECT id, hsl_id ' \
              'FROM stops ' \
              'WHERE hsl_code=:hsl_code'
        result = db.session.execute(text(sql), {'hsl_code': hsl_code})
        stop_found = result.fetchone()

        if not stop_found:
            return False

    # Add based on hsl_id
    elif len(hsl_code) == 7:
        sql = 'SELECT id, hsl_id ' \
              'FROM stops ' \
              'WHERE hsl_id=:hsl_code'
        result = db.session.execute(text(sql), {'hsl_code': hsl_code})
        stop_found = result.fetchone()

        if not stop_found:
            return False
    else:
        return False
    
    sql = text('INSERT INTO stops_and_users (stop_id, user_id, visible) ' \
               'VALUES (:stop_id, :user_id, :visible)')
    db.session.execute(sql, {'stop_id': stop_found[0], 'user_id': user_id, 'visible': True})
    db.session.commit()

    # Get routes related to new stop
    # from HSL api.
    query = """{
        stop(id: "HSL:"""+f'{stop_found[1]}"'+""") {
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
    stop = json.loads(response.text)
    categories = {'BUS': 1, 'TRAM': 2, 'SUBWAY': 3, 'RAIL': 4, 'FERRY': 5}

    # Add routes related to the newly added stop.
    routes = stop['data']['stop']['patterns']
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
    
    # Check if the routes_and_stops
    # table needs to be updated.
    sql = text('SELECT COUNT(*) ' \
               'FROM routes_and_stops ' \
                'WHERE stop_id=:stop_id')
    result = db.session.execute(sql, {'stop_id': stop_found[0]})
    found = result.fetchone()
    if found[0] == 0:
        sql = 'SELECT id ' \
              'FROM routes ' \
              'WHERE hsl_id=:hsl_id'
        result = db.session.execute(text(sql), {'hsl_id': hsl_id})
        route_id = result.fetchone()

        for route in routes:
            sql = text('INSERT INTO routes_and_stops (stop_id, route_id) '\
                       'VALUES (:stop_id, :route_id)')
            db.session.execute(sql, {'stop_id': stop_found[0], 'route_id': route_id[0]})
        
        db.session.commit()
    return True

def get_stop_arrivals(id):
    # Form a timestamp for the 
    # query to HSL api.
    current_time = str(time.time()).split(".")
    start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
    start_time = current_time[0]
    # Make the query to HSL api.
    query = """{
        stop(id: "HSL:"""+f'{str(id)}"'+""") {
            name
            stoptimesWithoutPatterns(startTime:"""+f'{start_time}'+""") {
                scheduledArrival
                realtimeArrival
                realtimeState
                headsign
                trip {
                    pattern {
                        code
                        route {
                            gtfsId
                            shortName
                            longName
                            mode
                            alerts {
                                id
                            }
                        }
                        }
                    }
                }
            }  
        }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    # Convert the query response
    dict = json.loads(response.text)
    arrival_time_list = dict['data']['stop']['stoptimesWithoutPatterns']
    arrival_list = []

    for element in arrival_time_list:
        # Format arrival time.
        element_arrival = element['realtimeArrival']
        time_delta = datetime.timedelta(seconds=element_arrival)
        date_object = start_of_day + time_delta
        # Format the minutes.
        minutes = date_object.minute
        if minutes < 10:
            minutes = "0"+str(minutes)
        # For some reason some queries 
        # return without a headsign.
        headsign = element['headsign']
        if not headsign:
            headsign = 'Tuntematon'

        route_id = element['trip']['pattern']['code']
        sql = text('SELECT short_name, long_name, C.category ' \
                   'FROM routes R ' \
                   'JOIN transport_categories C ON R.category_id=C.id ' \
                   'WHERE hsl_id=:route_id')
        result = db.session.execute(sql, {'route_id': route_id})
        row = result.fetchone()
        arrival = (f'{date_object.hour}:{minutes}', \
                   row[0], row[1], row[2])

        arrival_list.append(arrival)
    return arrival_list