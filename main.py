import json
import requests
import folium
import os
from geopy import distance
from flask import Flask
from dotenv import load_dotenv


load_dotenv()


def fetch_coordinates(geocode_api, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": geocode_api,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def find_user_location():
    location = str(input("Где вы находитесь? "))
    coords = fetch_coordinates(geocode_api, location)
    return coords


def read_file_locations():
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()
    return json.loads(file_contents)


def coffee_and_locations():
    coords = find_user_location()
    coffee_shops = read_file_locations()
    coffee_shops_infos = []
    for coffee_shop in coffee_shops:
        coffee_shops_infos.append({
            'title': coffee_shop['Name'],
            'distance': distance.distance(coords, tuple(coffee_shop['geoData']['coordinates'][::-1])).km,
            'latitude': coffee_shop['Latitude_WGS84'],
            'longitude': coffee_shop['Longitude_WGS84'],
        })
    return coords, coffee_shops_infos


def get_closer_location(coffee_shops):
    return coffee_shops['distance']


def main():
    start_loc, locations = coffee_and_locations()
    more_closer_location = sorted(locations, key=get_closer_location, reverse=False)[:5]
    creating_map(start_loc, more_closer_location)
    run_app()


def run_app():
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')


def creating_map(start_loc, list_locations):
    m = folium.Map(start_loc, zoom_start=12, tiles="Stamen Terrain")
    for location in list_locations:
        lat = location["latitude"]
        lon = location["longitude"]
        folium.Marker(
            location=(lat, lon),
            tooltip="Click me!",
            popup="Timberline Lodge",
            icon=folium.Icon(color="green"), ).add_to(m)
    m.save("index.html")


def hello_world():
    with open("index.html", "r", encoding='utf-8') as my_file:
        return my_file.read()


if __name__ == "__main__":
    geocode_api = os.environ['API_KEY']
    main()