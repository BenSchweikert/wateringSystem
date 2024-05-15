#!/usr/bin/python3
#coding: utf8
#sensorkal.py
import RPi.GPIO as GPIO
import sys
import spidev
from spidev import SpiDev
import time

from functions import *

value0, value1, value2, value3, value4, value5 = calibrateSensor(5)

# Maximalwert eintragen (nie mehr als 1023!)
max = 1023
# Ausgabe
print ("Sensor 1: ",value0," / ",round( ((max - value0) / max * 100),2), "%")
print ("Sensor 2: ",value1," / ",round( ((max - value1) / max * 100),2), "%")
print ("Sensor 3: ",value2," / ",round( ((max - value2) / max * 100),2), "%")
print ("Sensor 4: ",value3," / ",round( ((max - value3) / max * 100),2), "%")
print ("Sensor 5: ",value4," / ",round( ((max - value4) / max * 100),2), "%")
print ("Sensor 6: ",value5," / ",round( ((max - value5) / max * 100),2), "%")

