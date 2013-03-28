#!/usr/bin/env python

import urllib.request
from urllib.parse import quote_plus,urlencode
import json
import sys

API_KEY = "377d840e54b59adbe53608ba1aad70e8"
API_BASE = "http://live.kvv.de/webapp/"

class Stop:
    def __init__(self, name, id, lat, lon):
        self.name = name
        self.id = id
        self.lat = lat
        self.lon = lon

    def from_json(json):
        return Stop(json["name"], json["id"], json["lat"], json["lon"])

class Departure:
    def __init__(self, route, destination, direction, time, vehicle_type, lowfloor, realtime, traction, stop_position):
        self.route = route
        self.destination = destination
        self.direction = direction
        self.time = time #TODO: to timestamp?
        self.vehicle_type = vehicle_type
        self.lowfloor = lowfloor
        self.realtime = realtime
        self.traction = traction
        self.stop_position = stop_position

    def from_json(json):
        return Departure(json["route"], json["destination"], json["direction"], json["time"], json["vehicleType"], json["lowfloor"], json["realtime"], json["traction"], json["stopPosition"])

    def pretty_format(self):
        return self.time + ("  " if self.realtime else "* ") + self.route + " " + self.destination


def _query(path, params = {}):
    params["key"] = API_KEY
    url = API_BASE + path + "?" + urlencode(params)
    #print(url)
    req = urllib.request.Request(url)

    try:
        handle = urllib.request.urlopen(req)
    except IOError as e:
        print("error!")
        if hasattr(e, "code"):
            if e.code != 403:
                print("We got another error")
                print(e.code)
            else:
                print(e.headers)
                print(e.headers["www-authenticate"])
        return None; #TODO: Schoenere Fehlerbehandlung

    return json.loads(handle.read().decode())

def _search(query):
    json = _query(query)
    stops = []
    if json:
        for stop in json["stops"]:
            stops.append(Stop.from_json(stop))
    return stops

def search_by_name(name):
    """ search for stops by name
        returns a list of Stop objects
    """
    return _search("stops/byname/" + quote_plus(name))

def search_by_latlon(lat, lon):
    """ search for a stops by latitude and longitude
        returns a list of Stop objectss
    """
    return _search("stops/bylatlon/" + lat + "/" + lon)

def search_by_id(id):
    """ search for a stop by its id
        returns a list that should contain only one stop
    """
    return [Stop.from_json(_query("stops/bystop/" + id))]

def _get_departures(query, max_info=10):
    json = _query(query, {"maxInfo" : str(max_info)})
    departures = []
    if json:
        for dep in json["departures"]:
            departures.append(Departure.from_json(dep))
    return departures


def get_departures(id, max_info=10):
    """ gets departures for a given stop id
        optionally set the maximum number of entries 
        returns a list of Departure objects
    """
    return _get_departures("departures/bystop/" + id, max_info)

def get_departures_by_route(id, route, max_info=10):
    """ gets departures for a given stop id and route
        optionally set the maximum number of entries 
        returns a list of Departure objects
    """
    return _get_departures("departures/byroute/" + route + "/" + id, max_info)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "search":
        if sys.argv[2].startswith("de:"):
            for stop in search_by_id(sys.argv[2]):
                print(stop.name + " (" + stop.id + ")")
        else:
            for stop in search_by_name(sys.argv[2]):
                print(stop.name + " (" + stop.id + ")")
    elif len(sys.argv) == 4 and sys.argv[1] == "search":
        for stop in search_by_latlon(sys.argv[2], sys.argv[3]):
            print(stop.name + " (" + stop.id + ")")
    elif len(sys.argv) == 3 and sys.argv[1] == "departures":
        for dep in get_departures(sys.argv[2]):
            print(dep.pretty_format())
    elif len(sys.argv) == 4 and sys.argv[1] == "departures":
        for dep in get_departures_by_route(sys.argv[2], sys.argv[3]):
            print(dep.pretty_format())
    else:
        print("No such command. Try \"search <name>/<id>/<lat> <lon>\" or \"departures <stop id> [<route>]\"")
