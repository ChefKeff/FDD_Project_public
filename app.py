import ast
import json
from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import plotly
import requests
import datetime
import json
import plotly.graph_objects as go
from apscheduler.schedulers.background import BackgroundScheduler
from emailing import send_alert, send_remove_conf, send_sub_conf
import os
app = Flask(__name__)

json_file_path = "./data_collection_preprocessing/id_city.json"


with open(json_file_path, 'r') as j:
    all_ids = json.loads(j.read())
tot_number_of_meters = len(all_ids.keys())

metry_key = os.environ['METRY_API']
gmail = os.environ['GMAIL']
gmail_pass = os.environ['GMAIL_PASS']


def value_predictor(city, frm=datetime.date.today() - datetime.timedelta(days=34), to=datetime.date.today() - datetime.timedelta(days=31)):
    """
    This function will calculate the predicted value given a city and an interval.
    """
    model = pickle.load(open('model.pkl', "rb"))
    modelma = pickle.load(open('model_malmoe.pkl', "rb"))
    modelgb = pickle.load(open('model_gbg.pkl', "rb"))
    modelupp = pickle.load(open('model_uppsala.pkl', "rb"))
    modelsto = pickle.load(open('model_sthlm.pkl', "rb"))
    lat_lon = get_lat_lon(city)
    strang_api = get_irradiance(lat_lon[0], lat_lon[1], str(frm), str(to))
    result = model.predict(
        np.array(pd.DataFrame(strang_api)['value']).reshape(-1, 1))
    resultma = modelma.predict(
        np.array(pd.DataFrame(strang_api)['value']).reshape(-1, 1))
    resultgb = modelgb.predict(
        np.array(pd.DataFrame(strang_api)['value']).reshape(-1, 1))
    resultupp = modelupp.predict(
        np.array(pd.DataFrame(strang_api)['value']).reshape(-1, 1))
    resultsto = modelsto.predict(
        np.array(pd.DataFrame(strang_api)['value']).reshape(-1, 1))

    return(result, resultma, resultgb, resultupp, resultsto)


def per_meter_value_predictor(city, meter_id, frm=datetime.date.today() - datetime.timedelta(days=34), to=datetime.date.today() - datetime.timedelta(days=31)):
    """Currently not used since the models are not that good :("""
    try:
        model = pickle.load(
            open(f'./per_meter_models/model_{meter_id}.pkl', "rb"))
        lat_lon = get_lat_lon(city)
        strang_api = get_irradiance(lat_lon[0], lat_lon[1], str(frm), str(to))
        data = {"irradiance": pd.DataFrame(
            strang_api)['value'], "month": pd.to_datetime(
                pd.DataFrame(strang_api)['date_time']).dt.month}
        df = pd.DataFrame(data)
        df.round({'irradiance': 1, 'month': 1})
        result = model.predict(df[['irradiance', 'month']])
        return result.reshape(-1, 1)
    except:
        return []


def per_meter_energy_predictor(city, meter_id, frm=datetime.date.today() - datetime.timedelta(days=34), to=datetime.date.today() - datetime.timedelta(days=31)):
    """
    Used to get the per-day energy predictions. These are the predictions being displayed in the bar-graph.
    """
    try:
        model = pickle.load(
            open(f'./per_meter_models_energy/model_{meter_id}_energy_per_day.pkl', "rb"))
        lat_lon = get_lat_lon(city)
        strang_api = pd.DataFrame(get_irradiance(
            lat_lon[0], lat_lon[1], str(frm), str(to)))
        strang_api = strang_api.groupby(
            pd.to_datetime(strang_api['date_time']).dt.date).agg({"value": "sum"})
        data = {"irradiance": pd.DataFrame(strang_api)['value'], "month": pd.to_datetime(
            strang_api.index).month}
        df = pd.DataFrame(data)
        df.round({'irradiance': 1, 'month': 1})
        result = model.predict(df[['irradiance', 'month']])
        return result.reshape(-1, 1)
    except:
        return []


def get_lat_lon(city):
    """
    Getting the latitude and longitude of a given city using the city name.
    """
    if city == "uppsala":
        # lat and lon for Uppsala
        return([59.858562, 17.638927])
    if city == "stockholm":
        # lat and lon for Stockholm
        return([59.334591, 18.063240])
    if city == "gothenburg":
        # lat and lon for Gothenburg
        return([57.708870, 11.974560])
    # lat and lon for Malmoe
    return([55.60587, 13.00073])


def get_irradiance(lat, lon, frm, to):
    """
    Getting the irradiance from the SMHI STRÅNG-API using the latitude and longitude of some given city.
    The interval from when to retrieve the data need also be specified in the function call.
    """
    parameter = '117'
    response = requests.get(
        f"https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point/lon/{lon}/lat/{lat}/parameter/{parameter}/data.json?from={frm}&to={to}")
    if response.status_code == 200:
        return(response.json())
    else:
        print(
            f"Hello person, there's a {response.status_code} error with your request")


def get_metry_data(summed=True, frm=(datetime.date.today() - datetime.timedelta(days=34)).strftime("%Y%m%d"), to=(datetime.date.today() - datetime.timedelta(days=31)).strftime("%Y%m%d"), number_of_meters=tot_number_of_meters, id='614b288ed36b0038600833e6', interval="hour"):
    """
    Getting data from the Metry API. The from and to date can be specified, alongside the number of sensors being retrieved and the id(s) of the sensors.
    The id can be either the id of a "tree" or some "meters", if the id is of meters it needs to be on the form {id}%2C{id}... 
    """

    if summed == True:
        if len(id) <= len('614b288ed36b0038600833e6'):
            response = requests.get(
                f"https://app.metry.io/api/v2/consumptions/{id}/{interval}/{frm}-{to}?access_token={metry_key}").json()
        else:
            response = requests.get(
                f"https://app.metry.io/api/2.0/consumptions/sum/{interval}/{frm}-{to}?meters={id}&access_token={metry_key}").json()
        response_list = []
        time_range = pd.date_range(frm, to, freq='H')
        for i in time_range:
            response_list.append({
                'date_time': i,
                'generated_electricity': response['data'][0]['periods'][0]['energy'][time_range.get_loc(i)] / number_of_meters
            })
    elif summed == False:
        response = requests.get(
            f"https://app.metry.io/api/2.0/consumptions/multi/{interval}/{frm}-{to}?meters={id}&access_token={metry_key}").json()
        response_list = []
        id_list = id.split('%2C')
        time_range = pd.date_range(frm, to, freq='H')
        meter_response = []
        for j in range(len(response['data'])):
            meter_response.append({
                'meter_id': id_list[j],
                'generated_electricity': {
                    'generated_electricity': response['data'][j]['periods'][0]['energy'],
                    'date_time': time_range,
                }
            })
        response_list.append(meter_response)
        return pd.DataFrame(response_list)
    return pd.DataFrame(response_list)


def selected_city_ids():
    """
    Getting all the ids from some given city.
    """
    try:
        city = request.form['city']
    except:
        city = request.args.get('city')

    city_id_list = []

    for id in all_ids:
        if all_ids[id]['city'] == city:
            city_id_list.append(id)

    return len(city_id_list), "%2C".join(city_id_list)


def get_ml_diff():
    """
    This function checks if the ML and the actual value differs too much and sends out emails :)
    """
    subs = pd.read_csv('./secret_folder/contact_info.csv')
    if len(subs['id']) != 0:
        for index, entry in subs.iterrows():
            frm = datetime.date.today() - datetime.timedelta(days=38)
            to = datetime.date.today() - datetime.timedelta(days=31)
            summed = False
            city = entry['city']
            email = entry['email']
            ids = ast.literal_eval(entry['id'])
            predictions = []
            for id in ids:
                predictions.append({'pred': [k[0] for k in per_meter_energy_predictor(city, id, frm, to)],
                                    'id': id})
            predictions = pd.DataFrame(predictions)
            id_string = "%2C".join(ids)
            metry_data = get_metry_data(summed, frm.strftime(
                "%Y%m%d"), to.strftime("%Y%m%d"), 1, id_string, 'day')
            for i in range(len(metry_data.columns)):
                meter_id = metry_data.iloc[:, i][0]['meter_id']
                energy = metry_data.iloc[:,
                                         i][0]['generated_electricity']['generated_electricity']
                predicted = predictions.iloc[predictions.index[(
                    predictions['id'] == meter_id)]]['pred']
                days_diff = 0
                # predicted_vals = [i[0] for i in predicted.tolist()]
                print(range(len(metry_data.columns)))
                for i in range(len(energy)):
                    measured_val = energy[i]
                    for pred_val in predicted.iloc[0]:
                        if measured_val is None:
                            break
                        if measured_val > pred_val*1.5 or measured_val < pred_val*0.5:
                            print(days_diff)
                            days_diff = days_diff + 1
                            if days_diff == 6:
                                response = requests.get(
                                    f'https://app.metry.io/api/2.0/meters/{meter_id}?access_token={metry_key}').json()
                                meter_name = response["data"]['name']
                                send_alert(email, meter_name,
                                           city, meter_id, frm, to, gmail, gmail_pass)
                                break
                            break


scheduler = BackgroundScheduler()

scheduler.add_job(get_ml_diff, 'cron', hour=22, minute='*/1')
# scheduler.add_job(get_ml_diff, 'interval', seconds=30)
scheduler.start()


# This code is just spaghetti
# Basically all it does is create the graphs
# TO-DO
# Make it more human readable
@ app.route("/")
def hello():
    """
    Function for displaying the Solveig landing page.
    """

    fig = go.Figure()
    metry_data = get_metry_data()

    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=metry_data['generated_electricity'],
                             line_shape='spline', name="Genomsnittlig Energiproduktion"))

    ML_val = value_predictor('gothenburg')
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[0],
                             line_shape='spline', name="Modell 1 - GBG", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[1],
                             line_shape='spline', name="Modell 2 - GBG", line=dict(dash='dash')))

    ML_val_s = value_predictor('stockholm')
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_s[0],
                             line_shape='spline', name="Modell 1 - STO", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_s[1],
                             line_shape='spline', name="Modell 2 - STO", line=dict(dash='dash')))

    ML_val_u = value_predictor('uppsala')
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_u[0],
                             line_shape='spline', name="Modell 1 - UPP", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_u[1],
                             line_shape='spline', name="Modell 2 - UPP", line=dict(dash='dash')))

    ML_val_m = value_predictor('malmoe')
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_m[0],
                             line_shape='spline', name="Modell 1 - MAL", line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_m[1],
                             line_shape='spline', name="Modell 2 - MAL", line=dict(dash='dash')))
    fig.update_layout(
        title="Effekt per timme",
        xaxis_title="Tid (h)",
        yaxis_title="Effekt (W)"
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("about.html", graphJSON=graphJSON, to=(datetime.date.today() - datetime.timedelta(days=31)), frm=(datetime.date.today() - datetime.timedelta(days=32)))


@ app.route("/selected", methods=['GET'])
def selected_dates():
    """
    This function is run upon date and/ or city selection and collects data between the selected dates and from the selected city. It re-loads the 'about.html'-file with the
    data from the newly selected city and date interval.
    """
    # date_start = request.form['PV-start']
    date_start = request.args.get('PV-start')
    date_end = request.args.get('PV-end')

    # date_end = request.form['PV-end']

    # city = request.form['city']
    city = request.args.get('city')
    ids = request.args.getlist('meters')

    print(date_start, date_end, city, ids)

    id = '614b288ed36b0038600833e6'
    number_of_meters = 87
    summed = True
    stad = "samtliga anläggningar"

    if city != "all_cities":
        number_of_meters, id = selected_city_ids()

    if ids != []:
        if 'none' in "".join(ids):
            number_of_meters, id = selected_city_ids()
        else:
            number_of_meters = len(ids)
            id = "%2C".join(ids)
            summed = False

    if city == 'gothenburg':
        stad = 'Göteborg'
        ml_nr = 2
    if city == 'stockholm':
        stad = 'Stockholm'
        ml_nr = 4
    if city == 'uppsala':
        stad = 'Uppsala'
        ml_nr = 3
    if city == 'malmoe':
        stad = 'Malmö'
        ml_nr = 1

    date_metry_start = date_start.replace("-", "")
    date_metry_end = date_end.replace("-", "")

    fig = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()

    metry_data = get_metry_data(summed,
                                date_metry_start, date_metry_end, number_of_meters, id)
    SMHI_response = requests.get(
        f"https://opendata-download-metanalys.smhi.se/api/category/strang1g/version/1/geotype/point/lon/{get_lat_lon(city)[1]}/lat/{get_lat_lon(city)[0]}/parameter/117/data.json?from={date_start}&to={date_end}&interval=daily").json()
    SMHI_irradiance = np.array([obj['value'] for obj in SMHI_response])

    # TO-DO
    # Fix this mess!!!
    # The problem seems to be with None-Types - I want the code to ignore None-Types!!!!!!!!!!
    if summed == False:
        metry_data = metry_data.dropna(how='any')
        for i in range(len(metry_data.columns)):
            meter_id = metry_data.iloc[:, i][0]['meter_id']
            response = requests.get(
                f'https://app.metry.io/api/2.0/meters/{meter_id}?access_token={metry_key}').json()
            meter_name = response["data"]['name']
            if metry_data.iloc[:, i][0]['generated_electricity']['generated_electricity'] == 0:
                pass
            else:
                fig.add_trace(go.Scatter(x=metry_data.iloc[:, i][0]['generated_electricity']['date_time'], y=metry_data.iloc[:, i][0]['generated_electricity']['generated_electricity'],
                                         line_shape='spline', name=f"Energiproduktion för {meter_name}"))
                ML_val = value_predictor(city, date_start, date_end)
                ML_energy_val = per_meter_energy_predictor(
                    city, meter_id, date_start, date_end)

                """This code is currently not used"""
                # ML_per_meter = per_meter_value_predictor(
                #     city, meter_id, date_start, date_end)
                # if len(ML_per_meter) != 0:
                #     ML_vals = [i[0] for i in ML_per_meter.tolist()]
                #     fig.add_trace(go.Scatter(x=metry_data.iloc[:, i][0]['generated_electricity']['date_time'], y=ML_vals,
                #                              line_shape='spline', name=f"Modell för {meter_name}"))

                if len(ML_energy_val) != 0:
                    ML_energy_val = [i[0] for i in ML_energy_val.tolist()]
                    metry_data.iloc[:, i][0]['generated_electricity']['generated_electricity'] = metry_data.iloc[:,
                                                                                                                 i][0]['generated_electricity']['generated_electricity'][: len(metry_data.iloc[:, i][0]['generated_electricity']['date_time'])]
                    metry_df = pd.DataFrame(
                        metry_data.iloc[:, i][0]['generated_electricity'])
                    metry_df = metry_df.groupby(
                        pd.to_datetime(metry_df['date_time']).dt.date).agg({"generated_electricity": "sum"})
                    metry_df['ML_energy_vals'] = ML_energy_val
                    fig2.add_trace(go.Bar(
                        x=list(metry_df.index.values)[:-1],  y=metry_df['generated_electricity'][:-1], name=f"Elproduktion för {meter_name}"))
                    fig2.add_trace(go.Bar(
                        x=list(metry_df.index.values)[:-1],  y=metry_df['ML_energy_vals'][:-1], name=f"Modell för {meter_name}"))

                    gen_div_irr = metry_df['generated_electricity'][:-1] / \
                        SMHI_irradiance[:-1]
                    fig3.add_trace(go.Scatter(x=list(metry_df.index.values)[
                                   :-1], y=gen_div_irr, mode="lines+markers", line_shape="spline", name=f"Energi/solinstrålning - {meter_name}"))
        fig.add_trace(go.Scatter(x=metry_data.iloc[:, i][0]['generated_electricity']['date_time'], y=ML_val[0],
                                 line_shape='spline', name=f"Modell 1 - {stad}", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data.iloc[:, i][0]['generated_electricity']['date_time'], y=ML_val[ml_nr],
                                 line_shape='spline', name=f"Modell 2 - {stad}", line=dict(dash='dash')))

        fig.update_layout(
            title="Effekt per timme",
            xaxis_title="Tid",
            yaxis_title="Effekt"
        )
        fig2.update_layout(
            title="Energiproduktion per dag",
            xaxis_title="Dag",
            yaxis_title="Energi (Wh)"
        )
        fig3.update_layout(
            title="Energiproduktion/ solinstrålning per dag",
            xaxis_title="Dag",
            yaxis_title="Genererad el/ solinstrålning"
        )
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("about.html", graphJSON=graphJSON, graphJSON2=graphJSON2, graphJSON3=graphJSON3, to=(datetime.date.today() - datetime.timedelta(days=31)), frm=(datetime.date.today() - datetime.timedelta(days=32)))

    elif city == 'all_cities':
        print('all cities')
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=metry_data['generated_electricity'],
                                 line_shape='spline', name="Genomsnittlig Energiproduktion"))

        ML_val = value_predictor('gothenburg', date_start, date_end)
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[0],
                                 line_shape='spline', name="Modell 1 - GBG", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[1],
                                 line_shape='spline', name="Modell 2 - GBG", line=dict(dash='dash')))

        ML_val_s = value_predictor('stockholm', date_start, date_end)
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_s[0],
                                 line_shape='spline', name="Modell 1 - STO", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_s[1],
                                 line_shape='spline', name="Modell 2 - STO", line=dict(dash='dash')))

        ML_val_u = value_predictor('uppsala', date_start, date_end)
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_u[0],
                                 line_shape='spline', name="Modell 1 - UPP", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_u[1],
                                 line_shape='spline', name="Modell 2 - UPP", line=dict(dash='dash')))

        ML_val_m = value_predictor('malmoe', date_start, date_end)
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_m[0],
                                 line_shape='spline', name="Modell 1 - MAL", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val_m[1],
                                 line_shape='spline', name="Modell 2 - MAL", line=dict(dash='dash')))
    else:
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=metry_data['generated_electricity'],
                                 line_shape='spline', name=f"Genomsnittlig Energiproduktion i {stad}"))
        ML_val = value_predictor(city, date_start, date_end)
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[0],
                                 line_shape='spline', name=f"Modell 1 - {stad}", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=metry_data['date_time'], y=ML_val[ml_nr],
                                 line_shape='spline', name=f"Modell 2 - {stad}", line=dict(dash='dash')))

    fig.update_layout(
        title="Effekt per timme",
        xaxis_title="Tid (h)",
        yaxis_title="Effekt (W)"
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("about.html", graphJSON=graphJSON, to=(datetime.date.today() - datetime.timedelta(days=31)), frm=(datetime.date.today() - datetime.timedelta(days=32)))


@ app.route("/signup", methods=['POST'])
def signup():
    city = request.form['city']
    ids = request.form.getlist('meters_alert')
    email = request.form['email']
    df = pd.DataFrame({
        'email': [email],
        'id': [ids],
        'city': [city]
    })
    send_sub_conf(email, gmail, gmail_pass)
    df.to_csv('./secret_folder/contact_info.csv',
              mode='a', header=False, index=False)

    return render_template("signup.html")


@ app.route("/removeme", methods=['POST'])
def removeme():
    email = request.form['email']
    df = pd.read_csv('./secret_folder/contact_info.csv')
    df.drop(df.index[(df["email"] == email)], axis=0, inplace=True)
    df.to_csv('./secret_folder/contact_info.csv', index=False)
    send_remove_conf(email, gmail, gmail_pass)

    return render_template("removeme.html")


@ app.route("/unsub")
def unsub():
    return render_template("unsub.html")


if __name__ == "__main__":
    app.run(debug=True)
