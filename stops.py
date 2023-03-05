from db import db
from flask import session
from sqlalchemy import text
import datetime
import time
import requests
import json
import time
import routes

def get_stops(user_id):
    sql = 'SELECT S.id, S.hsl_id, S.hsl_code, S.name, S.description, C.category, SU.id ' \
          'FROM stops S ' \
          'JOIN transport_categories C ON S.category_id=C.id, ' \
          'stops_and_users SU ' \
          'WHERE SU.user_id=:user_id ' \
          'AND SU.stop_id=S.id ' \
          'AND SU.visible ' \
          'ORDER BY SU.id DESC'

    result = db.session.execute(text(sql), {'user_id': user_id})
    stop_list = result.fetchall()
    for stop in stop_list:
        print(stop)
    print(len(stop_list))
    return stop_list

def delete(stop_id, user_id):
    # Old query for reference. Stop can't be singled out without
    # SU.id when multiples of the same stop are visible.
    # sql = text('UPDATE stops_and_users ' \
    #            'SET visible=FALSE ' \
    #            'WHERE stops_and_users.id=:stop_id '\
    #                 '(SELECT id '\
    #                 'FROM stops_and_users '\
    #                 'WHERE stop_id=(SELECT id FROM stops WHERE hsl_id=:stop_id) ' \
    #                 'AND stops_and_users.user_id=:user2_id ' \
    #                 'AND stops_and_users.visible=TRUE ' \
    #                 'LIMIT 1)')
    sql = text('UPDATE stops_and_users ' \
               'SET visible=FALSE ' \
               'WHERE stops_and_users.id=:stop_id')
    db.session.execute(sql, {'stop_id': str(stop_id)})
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
        sql = text('SELECT hsl_id FROM stops WHERE hsl_id=:hsl_id')
        result = db.session.execute(sql, {'hsl_id': element['gtfsId'].split(':')[1]})
        found = result.fetchone()
        if found:
            continue
        
        sql = text('INSERT INTO stops (hsl_id, hsl_code, name, description, category_id) ' \
                   'VALUES (:hsl_id, :hsl_code, :name, :description, :category)')
        db.session.execute(sql, {"hsl_id": element['gtfsId'].split(':')[1], \
                                 "hsl_code":element['code'], \
                                 "name": element['name'], \
                                 "description": element['desc'], \
                                 "category": categories[element['vehicleMode']]})
        db.session.commit()
    return

def add_stop(hsl_code, user_id):
    # Handle hsl_code.
    if len(hsl_code) == 5:
        # Find the stop from database.
        sql = 'SELECT id, hsl_id ' \
              'FROM stops ' \
              'WHERE hsl_code=:hsl_code'
        result = db.session.execute(text(sql), {'hsl_code': hsl_code})
        new_stop = result.fetchone()
        if not new_stop:
            return False

    # Handle hsl_id
    elif len(hsl_code) == 7:
        sql = 'SELECT id, hsl_id ' \
              'FROM stops ' \
              'WHERE hsl_id=:hsl_code'
        result = db.session.execute(text(sql), {'hsl_code': hsl_code})
        new_stop = result.fetchone()
        if not new_stop:
            return False
    else:
        return False
    
    sql = text('INSERT INTO stops_and_users (stop_id, user_id, visible) ' \
               'VALUES (:stop_id, :user_id, :visible)')
    db.session.execute(sql, {'stop_id': new_stop[0], 'user_id': user_id, 'visible': True})
    db.session.commit()
    # Add routes for this stop.
    routes.add_routes(new_stop)
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