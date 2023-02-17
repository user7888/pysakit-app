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

@app.route("/")
def index():
    if session.get('user_id'):
        return redirect("/stops")
    if not session.get('user_id'):
        return render_template('login.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
       return render_template("login.html")
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

    return render_template("stops_add.html")

@app.route("/stops/delete/<int:id>")
def stops_delete(id):
    if session.get('user_id') is None:
        return redirect("/")

    stops.delete(id)
    return redirect("/stops")

@app.route("/stops/schedules/<int:id>")
def hsl(id):
    if session.get('user_id') is None:
        return redirect("/")

    stop_arrivals = stops.get_stop_arrivals(id)
    return render_template('individual_stop.html', arrivals=stop_arrivals)

@app.route("/stops/search/result", methods=["POST", "GET"])
def search_result():
    user_search = request.args["search"]
    search_results, results_length = stops.search(user_search)
    return render_template("search_results.html", user_search=user_search, search_list=search_results, len=results_length)

@app.route("/stops/search")
def stops_search():
    return render_template("search.html")

@app.route("/stops/add/", defaults={'id':None}, methods=["POST", "GET"])
@app.route("/stops/add/<id>")
def add_search(id):
    if request.method == "GET":
        hsl_id = id.split(":")[1]
        stops.add_stop(hsl_id)
    if request.method == "POST":
        user_input = request.form["content"]
        hsl_id = str(user_input)
        stops.add_stop(hsl_id)

    return redirect("/stops")

@app.route("/empty")
def empty():
    return render_template("functionality_missing.html")

@app.route("/template")
def template():
    # 'should be declared as text' error fix
    sql = text("SELECT content FROM messages")
    result = db.session.execute(sql)

    messages = result.fetchall()
    return render_template("index_db.html", count=len(messages), messages=messages)
