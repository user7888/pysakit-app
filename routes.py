from app import app
from db import db
from flask import render_template
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import requests
import json
import time
import users
import stops

@app.route("/template")
def template():
    # 'should be declared as text' error fix
    sql = text("SELECT content FROM messages")
    result = db.session.execute(sql)

    messages = result.fetchall()
    return render_template("index_db.html", count=len(messages), messages=messages)

@app.route("/empty")
def empty():
    return render_template("functionality_missing.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
       return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/stops")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get('user_id'):
        return redirect("/")

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eivät täsmää")
        if users.register(username, password1):
            return redirect("/stops")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")

@app.route("/stops")
def stop_view():
    if session.get('user_id') is None:
        return redirect("/")

    list = stops.get_stops()
    return render_template("stops.html", stops=list, len=len(list))

@app.route("/stops/new")
def stops_new():
    if session.get('user_id') is None:
        return redirect("/")

    return render_template("stops_new.html")

@app.route("/stops/delete/<int:id>")
def stops_delete(id):
    if session.get('user_id') is None:
        return redirect("/")

    stops.delete(id)
    return redirect("/stops")

@app.route("/stops/add", methods=["POST"])
def add():
    if session.get('user_id') is None:
        return redirect("/")
    
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
    # placeholder user is used (test user)
    sql = text('INSERT INTO stops (hsl_id, name, owner, visible) VALUES (:hsl_id, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "name": dict['data']['stop']['name'], "owner": "test_user", "visible": True})
    db.session.commit()
    return redirect("/stops")

@app.route("/stops/schedules/<int:id>")
def hsl(id):
    if session.get('user_id') is None:
        return redirect("/")

    # Timestamp for HSL api queries
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

@app.route("/stops/search/result", methods=["POST", "GET"])
def search_result():
    user_search = request.args["query"]
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
    # transport stop is a dict.
    search_result_list = dict["data"]["stops"]
    result_len = len(search_result_list)
    for alkio in search_result_list:
        print(alkio)
    return render_template("search_results.html", user_search=user_search, search_list=search_result_list, len=result_len)

@app.route("/stops/search")
def stops_search():
    return render_template("search.html")

@app.route("/stops/search/add/<id>", methods=["POST", "GET"])
def add_search(id):
    if session.get('user_id') is None:
        return redirect("/")
    # Get id from parameters
    hsl_id = id.split(":")[1]

    # User inputted id is used to make a call to HSL api
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

    # Insert values into database.
    # placeholder user is used (test user)
    #
    # Owner täytyy päivittää
    sql = text('INSERT INTO stops (hsl_id, name, owner, visible) VALUES (:hsl_id, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "name": dict['data']['stop']['name'], "owner": session.get('user_id'), "visible": True})
    db.session.commit()
    return redirect("/stops")