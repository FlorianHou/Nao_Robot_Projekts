import qi
import numpy as np
import time
import sys

class Landmark0:
    def __init__(self):

        app = qi.Application(url="tcp://10.0.158.231:9559")
        app.start()
        session = app.session
        self.memory = session.service("ALMemory")
        self.subscriber = self.memory.subscriber("LandmarkDetected")
        self.subscriber.signal.connect(self.doSomething)

        self.landmark_detection = session.service("ALLandMarkDetection")
        self.landmark_detection.subscribe("LandmarkDetector", 500, 0.0)
        self.got_land = False

    def doSomething(self,datei):

        np.savez("klein/4_Landmark/datei/Landmark45.npz", datei = datei)
        print "Saw It"
        time.sleep(5)


    def Run(self):

        try:
            while True:
                time.sleep(1)
            
        except KeyboardInterrupt:
            self.landmark_detection.unsubscribe("LandmarkDetector")
            sys.exit(0)


Landmark = Landmark0()
Landmark.Run()
