import qi
import sys
import math
import time

try:
    app = qi.Application(url="tcp://10.0.158.231:9559")
except RuntimeError:
    print"error!!"
    sys.exit(1)
app.start()
session = app.session
motion = session.service("ALMotion")
pose = session.service("ALRobotPosture")
life = session.service("ALAutonomousLife")
autonomous_service = session.service("ALAutonomousLife")

motion.rest()
# pose.goToPosture("StandInit", 0.5)
# motion.moveTo(0,0,180)
pose.goToPosture("Stand", 0.5)
time.sleep(5)
# autonomous_service.setState("disabled")
motion.setIdlePostureEnabled("Body", False)
motion.rest()
time.sleep(10)
# motion.rest()
# motion.wakeUp()
# life.stopAll()
# motion.setStiffnesses("Body", 1.0)