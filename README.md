# HeatMaps
PREVIEW: https://github.com/nn2006/Case-SSO-Realtime-Heatmap

Requirement Summary
In this project, we will develop an Industrial Site Monitoring System that receives real-time data from sensors located at various points within the industrial site. The system will collect temperature, pressure, and steam injection readings and visualize their spatial distribution on a map using heatmaps. Additionally, the system will allow users to navigate through historical data to observe how the readings have changed over time.

#Installation

Just clone the repo and create a new venv inside the folder. Then activate it and use "pip install -r requirements.txt" to install dependencies.
After that, run it as a flask application, set a FLASK_APP enviorment variable as app.py from the venv terminal and use "flask run" command.



And put there your api key and secret.
To charge data use the /chargeData?latitude=&longitude= endpoint.
