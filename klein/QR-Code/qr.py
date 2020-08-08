import qi
import time
import argparse
import sys

class QR():
    """QR Code identifiziern und poistionieren"""

    def __init__(self,app):
        """Initiern"""
        app.start()
        session = app.session
        #Services
        self.memory_service = session.service("ALMemory")
        self.qr_service = session.service("ALBarcodeReader")
        self.motion_service = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")
        self.tts_service = session.service("ALTextToSpeech")
        # Subscribe
        self.subscriber = self.memory_service.subscriber("BarcodeReader/BarcodeDetected")
        self.subscriber.signal.connect(self.dosomething)
        self.qr_service.subscribe("test")

    def dosomething(self, temp):
        self.datei = temp[:]
        print "QR: " + str(len(self.datei))
        for info in self.datei:
            print "Datei:" + str(info[0])
            print "Position" + str(info[1])
        self.tts_service.say("QR Code")
    def run(self):
        """Looping"""
        print "QR ditektieren!"
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print "Untergebrecht durch Nutzer"
            self.qr_service.unsubscribe("qr_identifizieren")
            sys.exit(0)


if __name__ == "__main__":
    try:
        # Initialize qi framework.
        connection_url = "tcp://10.0.158.231:9559"
        app = qi.Application(url=connection_url)
    except RuntimeError:
        print ("Can't connect to Naoqi")
        sys.exit(1)
    qr_run = QR(app)
    qr_run.run()