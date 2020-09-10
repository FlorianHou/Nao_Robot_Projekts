import qi
import serial
import sys
from math import pi
import time
# from simple_pid import PID    


session = qi.Session()
session.connect("tcp://10.0.147.226:9559")
motion_service = session.service("ALMotion")
posture_service = session.service("ALRobotPosture")
arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=.1)

x_gesch = 0.08
theta_gesch = (15./180)*pi
motion_service.rest()
posture_service.goToPosture("Stand", 0.6)

alt = ()
neu = ()


def get_Arduino():
    arduino.reset_input_buffer()
    while True:
        datei = arduino.readline()
        # print len(datei)
        if len(datei) == 4 or len(datei) == 3:
            break
    return datei


try:
    while True:
        # arduino.reset_input_buffer()
        # for _ in range(50):
        #     datei = arduino.readline()
        datei = get_Arduino()
        try:
            input = int(datei.rstrip())
        except ValueError:
            motion_service.rest()
            sys.exit()
        if input == 11:
            x = x_gesch
            theta = 0
        if input == 22:
            x = -x_gesch
            theta = 0
        if input == 33:
            x = 0
            theta = theta_gesch
        if input == 44:
            x = 0
            theta = -theta_gesch
        if input == 55:
            x = x_gesch
            theta = theta_gesch
        if input == 66:
            x = x_gesch
            theta = -theta_gesch
        if input == 77:
            x = -x_gesch
            theta = theta_gesch
        if input == 88:
            x = -x_gesch
            theta = -theta_gesch
        if input == 0:
            # x = 0
            # theta = 0
            motion_service.stopMove()

        if input != 0:
            neu = (x, theta)
            print x, theta
            motion_service.move(x, 0, theta)
            alt = neu

except KeyboardInterrupt:
    print "Stop"
    motion_service.rest()
    time.sleep(2)
    sys.exit(1)
