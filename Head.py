import qi
import almath
import numpy as np
import time
import math

session = qi.Session()
session.connect("tcp://10.0.158.231:9559")

motion_service = session.service("ALMotion")
posture_service = session.service("ALRobotPosture")
autonomous_service = session.service("ALAutonomousLife")

motion_service.setStiffnesses("Head", 1.0)
# motion_service.wakeUp()
# autonomous_service.setState("disabled")

effector = ["HeadYaw","HeadPitch"]
angeles = [0.0,20*math.pi/180]
fractionMaxSpeed = 0.1

motion_service.setAngles(effector, angeles, fractionMaxSpeed)

time.sleep(5)

