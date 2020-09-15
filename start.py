import qi
import sys
import math
import time

try:
    app = qi.Application(url="tcp://10.0.147.226:9559")
    # app = qi.Application(url="tcp://10.0.147.226:9559")
except RuntimeError:
    print"error!!"
    sys.exit(1)
app.start()
session = app.session
motion = session.service("ALMotion")
pose = session.service("ALRobotPosture")
life = session.service("ALAutonomousLife")
autonomous_service = session.service("ALAutonomousLife")
autonomous_service.setState("disabled")

motion.rest()

# pose.goToPosture("StandInit", 0.5)
# autonomous_service.setState("disabled")


# pose.goToPosture("Stand", 0.5)
# motion.setAngles(["HeadPitch"], [10*(math.pi/180)], 0.1)


time.sleep(2)
# pose.goToPosture("Stand", 0.5)
# life.stopAll()
# motion.setIdlePostureEnabled("Body", False)
# motion.rest()
# time.sleep(10)
# motion.rest()
# motion.wakeUp()
# life.stopAll()
# motion.setStiffnesses("Body", 1.0)