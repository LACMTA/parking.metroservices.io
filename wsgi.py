import json
import requests
import pytablewriter, dominate
from pytablewriter.style import Style
# import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone

from flask import Flask, Response, render_template
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

DEBUG = True

url_locations = 'https://api.metro.net/agencies/lametro/parking/'
headers = {}
fmt = "%b %d at %I:%M %p"


class Lot():
    def __init__(self, headers, id='5b81ee9500000021f0ce8a8b', name='unknown'):
        self.id = id
        self.name = name
        # self.updated = now_pacific.strftime(fmt)

    def __repr__(self):
        return (f'{self.__class__.__name__}('f'{self.id!r}, {self.name!r})')

    def __str__(self):
        return (f'{self.__class__.__name__}('f'{self.id!r}, {self.name!r})')

    def get_status(self):
        url_status = 'https://api.metro.net/agencies/lametro/parking/%s' % (
            self.id)
        response = requests.get(url_status, headers=headers)
        mydict = json.loads(response.json())

        # self.updated = now_pacific.strftime(fmt)
        self.name = mydict['name']
        self.updated = mydict['updated']
        self.total = mydict['total']
        self.free = mydict['free']
        self.disabledfree = mydict['disabledfree']
        self.disabledtotal = mydict['disabledtotal']
        self.basic = {
            'name': self.name,
            'updated': self.updated,
            'free': self.free,
            'total': self.total,
            'disabledfree': self.disabledfree,
            'disabledtotal': self.disabledtotal,
        }
        return json.dumps(self.basic)


def _get_stations():
    stations = []
    response = requests.get(url_locations, headers=headers)
    json_data = json.loads(response.json())

    for loc in json_data:
        tmp = Lot(headers, id=loc['id'], name=loc['name'])
        stations.append(tmp)
    return stations, json_data



def _updatestatus():
    stations, jsonstations = _get_stations()
    curstatus = []

    for station in stations:
        # convert json string to dict
        curstatus.append(json.loads(station.get_status()))

    mtrx = []
    for lot in curstatus:
        l = [
            lot['name'], lot['total'], lot['free'], lot['disabledtotal'],
            lot['disabledfree']
        ]
        mtrx.append(l)

    return mtrx


@app.route("/")
@cache.cached(timeout=15)
def parking_table():
    hwriter = pytablewriter.HtmlTableWriter()
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    hwriter.table_name = "Gold Line Parking status at %s" % (
        now_pacific.strftime(fmt))
    hwriter.headers = [
        "Station", "Total", "Available", "Disabled Total", "Disabled Available"
    ]
    hwriter.value_matrix = _updatestatus()
    return hwriter.dumps()

@app.route("/api/")
@cache.cached(timeout=15)
def getjson():
    jwriter = pytablewriter.JsonTableWriter()
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    jwriter.table_name = "Gold Line Parking status at %s" % (
        now_pacific.strftime(fmt))
    jwriter.headers = [
        "Station", "Total", "Available", "Disabled Total", "Disabled Available"
    ]
    jwriter.value_matrix = _updatestatus()
    return Response(jwriter.dumps(), mimetype='application/json')

@app.route("/zebra")
@cache.cached(timeout=15)
def gettemplate():
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    table_name = "Gold Line Parking status as of %s" % (
        now_pacific.strftime(fmt))
    headers = [
        "Station", "Total", "Available", "Disabled Total", "Disabled Available"
    ]
    data = _updatestatus()

    return render_template('zebra.html', data=data,table_name=table_name)


# import app as application

if __name__ == "__main__":
    app.run(host='0.0.0.0')

