#!/usr/bin/python3
#coding: utf8
#waterpi.py

import RPi.GPIO as GPIO
import sys
import spidev
from spidev import SpiDev
import time
from time import localtime, strftime
import configparser
from analogue.mcp3008 import MCP3008

#import datetime
from datetime import datetime, timedelta

from functions import *

# Read Date and Time for Watering Trigger. Watering only at 0, 6, 12 and 18:00
now = datetime.now()
current_hour = now.hour
current_minute = now.minute

# Load Sensor Calibration Data
sensor_config = load_sensor_config()
print(sensor_config)

# LOG
zeitpunkt = strftime("%Y-%m-%d %H:%M:00", time.localtime())
csv_file_path = '//home//ben//wateringSystem//datenlog.log'
#sys.stdout = open("//home//ben//wateringSystem//datenlog.log", "a")

# PINS FESTLEGEN
relais1 = 11
relais2 = 13
relais3 = 15
relais4 = 16
relais5 = 18
relais6 = 22

# BEZEICHNUNGEN FESTLEGEN (bezogen auf die Sensoren-Nummer)
text1 = "Pflanze 1"
text2 = "Pflanze 2"
text3 = "Pflanze 3"
text4 = "Pflanze 4"
text5 = "Pflanze 5"
text6 = "Pflanze 6"

# PROZENTWERTE (Minimum,Maximum) und PUMPENDAUER (in Sekunden) FESTLEGEN - [MIN,MAX,DAUER]
duerr = [5,20,120]
trocken = [20,30,90]
feucht = [30,52,60]
#cann = [1,15, 1]

strom_sensoren = 5
# GPIO SETUP
print("Setting up GPIO")
GPIO.setwarnings(False)                         # Fehlermeldungen deaktivieren
GPIO.setmode(GPIO.BOARD)
GPIO.setup(strom_sensoren, GPIO.OUT)

# SENSOREN ABFRAGEN
GPIO.output(strom_sensoren, GPIO.HIGH)
time.sleep(3)
print("Measuring Sensor Data:")
sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, temperature, humidity = readSensors(3) # Anzahl der Zyklen
print("Sensor1: ", sensor1, " Sensor2: ", sensor2, " Sensor3: ", sensor3, " Sensor4: ", sensor4, " Sensor5: ", sensor5, " Sensor6: ", sensor6)

time.sleep(2)
GPIO.output(strom_sensoren, GPIO.LOW)
time.sleep(0.5)
GPIO.cleanup()

sensor1 = calc_percent_hum(float(sensor_config['Sensor0']['calibration_output_air_0']),float(sensor_config['Sensor0']['calibration_output_water_0']),sensor1)
sensor2 = calc_percent_hum(float(sensor_config['Sensor1']['calibration_output_air_1']),float(sensor_config['Sensor1']['calibration_output_water_1']),sensor2)
sensor3 = calc_percent_hum(float(sensor_config['Sensor2']['calibration_output_air_2']),float(sensor_config['Sensor2']['calibration_output_water_2']),sensor3)
sensor4 = calc_percent_hum(float(sensor_config['Sensor3']['calibration_output_air_3']),float(sensor_config['Sensor3']['calibration_output_water_3']),sensor4)
sensor5 = calc_percent_hum(float(sensor_config['Sensor4']['calibration_output_air_4']),float(sensor_config['Sensor4']['calibration_output_water_4']),sensor5)
sensor6 = calc_percent_hum(float(sensor_config['Sensor5']['calibration_output_air_5']),float(sensor_config['Sensor5']['calibration_output_water_5']),sensor6)

if sensor1 < 0:
  sensor1 = 0
else:
   sensor1 = round(sensor1,0)
if sensor2 < 0:
  sensor2 = 0
else:
   sensor2 = round(sensor2,0)
if sensor3 < 0:
  sensor3 = 0
else:
   sensor3 = round(sensor3,0)
if sensor4 < 0:
  sensor4 = 0
else:
   sensor4 = round(sensor4,0)
if sensor5 < 0:
  sensor5 = 0
else:
   sensor5 = round(sensor5,0)
if sensor6 < 0:
  sensor6 = 0
else:
   sensor6 = round(sensor6,0)

# Sensor values
sensors = [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6]
relais = [relais1, relais2, relais3, relais4, relais5, relais6]
pumps = [0, 0, 0, 0, 0, 0]

if current_hour in {0, 6, 12, 18} and current_minute < 15:
   print("Watering is allowed and is checked.")

   for i, (sensor, relai) in enumerate(zip(sensors, relais)):
   #for sensor, relai, in zip(sensors, relais):
      water = check_and_water(sensor, relai, duerr, trocken, feucht)
      pumps[i] = water

pump1 = pumps[0]
pump2 = pumps[1]
pump3 = pumps[2]
pump4 = pumps[3]
pump5 = pumps[4]
pump6 = pumps[5]


# Putting Date together
new_data = {
    'Date': [zeitpunkt],
    'Sensor1': [sensor1],
    'Sensor2': [sensor2],
    'Sensor3': [sensor3],
    'Sensor4': [sensor4],
    'Sensor5': [sensor5],
    'Sensor6': [sensor6],
    'Temperature':[temperature],
    'Humidity':[humidity],
    'Pumpe1':[pump1],
    'Pumpe2':[pump2],
    'Pumpe3':[pump3],
    'Pumpe4':[pump4],
    'Pumpe5':[pump5],
    'Pumpe6':[pump6]
}
datenlog = pd.DataFrame(new_data)
print(datenlog)


print("Writing datenlog file.")
datenlog.to_csv(csv_file_path, mode='a', header=False, index=False)

# Create HTML Plot
print("Creating HTML file.")
createHtml()

