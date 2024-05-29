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

from functions import *

#GPIO.cleanup()
sensor_config = load_sensor_config()

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
duerr = [0,15,1]
trocken = [15,25,1]
feucht = [25,35,1]
cann = [0,15, 1]

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

sensor1 = calc_percent_hum(float(sensor_config['Sensor0']['calibration_output_air']),float(sensor_config['Sensor0']['calibration_output_water']),sensor1)
sensor2 = calc_percent_hum(float(sensor_config['Sensor1']['calibration_output_air']),float(sensor_config['Sensor1']['calibration_output_water']),sensor2)
sensor3 = calc_percent_hum(float(sensor_config['Sensor2']['calibration_output_air']),float(sensor_config['Sensor2']['calibration_output_water']),sensor3)
sensor4 = calc_percent_hum(float(sensor_config['Sensor3']['calibration_output_air']),float(sensor_config['Sensor3']['calibration_output_water']),sensor4)
sensor5 = calc_percent_hum(float(sensor_config['Sensor4']['calibration_output_air']),float(sensor_config['Sensor4']['calibration_output_water']),sensor5)
sensor6 = calc_percent_hum(float(sensor_config['Sensor5']['calibration_output_air']),float(sensor_config['Sensor5']['calibration_output_water']),sensor6)

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
    'Humidity':[humidity]
}
datenlog = pd.DataFrame(new_data)
print(datenlog)

# Sensor 1
if duerr[0] <= sensor1 <= duerr[1]:
   watering(relais1,duerr[2])
elif trocken[0] <= sensor1 <= trocken[1]:
   watering(relais1,trocken[2])
elif feucht[0] <= sensor1 <= feucht[1]:
   watering(relais1,feucht[2])

# Sensor 2
if duerr[0] <= sensor2 <= duerr[1]:
   watering( relais2,duerr[2])
elif trocken[0] <= sensor2 <= trocken[1]:
   watering( relais2,trocken[2])
elif feucht[0] <= sensor2 <= feucht[1]:
   watering(relais2,feucht[2])

# Sensor 3
if duerr[0] <= sensor3 <= duerr[1]:
   watering(relais3,duerr[2])
elif trocken[0] <= sensor3 <= trocken[1]:
   watering(relais3,trocken[2])
elif feucht[0] <= sensor3 <= feucht[1]:
   watering(relais3,feucht[2])

# Sensor 4
if duerr[0] <= sensor4 <= duerr[1]:
   watering(relais4,duerr[2])
elif trocken[0] <= sensor4 <= trocken[1]:
   watering(relais4,trocken[2])
elif feucht[0] <= sensor4 <= feucht[1]:
   watering(relais4,feucht[2])

# Sensor 5
if duerr[0] <= sensor5 <= duerr[1]:
   watering(relais5,duerr[2])
elif trocken[0] <= sensor5 <= trocken[1]:
   watering(relais5,trocken[2])
elif feucht[0] <= sensor5 <= feucht[1]:
   watering(relais5,feucht[2])

# Sensor 6
if duerr[0] <= sensor6 <= duerr[1]:
   watering(relais6,duerr[2])
elif trocken[0] <= sensor6 <= trocken[1]:
   watering(relais6,trocken[2])
elif feucht[0] <= sensor6 <= feucht[1]:
   watering(relais6,feucht[2])
#print(zeitpunkt+",{:.1f}".format(sensor1)+",{:.1f}".format(sensor2)+",{:.1f}".format(sensor3)+",{:.1f}".format(sensor4)+",{:.1f}".format(sensor5)+",{:.1f}".format(sensor6))
#datenlog=pd.DataFrame(columns=['Date','Sensor1','Sensor2','Sensor3','Sensor4','Sensor5','Sensor6'])

print("Writing datenlog file.")
datenlog.to_csv(csv_file_path, mode='a', header=False, index=False)

# Create HTML Plot
createHtml()

