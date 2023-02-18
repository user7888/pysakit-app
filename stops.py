from db import db
from flask import session
from sqlalchemy import text
import datetime
import time
import requests
import json

def get_stops():
    sql = text('SELECT S.id, S.hsl_id, S.name, S.owner, S.visible FROM stops S, users U WHERE S.owner=U.id AND S.visible ORDER BY s.id DESC')
    result = db.session.execute(sql)
    stop_list = result.fetchall()
    return stop_list

def delete(hsl_id):
    sql = text('UPDATE stops SET visible=FALSE WHERE hsl_id=:hsl_id')
    db.session.execute(sql, {"hsl_id": str(hsl_id)})
    db.session.commit()
    return

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
                arrivalDelay
                scheduledDeparture
                realtimeDeparture
                departureDelay
                realtime
                realtimeState
                serviceDay
                headsign
                trip {
                    bikesAllowed
                    alerts {
                        alertDescriptionText
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
        arrival = (headsign, f'{date_object.hour}:{minutes}')
        arrival_list.append(arrival)
    return arrival_list

def search(user_search):
    # name: transport stop name
    # code: transport stop code visible in stops
    # desc: transport stop street name
    # locationType: stop or station
    query = """{
        stops(name: """+f'"{str(user_search)}"'+"""){
            gtfsId
            name
            code
            desc
            locationType
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    dict = json.loads(response.text)
    # Access the array from query. Each
    # transport stop is a dictionary.
    search_result = dict["data"]["stops"]
    return search_result, len(search_result)

def add_stop(hsl_id):
    # Make the query to HSL api.
    query = """{
        stop(id: "HSL:"""+f'{hsl_id}"'+""") {
            gtfsId
            name
            wheelchairBoarding
            code
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    dict = json.loads(response.text)
    if len(dict['data']['stop']) == 0:
        return False
    # Save stop data to database.
    sql = text('INSERT INTO stops (hsl_id, hsl_code, name, owner, visible) VALUES (:hsl_id, :hsl_code, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "hsl_code":dict['data']['stop']['code'],"name": dict['data']['stop']['name'], "owner": session.get('user_id'), "visible": True})
    db.session.commit()
    return True

def add_stop_by_code(hsl_code):
    if len(hsl_code) != 5:
        return
    query = """{
        stops(name: """+f'"{str(hsl_code)}"'+""") {
            gtfsId
            name
            code
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})
    dict = json.loads(response.text)
    if len(dict['data']['stops']) == 0:
        return False
    # Save stop data to database.
    hsl_id = dict['data']['stops'][0]['gtfsId'].split(':')[1]
    sql = text('INSERT INTO stops (hsl_id, hsl_code, name, owner, visible) VALUES (:hsl_id, :hsl_code, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "hsl_code":dict['data']['stops'][0]['code'],"name": dict['data']['stops'][0]['name'], "owner": session.get('user_id'), "visible": True})
    db.session.commit()

    return True