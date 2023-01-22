from flask import Flask
import urllib.request
import json
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return "Heipparallaa!"

@app.route("/page1")
def page1():
    return "Tämä on sivu 1"

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