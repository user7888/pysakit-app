from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from os import getenv
import time
import datetime
import requests
import json

app = Flask(__name__)
app.run(debug=True)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/template")
def template():
    # 'should be declared as text' error fix
    sql = text("SELECT content FROM messages")
    result = db.session.execute(sql)

    messages = result.fetchall()
    return render_template("index_db.html", count=len(messages), messages=messages)

@app.route("/stops")
def stops():
    # Placeholder
    stops = []
    #stops = [('1230109', 'Kumpulan kampus'), ('1230112', 'Kumpulan kampus'), ('1240108', 'Kumpula'), ('1240419', 'Kumpulan kampus')]
    # SQL
    sql = text('SELECT id, hsl_id, name, owner, visible FROM stops_new ORDER BY id DESC')
    result = db.session.execute(sql)
    stops_for_user = result.fetchall()

    for stop in stops_for_user:
        print("pysäkki", stop)
        if stop[4] == True:
            stops.append((stop[1], stop[2]))

    print("---")
    print("SQL QUERY RESULT:", stops_for_user)
    print("---")
    return render_template("stops.html", stops=stops)

@app.route("/stops/new")
def stops_new():
    # Search by name or
    # search by id
    stop_ids = [('1230109', 'Kumpulan kampus'), ('1230112', 'Kumpulan kampus'), ('1240108', 'Kumpula'), ('1240419', 'Kumpulan kampus')]

    return render_template("stops_new.html", examples=stop_ids)

@app.route("/stops/delete/<int:id>")
def stops_delete(id):
    sql = text('UPDATE stops_new SET visible=FALSE WHERE hsl_id=:id')
    db.session.execute(sql, {"id": str(id)})
    db.session.commit()

    return redirect("/stops")

@app.route("/stops/add", methods=["POST"])
def add():
    user_input = request.form["content"]
    hsl_id = str(user_input)
    print("---")
    print("INPUT FROM USER:", user_input)
    print("---")

    # User unputted id is used to make a call to HSL api
    query = """{
        stop(id: "HSL:"""+f'{hsl_id}"'+""") {
            name
            wheelchairBoarding
        }
    }"""
    url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    response = requests.post(url, json={'query': query})

    # Convert response to dict
    dict = json.loads(response.text)
    print("DICT FROM /stops/add", dict)

    # Insert values into database.
    # placeholder user is used. (test user)
    sql = text('INSERT INTO stops_new (hsl_id, name, owner, visible) VALUES (:hsl_id, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "name": dict['data']['stop']['name'], "owner": "test_user", "visible": True})
    db.session.commit()
    return redirect("/stops")

@app.route("/stops/schedules/<int:id>")
def hsl(id):
    # Fresh timestamp
    # needed for queries.
    current_time = str(time.time()).split(".")
    start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
    print(current_time)
    start_time = current_time[0]

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
    # Convert to dict
    dict = json.loads(response.text)
    # Arrival time from response
    arrival_time = dict['data']['stop']['stoptimesWithoutPatterns'][0]['realtimeArrival']
    arrival_time_list = dict['data']['stop']['stoptimesWithoutPatterns']
    sign_and_arrival = []

    for element in arrival_time_list:
        element_arrival = element['realtimeArrival']
        time_delta = datetime.timedelta(seconds=element_arrival)
        date_object = start_of_day + time_delta
        # Minutes format fix
        minutes = date_object.minute
        if minutes < 10:
            minutes = "0"+str(minutes)
        temp = (element['headsign'], f'{date_object.hour}:{minutes}')
        sign_and_arrival.append(temp)

    for element in sign_and_arrival:
        print(element)
    # Converting seconds from midnight
    # to current time.
    time_delta = datetime.timedelta(seconds=arrival_time)
    date_object = datetime.datetime.now() + time_delta
    print(dict['data']['stop']['stoptimesWithoutPatterns'][0]['realtimeArrival'])
    return render_template('individual_stop.html', arrivals=sign_and_arrival)