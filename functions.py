#!/usr/bin/python3
#coding: utf8
#sensorkal.py
import Adafruit_DHT
import RPi.GPIO as GPIO
import sys
import spidev
from spidev import SpiDev
from analogue.mcp3008 import MCP3008
import time
import pandas as pd
from datetime import datetime, timedelta
from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool
from bokeh.layouts import row, column

import numpy as np
from scipy.interpolate import make_interp_spline

import configparser
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def watering(relay,pump):
  #pass
  strom_sensoren = 5
  # GPIO SETUP
  GPIO.setwarnings(False)                         # Fehlermeldungen deaktivieren
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(relay, GPIO.OUT)
  print("Starting pump(relais) ", str(relay), " for ", str(pump), " seconds.")
  GPIO.output(relay, False)
  time.sleep(pump)
  GPIO.output(relay, True)
  time.sleep(1)

def check_and_water(sensor, relais, duerr, trocken, feucht):
    water = 0
    if duerr[0] <= sensor <= duerr[1]:
        watering(relais, duerr[2])
        water = 1
    elif trocken[0] <= sensor <= trocken[1]:
        watering(relais, trocken[2])
        water = 1
    elif feucht[0] <= sensor <= feucht[1]:
        watering(relais, feucht[2])
        water = 1
    return 0

def load_sensor_config():
    config = configparser.ConfigParser()
    config.read('//home//ben//wateringSystem//sensor_config.ini')
    return config

def calc_percent_hum(configDataAir,configDataWater, measuredData):
  #value = (configData - data) / configData *100
  value = round(100-((measuredData - configDataWater) / (configDataAir - configDataWater)) * 100,1)
#  print("ConfigDate: ", configData, ", Data: ", data)
  return value

def createHtml():
  df = pd.read_csv('//home//ben//wateringSystem//datenlog.log', header=None, names=['Date', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Temperature', 'Humidity', 'Pump1', 'Pump2', 'Pump3', 'Pump4', 'Pump5', 'Pump6'])

  # Convert 'Date' column to datetime object
  df['Date'] = pd.to_datetime(df['Date'])

  # Calculate the start date (one week ago from today)
  start_date = datetime.now() - timedelta(days=1)

  # Filter DataFrame to include only rows within the desired date range
  df1 = df[df['Date'] >= start_date]

  #df1 = remove_non_increasing_dates(df1)

  # Create a new Bokeh figure
  p = figure(x_axis_type="datetime", title="Sensor Readouts Over Time", width=1200, height=400, y_range=[-10,100])

  # Add lines for each sensor
  #df1 = smoothData(df1)
  p.line(x='Date', y='Sensor1', source=df1, legend_label="Sensor 1 [%]", line_width=2, line_color="blue")
  p.line(x='Date', y='Sensor2', source=df1,legend_label="Sensor 2 [%]", line_width=2, line_color="green")
  p.line(x='Date', y='Sensor3', source=df1,legend_label="Sensor 3 [%]", line_width=2, line_color="red")
  p.line(x='Date', y='Sensor4', source=df1,legend_label="Sensor 4 [%]", line_width=2, line_color="orange")
  p.line(x='Date', y='Sensor5', source=df1,legend_label="Sensor 5 [%]", line_width=2, line_color="purple")
  p.line(x='Date', y='Sensor6', source=df1,legend_label="Sensor 6 [%]", line_width=2, line_color="brown")

  p.line(x='Date', y='Temperature', source=df1, legend_label="Temperature [°C]", line_width=2, line_color='blue', line_dash='dotted')
  p.line(x='Date', y='Humidity', source=df1, legend_label="Humidity [%]", line_width=2, line_color='red', line_dash='dotted')

  filtered_df = df[df['Pump1'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor1'], marker="circle", color="blue", size=12) 

  filtered_df = df[df['Pump2'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor2'], marker="circle", color="green", size=12) 

  filtered_df = df[df['Pump3'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor3'], marker="circle", color="red", size=12) 

  filtered_df = df[df['Pump4'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor4'], marker="circle", color="orange", size=12) 

  filtered_df = df[df['Pump5'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor5'], marker="circle", color="purple", size=12) 

  filtered_df = df[df['Pump6'] == 1]
  if not filtered_df.empty:
    p.scatter(x=filtered_df['Date'],y=filtered_df['Sensor6'], marker="circle", color="brown", size=12) 

  # Add legend
  p.legend.location = "top_left"
  p.legend.click_policy = "hide"

  # Set plot properties
  p.xaxis.axis_label = "Date"
  p.yaxis.axis_label = "Sensor Values"

  # Enable grid
  p.xgrid.grid_line_color = 'gray'
  p.ygrid.grid_line_color = 'gray'
  p.xgrid.grid_line_dash = [6, 4]
  p.ygrid.grid_line_dash = [6, 4]

  tooltips = [("Date", "@Date{%F %H:%M:%S}"),
           ("Sensor1: ","@Sensor1 %"),
           ("Sensor2: ","@Sensor2 %"),
           ("Sensor3: ","@Sensor3 %"),
           ("Sensor4: ","@Sensor4 %"),
           ("Sensor5: ","@Sensor5 %"),
           ("Sensor6: ","@Sensor6 %"),
           ("Temperature: ","@Temperature °C"),
           ("Humidity: ","@Humidity %")]

  hover = HoverTool(
    tooltips = tooltips,
    formatters = {'@Date': 'datetime'},
    mode = 'mouse'
  )
  p.add_tools(hover)

  #######
  start_date = datetime.now() - timedelta(days=7)

  # Filter DataFrame to include only rows within the desired date range
  df7 = df[df['Date'] >= start_date]

  # Create a new Bokeh figure
  p2 = figure(x_axis_type="datetime", title="Sensor Readouts Over Time", width=1200, height=400, y_range=[-10,100])

  # Add lines for each sensor
  p2.line(x='Date', y='Sensor1', source=df7, legend_label="Sensor 1 [%]", line_width=2, line_color="blue")
  p2.line(x='Date', y='Sensor2', source=df7,legend_label="Sensor 2 [%]", line_width=2, line_color="green")
  p2.line(x='Date', y='Sensor3', source=df7,legend_label="Sensor 3 [%]", line_width=2, line_color="red")
  p2.line(x='Date', y='Sensor4', source=df7,legend_label="Sensor 4 [%]", line_width=2, line_color="orange")
  p2.line(x='Date', y='Sensor5', source=df7,legend_label="Sensor 5 [%]", line_width=2, line_color="purple")
  p2.line(x='Date', y='Sensor6', source=df7,legend_label="Sensor 6 [%]", line_width=2, line_color="brown")

  p2.line(x='Date', y='Temperature', source=df7, legend_label="Temperature [°C]", line_width=2, line_color='blue', line_dash='dotted')
  p2.line(x='Date', y='Humidity', source=df7, legend_label="Humidity [%]", line_width=2, line_color='red', line_dash='dotted')

  filtered_df = df7[df7['Pump1'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor1'], marker="circle", color="blue", size=12) 

  filtered_df = df7[df7['Pump2'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor2'], marker="circle", color="green", size=12) 

  filtered_df = df7[df7['Pump3'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor3'], marker="circle", color="red", size=12) 

  filtered_df = df7[df7['Pump4'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor4'], marker="circle", color="orange", size=12) 

  filtered_df = df7[df7['Pump5'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor5'], marker="circle", color="purple", size=12) 

  filtered_df = df7[df7['Pump6'] == 1]
  if not filtered_df.empty:
    p2.scatter(x=filtered_df['Date'],y=filtered_df['Sensor6'], marker="circle", color="brown", size=12) 

  # Add legend
  p2.legend.location = "top_left"
  p2.legend.click_policy = "hide"

  # Set plot properties
  p2.xaxis.axis_label = "Date"
  p2.yaxis.axis_label = "Sensor Values"

  # Enable grid
  p2.xgrid.grid_line_color = 'gray'
  p2.ygrid.grid_line_color = 'gray'
  p2.xgrid.grid_line_dash = [6, 4]
  p2.ygrid.grid_line_dash = [6, 4]

  tooltips = [("Date", "@Date{%F %H:%M:%S}"),
           ("Sensor1: ","@Sensor1 %"),
           ("Sensor2: ","@Sensor2 %"),
           ("Sensor3: ","@Sensor3 %"),
           ("Sensor4: ","@Sensor4 %"),
           ("Sensor5: ","@Sensor5 %"),
           ("Sensor6: ","@Sensor6 %"),
           ("Temperature: ","@Temperature °C"),
           ("Humidity: ","@Humidity %")]

  hover = HoverTool(
    tooltips = tooltips,
    formatters = {'@Date': 'datetime'},
    mode = 'mouse'
  )
  p2.add_tools(hover)
  #######

  # Set output file
  layout = column(p, p2)
  output_file("//var//www//html//index.html", title="Grow Plot")

  # Save the plot
  save(layout)

def calibrateSensor(calibCycles):
  strom_sensoren = 5
  relais1 = 11
  relais2 = 13
  relais3 = 15
  relais4 = 16
  relais5 = 18
  relais6 = 22
  # GPIO SETUP
  GPIO.setwarnings(False)                         # Fehlermeldungen deaktivieren
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(strom_sensoren, GPIO.OUT)

  # SENSOREN ABFRAGEN
  GPIO.output(strom_sensoren, GPIO.HIGH)
  time.sleep(3)
  config = configparser.ConfigParser()

  value0, value1, value2, value3, value4, value5, temperature, humidity = readSensors(calibCycles)

  time.sleep(2)
  GPIO.output(strom_sensoren, GPIO.LOW)
  time.sleep(0.5)
  GPIO.cleanup()

  if value0 < 500:
    value0 = int((value1 + value2 + value3 + value4 + value5)/5)
    print("Calibration of Sensor0 did not work: ", str(value0), " Setting to mean value.")
  if value1 < 500:
    value1 = int((value0 + value2 + value3 + value4 + value5)/5)
    print("Calibration of Sensor1 did not work: ", str(value1), " Setting to mean value.")
  if value2 < 500:
    value2 = int((value1 + value0 + value3 + value4 + value5)/5)
    print("Calibration of Sensor2 did not work: ", str(value2), " Setting to mean value.")
  if value3 < 500:
    value3 = int((value1 + value2 + value0 + value4 + value5)/5)
    print("Calibration of Sensor3 did not work: ", str(value3), " Setting to mean value.")
  if value4 < 500:
    value4 = int((value1 + value2 + value3 + value0 + value5)/5)
    print("Calibration of Sensor4 did not work: ", str(value4), " Setting to mean value.")
  if value5 < 500:
    value5 = int((value1 + value2 + value3 + value4 + value0)/5)
    print("Calibration of Sensor5 did not work: ", str(value5), " Setting to mean value.")

  config['Sensor{}'.format(0)] = {'calibration_output': str(value0)}
  config['Sensor{}'.format(1)] = {'calibration_output': str(value1)}
  config['Sensor{}'.format(2)] = {'calibration_output': str(value2)}
  config['Sensor{}'.format(3)] = {'calibration_output': str(value3)}
  config['Sensor{}'.format(4)] = {'calibration_output': str(value4)}
  config['Sensor{}'.format(5)] = {'calibration_output': str(value5)}

  #with open('//home//ben//wateringSystem//sensor_config.ini', 'w') as configfile:
  #  config.write(configfile)

  return value0, value1, value2, value3, value4, value5, temperature, humidity

def readSensors(calibCycles):
  adc_mcp3008 = MCP3008(max_speed_hz=1_000_000)
  DHT_SENSOR = Adafruit_DHT.DHT22
  DHT_PIN = 4
 
  humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
  #print("Temperature: ", temperature, " Humidity: ", humidity )
  temperature = int(round(temperature ,1))
  humidity = int(round(humidity ,1))

  value0 = 0
  value1 = 0
  value2 = 0
  value3 = 0
  value4 = 0
  value5 = 0

  column_names = ['Sensor1','Sensor2','Sensor3','Sensor4','Sensor5','Sensor6']
  df = pd.DataFrame(columns=column_names)

  for x in range(calibCycles):
    raw0 = adc_mcp3008.read_channel(channel=0)
    time.sleep(0.2)
    raw1 = adc_mcp3008.read_channel(channel=1)
    time.sleep(0.2)
    raw2 = adc_mcp3008.read_channel(channel=2)
    time.sleep(0.2)
    raw3 = adc_mcp3008.read_channel(channel=3)
    time.sleep(0.2)
    raw4 = adc_mcp3008.read_channel(channel=4)
    time.sleep(0.2)
    raw5 = adc_mcp3008.read_channel(channel=5)

    row_data = {
        'Sensor1': raw0,
        'Sensor2': raw1,
        'Sensor3': raw2,
        'Sensor4': raw3,
        'Sensor5': raw4,
        'Sensor6': raw5
    }

    # Append the dictionary as a new row to the DataFrame
    df = df.append(row_data, ignore_index=True)
    time.sleep(1)
  print(df)
  # Calculate the mean for each column
  mean_values = df.mean()
  print(mean_values)
  return mean_values['Sensor1'], mean_values['Sensor2'], mean_values['Sensor3'], mean_values['Sensor4'], mean_values['Sensor5'], mean_values['Sensor6'], temperature, humidity

def smoothData(df):
  x = df[['Date']]
  y = df[['Sensor1']]

  # Convert datetime to numerical (timestamp) values for interpolation
  x = x.astype(np.int64) // 10**9  # Convert to seconds since epoch

  # Create a B-spline representation of the curve
  x_smooth = np.linspace(x.min(), x.max(), 300)
  spl = make_interp_spline(x, y, k=3)  # BSpline object
  y_smooth = spl(x_smooth)
  df[['Sensor1']] = y_smooth
  return df

def remove_non_increasing_dates(df):
    # Ensure the Date column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Find the differences between consecutive dates
    date_diff = df['Date'].diff()
    
    # Keep only rows where the date difference is positive (strictly increasing)
    df_strictly_increasing = df[date_diff > pd.Timedelta(0)]
    
    # Always keep the first row, as it has no previous date to compare to
    df_strictly_increasing = pd.concat([df.iloc[[0]], df_strictly_increasing])
    
    return df_strictly_increasing.reset_index(drop=True)
