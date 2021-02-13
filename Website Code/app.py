from flask import Flask, render_template, request
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure
import database as db
import numpy as np
import pandas as pd
from datetime import datetime
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()

#Left to do 
#Filter by number of days code
#fix side graph
#align text center
#add background image
app=Flask(__name__)

plot_data = ['date','temp']
data_days = 1

def table_legend(data):
    color = plot_color[:len(data)]
    data_dic= ['Date']
    for i in range(len(data)-1):
      data_dic.append((list(data_dictionary.keys()))[list(data_dictionary.values()).index(data[i+1])])
    print(color)
    table_data = {'Color Legend': color, 'Data': data_dic}
    table = pd.DataFrame(data = table_data)
    return table

@app.route('/', methods = ['GET', 'POST'])
def homepage():
    global plot_data, data_days, plot_color, data_dictionary

    data_dictionary = {
    'Temperature' : 'temp',
    'DewPoint' : 'dew' ,
    'Humidity' : 'humidity',
    'Pressure' : 'pressure',
    'CO2' : 'CO2',
    'O2' : 'O2',
    'LUX' : 'lux'
    }

    plot_color = ['red', 'green', 'yellow', 'blue', 'navy', 'orange', 'cyan']

    if request.method == 'POST':
        if request.form['submit']=="submit":
            if request.form['action'] == 'Add':
                data_type_web = request.form["data_type"]
                data_days = request.form["numb_days"]
                data_type_database = data_dictionary[data_type_web]
                plot_data.append(data_type_database)

            if request.form['action']=="Remove":
                data_type_web = request.form['data_type']
                data_type_database = data_dictionary[data_type_web]
                plot_data.remove(data_type_database)

            if request.form['action']=='Replace':
                data_type_web = request.form['data_type']
                data_days = int(request.form["numb_days"])
                data_type_database = data_dictionary[data_type_web]
                plot_data = ['date', data_type_database]
        

    #table = table_legend(plot_data)
    title = 'Weather Station'
    #First Plot
    p =plot(plot_data, data_days, plot_color)
    table = table_legend(plot_data)
    script, div = components(p)
    cdn_js0=CDN.js_files[0]
    cdn_js = CDN.js_files[1]
    cdn_css=CDN.css_files
    print("cdn_js:",cdn_js)
    print("cdn_css",cdn_css)

    return render_template('index.html', title = title, script = script,
    div = div, cdn_css=cdn_css, cdn_js=cdn_js, cdn_js0=cdn_js0, 
    table = table.to_html(index = False, justify = 'center'))

def plot(plot_data_fn, data_days_fn, plot_color):
    #data range in days
    end_day = int(db.get_bound("DESC")[2])
    start_day = end_day - data_days_fn + 1

    #Dictionary to get y-label
    label_dictionary = {
    'temp' : 'Temperature (°C)',
    'dew' : 'Dew Point (°C)' ,
    'humidity' : 'Relative Humidity (%)',
    'pressure' : 'Ambient Pressure (Kpa)',
    'CO2' : 'CO2',
    'O2' : 'O2 Concentration (%)',
    'lux' : 'Light Intensity'
    }

    #get time and convert it into datetime type
    time_series = []
    extract_date = []
    extract_data = []
    for i in range(start_day, end_day + 1):
        data = db.read_bydays('date', i)
        extract_date.extend(data)

    for i in range(len(extract_date)):
        time_series.append(datetime.fromisoformat(extract_date[i][0]))

    y_label = label_dictionary[plot_data_fn[1]]
    #plot the figures
    p = figure(plot_width=1400, plot_height=400,x_axis_label='Date/Time', y_axis_label=y_label, x_axis_type="datetime")
    #for i in range(len(plot_data_fn)-1):
    for j in range(start_day, end_day + 1):
        data = db.read_bydays(plot_data_fn[1], j)
        extract_data.extend(data)
    data_plot = np.array(extract_data)
    data_plot = np.ravel(data_plot)
    p.line(time_series,data_plot)

    return p  

if __name__=='__main__':
    app.debug=True
    app.run( port = 5000, debug=True)

#host = '192.168.1.11',