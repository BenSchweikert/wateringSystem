#!/usr/bin/python3
#coding: utf8
#sensorkal.py
import RPi.GPIO as GPIO
import sys
import spidev
from spidev import SpiDev
import time
import pandas as pd
from datetime import datetime
from bokeh.plotting import figure, output_file, save

import configparser

class MCP3008:
    def __init__(self, bus = 0, device = 0):
        self.bus, self.device = bus, device
        self.spi = SpiDev()
        self.open()

    def open(self):
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 1000000                 # ab Raspbian-Version "Buster" erforderlich!

    def read(self, channel = 0):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        if 0<=adc[1]<=3:
           data = ((adc[1]&3)<<8)+adc[2]
           return data
        else:
           return 0

    def close(self):
        self.spi.close()

def watering(relay,pump):
    pass
    #print("Starting pump(relais) ", str(relay), " for ", str(pump), " seconds.")
    #GPIO.output(relay, False)
    #time.sleep(pump)
    #GPIO.output(relay, True)
    #time.sleep(1)

def load_sensor_config():
    config = configparser.ConfigParser()
    config.read('//home//ben//wateringSystem//sensor_config.ini')
    return config

def calc_percent_hum(configData,data):
  #(680 - data) / 680 * 100
  value = (configData - data) / configData *100
#  print("ConfigDate: ", configData, ", Data: ", data)
  return value

def createHtml():
  df = pd.read_csv('//home//ben//wateringSystem//datenlog.log', header=None, names=['Date', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6'])

  # Convert 'Date' column to datetime object
  df['Date'] = pd.to_datetime(df['Date'])

  # Create a new Bokeh figure
  p = figure(x_axis_type="datetime", title="Sensor Readings Over Time")

  # Add lines for each sensor
  p.line(df['Date'], df['Sensor1'], legend_label="Sensor 1", line_width=2, line_color="blue")
  p.line(df['Date'], df['Sensor2'], legend_label="Sensor 2", line_width=2, line_color="green")
  p.line(df['Date'], df['Sensor3'], legend_label="Sensor 3", line_width=2, line_color="red")
  p.line(df['Date'], df['Sensor4'], legend_label="Sensor 4", line_width=2, line_color="orange")
  p.line(df['Date'], df['Sensor5'], legend_label="Sensor 5", line_width=2, line_color="purple")
  p.line(df['Date'], df['Sensor6'], legend_label="Sensor 6", line_width=2, line_color="brown")

  # Add legend
  p.legend.location = "top_left"

  # Set plot properties
  p.xaxis.axis_label = "Date"
  p.yaxis.axis_label = "Sensor Value"

  # Set output file
  output_file("//var//www//html//index.html")

  # Save the plot
  save(p)

def calibrateSensor(calibCycles):
  config = configparser.ConfigParser()
  # PINS FESTLEGEN
  strom_sensoren = 5
  # GPIO SETUP
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(strom_sensoren, GPIO.OUT)

  # FÜHLER ABFRAGEN
  GPIO.output(strom_sensoren, GPIO.HIGH)
  time.sleep(3)
  
  value0 = 0
  value1 = 0
  value2 = 0
  value3 = 0
  value4 = 0
  value5 = 0

  adc = MCP3008()
  
  for x in range(calibCycles):
    #print("Calib. Iteration running: ", x+1)
    raw0 = adc.read( channel = 0 ) # Den auszulesenden Channel kannst du natürlich anpassen
    raw1 = adc.read( channel = 1 ) # Den auszulesenden Channel kannst du natürlich anpassen
    raw2 = adc.read( channel = 2 ) # Den auszulesenden Channel kannst du natürlich anpassen
    raw3 = adc.read( channel = 3 ) # Den auszulesenden Channel kannst du natürlich anpassen
    raw4 = adc.read( channel = 4 ) # Den auszulesenden Channel kannst du natürlich anpassen
    raw5 = adc.read( channel = 5 ) # Den auszulesenden Channel kannst du natürlich anpassen
    value0 = value0 + raw0
    value1 = value1 + raw1
    value2 = value2 + raw2
    value3 = value3 + raw3
    value4 = value4 + raw4
    value5 = value5 + raw5
    print("Calib. Iteration done:", x+1, " -> ", raw0, " ", raw1, " ", raw2, " ", raw3, " ", raw4, " ", raw5)
    time.sleep(1)
#  print("Calib. Iterations per Sensor: ", x+1)
  value0 = int(round(value0 / (x+1),0))
  value1 = int(round(value1 / (x+1),0))
  value2 = int(round(value2 / (x+1),0))
  value3 = int(round(value3 / (x+1),0))
  value4 = int(round(value4 / (x+1),0))
  value5 = int(round(value5 / (x+1),0))

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

  with open('sensor_config.ini', 'w') as configfile:
    config.write(configfile)

  time.sleep(2)
  GPIO.output(strom_sensoren, GPIO.LOW)
  time.sleep(0.5)
  GPIO.cleanup()
  return value0, value1, value2, value3, value4, value5
