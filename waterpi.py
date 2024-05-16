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

from functions import *

# CLASS & FUNCTIONS
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
           #print("Debug RawDataValue: ", data)
           #per = (680 - data) / 680 * 100               # maximalen Wert testen und 2x eintragen, zB 918; Wert kann nie mehr als 1023 sein!
           #return per
           return data
        else:
           return 0
    def close(self):
        self.spi.close()

#GPIO.cleanup()
sensor_config = load_sensor_config()

# LOG
zeitpunkt = strftime("%Y-%m-%d %H:%M:00", time.localtime())
sys.stdout = open("//home//ben//wateringSystem//datenlog.log", "a")


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
duerr = [0,15,15]
trocken = [15,25,10]
feucht = [25,35,5]
cann = [0,15, 15]

sensor1, sensor2, sensor3, sensor4, sensor5, sensor6 = readSensors(3) # Anzahl der Zyklen

sensor1 = calc_percent_hum(float(sensor_config['Sensor0']['calibration_output']),sensor1)
sensor2 = calc_percent_hum(float(sensor_config['Sensor1']['calibration_output']),sensor2)
sensor3 = calc_percent_hum(float(sensor_config['Sensor2']['calibration_output']),sensor3)
sensor4 = calc_percent_hum(float(sensor_config['Sensor3']['calibration_output']),sensor4)
sensor5 = calc_percent_hum(float(sensor_config['Sensor4']['calibration_output']),sensor5)
sensor6 = calc_percent_hum(float(sensor_config['Sensor5']['calibration_output']),sensor6)

if sensor1 < 0:
  sensor1 = 0
if sensor2 < 0:
  sensor2 = 0
if sensor3 < 0:
  sensor3 = 0
if sensor4 < 0:
  sensor4 = 0
if sensor5 < 0:
  sensor5 = 0
if sensor6 < 0:
  sensor6 = 0

#time.sleep(1)
#GPIO.output(strom_sensoren, GPIO.LOW)
#time.sleep(0.5)


#print(zeitpunkt+"; "+text1+"; {:.1f}%".format(sensor1))
if duerr[0] <= sensor1 <= duerr[1]:
   watering(relais1,duerr[2])
elif trocken[0] <= sensor1 <= trocken[1]:
   watering(relais1,trocken[2])
elif feucht[0] <= sensor1 <= feucht[1]:
   watering(relais1,feucht[2])

#print(zeitpunkt+"; "+text2+"; {:.1f}%".format(sensor2))
if duerr[0] <= sensor2 <= duerr[1]:
   watering(relais2,duerr[2])
elif trocken[0] <= sensor2 <= trocken[1]:
   watering(relais2,trocken[2])
elif feucht[0] <= sensor2 <= feucht[1]:
   watering(relais2,feucht[2])

#print(zeitpunkt+"; "+text3+"; {:.1f}%".format(sensor3))
if duerr[0] <= sensor3 <= duerr[1]:
   watering(relais3,duerr[2])
elif trocken[0] <= sensor3 <= trocken[1]:
   watering(relais3,trocken[2])
elif feucht[0] <= sensor3 <= feucht[1]:
   watering(relais3,feucht[2])

#print(zeitpunkt+"; "+text4+"; {:.1f}%".format(sensor4))
if duerr[0] <= sensor4 <= duerr[1]:
   watering(relais4,duerr[2])
elif trocken[0] <= sensor4 <= trocken[1]:
   watering(relais4,trocken[2])
elif feucht[0] <= sensor4 <= feucht[1]:
   watering(relais4,feucht[2])

#print(zeitpunkt+"; "+text5+"; {:.1f}%".format(sensor5))
if duerr[0] <= sensor5 <= duerr[1]:
   watering(relais5,duerr[2])
elif trocken[0] <= sensor5 <= trocken[1]:
   watering(relais5,trocken[2])
elif feucht[0] <= sensor5 <= feucht[1]:
   watering(relais5,feucht[2])

#print(zeitpunkt+"; "+text6+"; {:.1f}%".format(sensor6))
if duerr[0] <= sensor6 <= duerr[1]:
   watering(relais6,duerr[2])
elif trocken[0] <= sensor6 <= trocken[1]:
   watering(relais6,trocken[2])
elif feucht[0] <= sensor6 <= feucht[1]:
   watering(relais6,feucht[2])
#print(zeitpunkt+",{:.1f}%".format(sensor1)+",{:.1f}%".format(sensor2)+",{:.1f}%".format(sensor3)+",{:.1f}%".format(sensor4)+",{:.1f}%".format(sensor5)+",{:.1f}%".format(sensor6))
#print(zeitpunkt+","+str(sensor1)+","+str(sensor2)+","+str(sensor3)+","+str(sensor4)+","+str(sensor5)+","+str(sensor6))
print(zeitpunkt+",{:.1f}".format(sensor1)+",{:.1f}".format(sensor2)+",{:.1f}".format(sensor3)+",{:.1f}".format(sensor4)+",{:.1f}".format(sensor5)+",{:.1f}".format(sensor6))

# Create HTML Plot
createHtml()

