from flask import Flask , request ,render_template, jsonify,redirect, session
from ldap3 import Server, Connection, ALL, SIMPLE
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
             #return render_template('index.html')
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
@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        return render_template('index.html')
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')




@app.route('/drawMap')
def draw_map():
    if session.get('logged_in'):
        map_data = pd.read_csv("./Data/data_01.csv", sep=',')
        map_data = map_data [(map_data ["ID"] == 31228403)]
        lat = map_data['LATITUDE'].mean()
        lom = map_data['LONGITUDE'].mean()
        startingLocation = [lat, lom]#[39.47, -0.37]
        hmap = folium.Map(location=startingLocation, zoom_start=15)
        max_amount = map_data['STEAM_INJECTION'].max()
        hm_wide = HeatMap( list(zip(map_data.LATITUDE.values, map_data.LONGITUDE.values, map_data.STEAM_INJECTION.values)),
                            min_opacity=0.2,
                            max_val=max_amount,
                            radius=17, blur=15,
                            max_zoom=1)

        # Adds the heatmap element to the map
        hmap.add_child(hm_wide)
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
    FILE.writerow(['ID', 'LATITUDE', 'LONGITUDE', 'TEMPERATURE', 'PRESSURE', 'STEAM_INJECTION'])

    while contador <= int(request.args.get('numPags')):
        data = ide.get_properties(bearer, 'rent', latitude, longitude, contador)

        if data == False:
            return  {'code': 200, 'message': 'All available data charged'}, 200

        for property in data['elementList']:
            new_row = [property['propertyCode'], property['latitude'], property['longitude'], property['temperature'], property['pressure'], property['steam_injection']]
            FILE.writerow(new_row)
        
        contador += 1
    
    FILE.close()

    #Limpiamos lineas en blanco
    with open('./Data/data_01.csv') as infile, open('./Data/data_01.csv', 'w') as outfile:
        for line in infile:
            if not line.strip(): continue  # skip the empty line
            outfile.write(line)  # non-empty line. Write it to output

    return {'code': 200, 'message': 'Data charged :D'}, 200
