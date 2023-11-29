from flask import Flask , request ,render_template, jsonify,redirect, session
from ldap3 import Server, Connection, ALL, SIMPLE
import folium.plugins as plugins
import pandas as pd 
import os

import csv

import json
import folium
from folium.plugins import HeatMap

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
#secrets = open('secrets.json','r')
#secrets_obj = json.load(secrets)

#Active Directory Acthencation 
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_active_directory(username, password):
            session['logged_in'] = True
             
            return redirect('/drawMap')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error='')
def authenticate_active_directory(username, password):
    server = Server('dc1-arpatechonline.net', get_info=ALL)  # Replace with your domain controller address
    try:
        conn = Connection(server, user=f"{username}@dc1-arpatechonline.net", password=password, authentication=SIMPLE, auto_bind=True)
        if conn.bind():
            conn.unbind()
            return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
    return False
# @app.route('/dashboard')
# def dashboard():
#     if session.get('logged_in'):
#         return render_template('index.html')
#     return redirect('/')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')




@app.route('/drawMap')
def draw_map():
    if session.get('logged_in'):
        map_data = pd.read_csv("./Data/data_01.csv", sep=',')
        #map_data = map_data [(map_data ["ID"] == 31228403)]
        lat = map_data['LATITUDE'].mean()
        lom = map_data['LONGITUDE'].mean()
        startingLocation = [lat, lom]#[39.47, -0.37]
        hmap = folium.Map(location=startingLocation, zoom_start=15)
        max_amount = map_data['STEAM_INJECTION'].max()
        # Convert 'DATE_TIME' column to datetime format
        map_data['RECEIVEDTIME'] = pd.to_datetime(map_data['RECEIVEDTIME'], errors='coerce')

        # Drop rows with NaT (invalid) datetime values
        map_data = map_data.dropna(subset=['RECEIVEDTIME'])

        # Sort the data by date-time
        map_data = map_data.sort_values(by='RECEIVEDTIME')
        # Create a list of features for TimestampedGeoJson
        features = []
        for index, row in map_data.iterrows():
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['LONGITUDE'], row['LATITUDE']],
                },
                'properties': {
                    'time': str(row['RECEIVEDTIME']),  # Format time as required
                    'popup': f"Steam Injection: {row['STEAM_INJECTION']}"  # Additional info in popup
                }
            }
            features.append(feature)

        # Create TimestampedGeoJson layer
        ts_geojson = folium.plugins.TimestampedGeoJson(
            {'type': 'FeatureCollection', 'features': features},
            period='PT1M',  # Interval for time slider
            add_last_point=True,  # Add last data point even after animation ends
            auto_play=True,  # Auto-play the time animation
            loop=True,  # Loop the animation
            max_speed=1,  # Max animation speed
            loop_button=True,  # Show loop button
            time_slider_drag_update=True  # Enable time slider drag update
        )

        # Add TimestampedGeoJson layer to the map
        hmap.add_child(ts_geojson)




        hm_wide = HeatMap( list(zip(map_data.LATITUDE.values, map_data.LONGITUDE.values, map_data.STEAM_INJECTION.values)),
                            min_opacity=0.2,
                            max_val=max_amount,
                            radius=17, blur=15,
                            max_zoom=1)
                    

        # hm = plugins.HeatMapWithTime(map_data, auto_play=True,
        #                      display_index=True,
        #                      gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'},
        #                      index=map_data['RECEIVEDTIME'].tolist(),
        #                      max_opacity=0.8)
        #hm.add_to(hmap)
        # Adds the heatmap element to the map
        
        hmap.add_child(hm_wide)
        #hmap.add_child(hm)
        # Saves the map to heatmap.hmtl
        hmap.save(os.path.join('./templates', 'heatmap.html'))
        #Render the heatmap
        return render_template('heatmap.html')
    return redirect('/')




@app.route('/chargeData')
def charge_data():
    latitude = ''
    longitude = ''
    try:
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
    except:
        return {'code': 400, 'message':'Missing latitude and longitude arguments at the call.'}, 400

    #auth_object = auth.Auth(secrets['key'], secrets['secret'])
    #auth_json = auth_object.auth()
    #bearer = auth_json['access_token']
    #print (bearer)

    contador = 1
    FILE = csv.writer(open('./Data/data_01.csv', 'a')) 
    FILE.writerow(['ID', 'LATITUDE', 'LONGITUDE', 'TEMPERATURE', 'PRESSURE', 'STEAM_INJECTION', 'RECEIVEDTIME'])
    
    #To enhance API security in a way that allows the API to gather telemetry from protected devices.
    
    # while contador <= int(request.args.get('numPags')):
    #     data = ide.get_properties(bearer, 'rent', latitude, longitude, contador)

    #     if data == False:
    #         return  {'code': 200, 'message': 'All available data charged'}, 200

    #     for property in data['elementList']:
    #         new_row = [property['propertyCode'], property['latitude'], property['longitude'], property['temperature'], property['pressure'], property['steam_injection']]
    #         FILE.writerow(new_row)
        
    #     contador += 1
    
    # FILE.close()

    #Limpiamos lineas en blanco
    with open('./Data/data_01.csv') as infile, open('./Data/data_01.csv', 'w') as outfile:
        for line in infile:
            if not line.strip(): continue  # skip the empty line
            outfile.write(line)  # non-empty line. Write it to output

    return {'code': 200, 'message': 'Data charged :D'}, 200
