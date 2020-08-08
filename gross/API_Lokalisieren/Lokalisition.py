import qi
import almath
import math
try:
    app = qi.Application(url="tcp://10.0.158.231:9559")
except RuntimeError:
    print "error!!"
    sys.exit(1)
app.start()
session = app.session

motion_service = session.service("ALMotion")
posture_service = session.service("ALRobotPosture")
lokal_service = session.service("ALLocalization")
memory_service = session.service("ALMemory")
autonomous_service = session.service("ALAutonomousLife")
posture_service.goToPosture("StandInit", 0.5)
# motion_service.wakeUp()
# autonomous_service.setState("disabled")
lokal_service.learnHome()
lokal_service.goToPosition([0.5, 0.5, math.pi * 45 / 180])
back = lokal_service.goToHome()

motion_service.rest()
# x, y, theta = lokal_service.getRobotPosition
# print str(x)+"\n"+str(y)+"\n"+str(theta)
