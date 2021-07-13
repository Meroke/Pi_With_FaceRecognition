import serial
import RPi.GPIO as GPIO
# 树莓派和arduino的通信
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)


