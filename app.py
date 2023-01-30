from flask import Flask
from flask import render_template, request
import urllib.request
import json
import requests

app = Flask(__name__)

@app.route("/")
def index():
    words = ["apina", "banaani", "cembalo"]
    return render_template("index.html", message="Tervetuloa!", items=words)

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/result", methods=["POST"])
def result():
    return render_template("result.html", name=request.form["name"])

@app.route("/order")
def order():
    return render_template("order.html")

@app.route("/orderresult", methods=["POST"])
def order_result():
    pizza = request.form["pizza"]
    # Huom. getlist-metodi.
    extras = request.form.getlist("extra")
    message = request.form["message"]
    return render_template("order_result.html", pizza=pizza, extras=extras, message=message)

@app.route("/page1")
def page1():
    return "Tämä on sivu 1"

@app.route("/page/<int:id>")
def page(id):
    return "Tämä on sivu " + str(id)

@app.route("/hsltest")
def hsl():
    query = """{
        stop(id: "HSL:1240133") {
            name
            stoptimesWithoutPatterns(startTime: 1674392128) {
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

@app.route("/test")
def test():
    query = """query {
        characters {
            results {
                name
                status
                species
                type
                gender
            }
        }
    }"""

    url = 'https://rickandmortyapi.com/graphql/'
    response = requests.post(url, json={'query': query})

    print(response.status_code)
    print(response.text)

    return response.text