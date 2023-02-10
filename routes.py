from app import app
from flask import render_template
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import requests
import json
import time
db = SQLAlchemy(app)

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

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    session["username"] = username
    return redirect("/stops")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    # Should redirect to index if user is
    # logged in (and logged out?)
    if session.get('username'):
        return redirect("/")

    return render_template("register.html")

@app.route("/users/add", methods=["POST"])
def add_user():
    username = request.form["username"]
    password = request.form["password"]
    password_again = request.form["password_again"]
    print("user", username)
    print("pass", password)
    print("pass again", password_again)
    # Raise error passwords do not match
    # -
    # Hash the password and insert values to
    # database
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    return redirect("/")

@app.route("/stops")
def stops():
    if session.get('username') is None:
        return redirect("/")

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
    return render_template("stops.html", stops=stops, len=len(stops))

@app.route("/stops/new")
def stops_new():
    if session.get('username') is None:
        return redirect("/")

    # Search by name or
    # search by id
    stop_ids = [('1230109', 'Kumpulan kampus'), ('1230112', 'Kumpulan kampus'), ('1240108', 'Kumpula'), ('1240419', 'Kumpulan kampus')]

    return render_template("stops_new.html", examples=stop_ids)

@app.route("/stops/delete/<int:id>")
def stops_delete(id):
    if session.get('username') is None:
        return redirect("/")

    sql = text('UPDATE stops_new SET visible=FALSE WHERE hsl_id=:id')
    db.session.execute(sql, {"id": str(id)})
    db.session.commit()

    return redirect("/stops")

@app.route("/stops/add", methods=["POST"])
def add():
    if session.get('username') is None:
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
    sql = text('INSERT INTO stops_new (hsl_id, name, owner, visible) VALUES (:hsl_id, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "name": dict['data']['stop']['name'], "owner": "test_user", "visible": True})
    db.session.commit()
    return redirect("/stops")

@app.route("/stops/schedules/<int:id>")
def hsl(id):
    if session.get('username') is None:
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
    if session.get('username') is None:
        return redirect("/")
    # Get id from parameters
    hsl_id = id.split(":")[1]

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

    # Insert values into database.
    # placeholder user is used (test user)
    sql = text('INSERT INTO stops_new (hsl_id, name, owner, visible) VALUES (:hsl_id, :name, :owner, :visible)')
    db.session.execute(sql, {"hsl_id": hsl_id, "name": dict['data']['stop']['name'], "owner": "test_user", "visible": True})
    db.session.commit()
    return redirect("/stops")