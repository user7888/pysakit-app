from app import app
from db import db
from flask import render_template
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash
from utils import auth
import datetime
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
    allow = True
    if users.user_id():
        allow = False
    if not allow:
        return redirect('/')

    if request.method == "GET":
       return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/stops")
        else:
            return render_template("error.html", \
                                   message="Väärä tunnus tai salasana", \
                                   redirect_url=url_for('login'))

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    allow = True
    if users.user_id():
        allow = False
    if not allow:
        return redirect('/')

    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return render_template("error.html", \
                                   message="Salasanat eivät täsmää", \
                                   redirect_url=url_for('register'))
        if len(username) > 20:
            return render_template("error.html", \
                                   message="Käyttäjänimi on liian pitkä", \
                                   redirect_url=url_for('register'))
        if len(username) <= 0:
            return render_template("error.html", \
                                   message="Käyttäjänimi on liian lyhyt", \
                                   redirect_url=url_for('register'))
        if len(password1) <= 0:
            return render_template("error.html", \
                                   message="Salasana on liian lyhyt", \
                                   redirect_url=url_for('register'))

        if users.register(username, password1):
            return redirect("/stops")
        else:
            return render_template("error.html", \
                                   message="Rekisteröinti ei onnistunut", \
                                   redirect_url=url_for('register'))

@app.route("/stops")
def stop_view():
    # Stop object
    # [0] = key
    # [1] = HSL id
    # [2] = HSL code
    # [3] = name
    # [4] = street name
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')
    user_id = users.user_id()
    stop_list = stops.get_stops(user_id)
    for stop in stop_list:
        print(stop)

    return render_template("stops.html", \
                           stops=stop_list, \
                           len=len(stop_list))

@app.route("/stops/new")
def stops_new():
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')

    return render_template("stops_add.html")

@app.route("/stops/delete/<int:id>")
def stops_delete(id):
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')
    user_id = users.user_id()

    stops.delete(id, user_id)
    return redirect("/stops")

@app.route("/stops/schedules/<int:id>")
def hsl(id):
    # Arrival object
    # [0] = time
    # [1] = headsign
    # [2] = name
    # [3] = mode
    stop_arrivals = stops.get_stop_arrivals(id)
    return render_template('individual_stop.html', \
                           arrivals=stop_arrivals)

@app.route("/stops/search")
def stops_search():
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')
    return render_template("search.html")

@app.route("/stops/search/result", methods=["POST", "GET"])
def search_result():
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')
    
    if not request.form:
        return render_template("error.html", \
                               message="Jotain meni vikaan..", \
                               redirect_url=url_for('stops_search'))
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    user_search = request.form["search"]
    if len(user_search) > 15:
        return render_template("error.html", \
                               message="Hakusana on liian pitkä", \
                               redirect_url=url_for('stops_search'))

    search_results, results_length = stops.search(user_search)
    if results_length == 0:
        return render_template("error.html", \
                               message="Hakusanalla ei löytynyt pysäkkejä", \
                               redirect_url=url_for('stops_search'))

    return render_template("search_results.html", \
                           user_search=user_search, \
                           search_list=search_results, \
                           len=results_length)

@app.route("/stops/add/", defaults={'id':None}, methods=["POST", "GET"])
@app.route("/stops/add/<id>")
def stops_add(id):
    allow = auth.user_is_authorized()
    if not allow:
        return redirect('/')
    user_id = users.user_id()
    if request.method == 'POST':
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

    if request.method == "GET":
        hsl_id = id.split(":")[1]
        if not stops.add_stop(hsl_id, user_id):
            return render_template("error.html", \
                                   message="Yhtäkään pysäkkiä ei löytynyt", \
                                   redirect_url=url_for('stops_search'))
    elif request.method == "POST":
        user_input = request.form["content"]
        hsl_code = str(user_input)
        if not stops.add_stop(hsl_code, user_id):
            return render_template("error.html", \
                                   message="Yhtäkään pysäkkiä ei löytynyt", \
                                   redirect_url=url_for('stops_new'))
    return redirect("/stops")