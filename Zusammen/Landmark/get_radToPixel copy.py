import math
import numpy as np
import cv2 as cv


class LandMarksToPixel():
    """nehme die Datei aus Landmarks auf"""
    def __init__(self, app):
        """Initizieren"""
        app.start()
        session = app.session
        self.memory_service = session.service("ALMemory")
        self.motion_service = session.service("ALMotion")
        self.subscriber = self.memory_service.subscriber("LandmarkDetected")
        self.subscriber.signal.connect(self.FundLandmark)
        self.landmark_detection = session.service("ALLandMarkDetection")
        self.landmark_detection.subscribe("LandmarkDetector", 500, 0.0)
        self.got_4landmark = False
        self.mark_dict = dict()
        motion_service.setAngles()

    def r2p(alpha, beta):
        """Alpha und Beta zu Pixel umwanden"""
        dfov = 67.4  #Grad
        dfov_rad = dfov / 180 * math.pi
        # h und w von Bild
        h, w = img.shape[:2]
        # Pixels in
        d = math.sqrt(h**2 + w**2)
        # Pixels pro Rad
        einheit = d / dfov_rad
        # In Kamera Koordinaten
        alpha_pixel = alpha * einheit
        beta_pixel = beta * einheit
        # In Opencv Koordinaten System
        w_pixel = w / 2 - alpha_pixel
        h_pixel = h / 2 + beta_pixel
        return int(w_pixel), int(h_pixel)

    def FundLandmark(self, datei):
        """Landmarks detektieren"""
        MarkInfo = datei[1]
        if len[MarkInfo] < 4:
            self.got_4landmark = False
            
        elif not self.got_4landmark:
            self.got_4landmark = True
            print "I saw 4 landmarks!"

            for mark_info in MarkInfo:
                alpha = mark_info[0][1]
                beta = mark_info[0][2]
                heading = mark_info[0][5]
                id = mark_info[1]
                self.mark_dict[id] = (alpha, beta)

    def HeadMarkZentierung(self):
        winkel_summe = np.zeros((1,2), np.float)
        for _, winkel in mark_dict.items():
            winkel_array = np.array(winkel)
            winkel_summe = winkel_summe + winkel_array
            names  = ["HeadYaw", "HeadPitch"]
            angles = (winkel_summe/4).tolist()[0]
            fractionMaxSpeed  = 0.05
            try:
                self.motion_service.changeAngles(names, angles, fractionMaxSpeed)
                time.sleep(2)
                return True

            except RuntimeError:
                print "Fehler! Die Rcihtung der Kamera nicht eingestellt werden kann!"
                return False

    def TorsoZentierung(self):
        name            = "CameraTop"
        frame           = motion.FRAME_ROBOT
        useSensorValues = True
        result          = motion_service.getPosition(name, frame, useSensorValues)
        Cam_Top_6D = self.motion_service.getPosition()
        
if __name__ == "__main__":
    app = qi.application(url="")
    img = cv.imread("./klein/4_Landmark/datei/fotos/001.png")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    for info in self.mark_dict.values():
        alpha, beta = info
        position = r2p(alpha, beta)
        print(position)
        positions_list.append(position)
        cv.circle(gray, position, 20, 150 + i, -1)
        i = i + 25
    # cv.imwrite("gray.png", gray)
    cv.imshow("img", gray)
    cv.waitKey(0)
    cv.destroyAllWindows()
