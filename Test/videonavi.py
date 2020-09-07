import qi
import almath
from math import pi
import time
try:
    session = qi.Session()
    session.connect("tcp://10.42.1.191:9559")
except RuntimeError:
    print "Error"
#initieren
navi_service = session.service("ALVisualCompass")
pose_service = session.service("ALRobotPosture")
motion_service = session.service("ALMotion")
navi_service.subscribe("navi_1")
#Refersh Bild
navi_service.enableReferenceRefresh(True)
time.sleep(3)
pose_service.goToPosture("Stand", 0.5)
# navi-Weg
navi_service.setResolution(1)
theta = (20./180.)*pi

navi_service.moveTo(4.,1.,theta*2.5)
navi_service.moveTo(2.5,1, theta*2.5)
navi_service.moveTo(3.5,1.,0.0)
#unsub
navi_service.unsubscribe("navi_1")
#Pose Reset
motion_service.rest()



