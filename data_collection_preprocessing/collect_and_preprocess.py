# Getting solar data from API

import requests
import pandas as pd
import json
from pathlib import Path
import os

uppsala_lat_lon = [59.858562, 17.638927]
stockholm_lat_lon = [59.334591, 18.063240]
gothenburg_lat_lon = [57.708870, 11.974560]
malmoe_lat_lon = [55.60587, 13.00073]

uppsala_station = '97530'
stockholm_station = '98230'
gothenburg_station = '71420'
malmoe_station = '52350'

directory_meter = 'meter_data'
metry_key = os.environ['METRY_API']
gmail = os.environ['GMAIL']
gmail_pass = os.environ['GMAIL_PASS']

parameters_STRANG = {
    "CIE_UV_irr": 116,
    "Global_irr": 117,
    "Direct_normal_irr": 118,
    "PAR": 120,
    "Direct_horizontal_irr": 121,
    "Diffuse_irr": 122
}

# Trying the SMHI STRÅNG API


def get_solar_data_STRANG(frm="2019-05-01", to="2022-05-01", parameter=parameters_STRANG["Direct_normal_irr"]):
    cities = ["uppsala", "stockholm", "malmoe", "gothenburg"]
    for city in cities:
        if city == "uppsala":
            lat, lon = 59.858562, 17.638927
        elif city == "gothenburg":
            lat, lon = 57.708870, 11.974560
        elif city == "malmoe":
            lat, lon = 55.6, 13.0
        elif city == "stockholm":
            lat, lon = 59.334591, 18.063240

        response = requests.get(
            f"https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point/lon/{lon}/lat/{lat}/parameter/{parameter}/data.json?from={frm}&to={to}&interval=hourly")
        if response.status_code == 200:
            with open(f'./irr_data/irr_data{city}.json', 'w') as outfile:
                json.dump(response.json(), outfile)
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

# Getting some data from Metry


def get_metry_data(frm="20190501", to="20220501"):
    f = open('./data_collection_preprocessing/metry_files/meters_metry.json')
    meter_ids = json.load(f)
    for place in meter_ids["meters"]:
        id = place["_id"]
        response = requests.get(
            f"https://app.metry.io/api/v2/consumptions/{id}/hour/{frm}-{to}?access_token={metry_key}")
        if response.status_code == 200:
            with open(f'./meter_data/solar_metry_meters_{id}.json', 'w') as outfile:
                json.dump(response.json(), outfile)
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")


def generate_csv_for_ml():
    j = 1
    files_meter = Path(directory_meter).glob('**/*.json')
    print(files_meter)
    id_city = json.load(open('./data_collection_preprocessing/id_city.json'))
    for meter_file in files_meter:
        print("Nu gör jag nummer: " + str(j) + " av 87 :-)")
        print("Nu gör jag nummer: " + str(j) + " av 87 :-)")
        id = str(meter_file).split('_')[4].split('.')[0]
        f = open(meter_file)
        print(id)
        meter_vals = json.load(f)
        city = id_city[id]['city']
        g = open(f'irr_data/irr_data{city}.json')
        irr_vals = pd.read_json(g)
        list = []
        print(len(irr_vals))
        print(len(meter_vals["data"][0]["periods"][0]["energy"]))
        for i in range(len(irr_vals)):
            list.append(
                {
                    "date_time": irr_vals.iloc[i]['date_time'],
                    "irradiance": irr_vals.iloc[i]['value'],
                    "generated_energy": meter_vals["data"][0]["periods"][0]["energy"][i+1],
                    "city": city,
                    "metry_meter_id": id
                })
        listdf = pd.DataFrame(list)
        listdf.to_csv(f'./meter_obs_and_irr/{id}_irr_and_energy_data.csv')
        j += 1
    return()


frm_strang = "2019-05-01"
to_strang = "2022-05-01"
frm_metry = "20190501"
to_metry = "20220501"

get_solar_data_STRANG(frm_strang, to_strang)


# get_metry_data(frm, to)
# generate_csv_for_ml()
