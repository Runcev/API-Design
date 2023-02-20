from flask import Flask, jsonify, request, json
from datetime import datetime
import requests

app = Flask(__name__)


# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = ""
# you can get API keys for free here - https://api-docs.pgamerx.com/
RSA_API_KEY = ""


def generate_weather(location: str, date: str):
    coordinateURL = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={RSA_API_KEY}"

    coordinateResponse = requests.request("GET", coordinateURL)
    data = json.loads(coordinateResponse.text)
    lat = data[0]['lat']
    lon = data[0]['lon']
    dt = int(datetime.strptime(date, '%Y-%m-%d').timestamp())
    print("datetime", dt)

    weatherURL = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?units=metric&lang=ua&lat={lat}&lon={lon}&dt={dt}&appid={RSA_API_KEY}"

    weatherResponse = requests.request("GET", weatherURL)
    weather = json.loads(weatherResponse.text)

    return weather


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    # token
    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    # Name
    requester_name = ""
    if json_data.get("requester_name"):
        requester_name = json_data.get("requester_name")

    # Location
    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")

    # Date
    if json_data.get("date") is None:
        raise InvalidUsage("Date is required", status_code=400)

    date = ""
    if json_data.get("date"):
        date = json_data.get("date")

    weather = generate_weather(location, date)

    result = {
        "requester_name": requester_name,
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result
