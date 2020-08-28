import qi
import almath
import time
import sys
import uuid
import cv2 as cv
import numpy as np
from math import pi
from matplotlib import pyplot as plt


class DreiecksLokalisierung():
    """Lokalisierung durch Dreiecks Mark"""

    def __init__(self, app):
        """initisierung"""
        app.start()
        session = app.session
        self.motion_service = session.service("ALMotion")
        self.memory_service = session.service("ALMemory")
        self.pose_service = session.service("ALRobotPosture")
        self.tts = session.service("ALTextToSpeech")
        self.video_cam = session.service("ALVideoDevice")
        self.video_navigation = session.service("ALVisualCompass")
        self.video_navigation.enableReferenceRefresh(True)
        # 2: 640*480
        self.video_navigation.setResolution(1)
        self.autonomous_service = session.service("ALAutonomousLife")
        self.motion_fertig = False
        self.KamIsBreit = False

    def pose_init(self):
        """Zusand ruecksetzen"""
        self.autonomous_service.setState("disabled")
        self.pose_service.goToPosture("Stand", 0.6)
        self.motion_service.setAngles(["HeadPitch"], [15*(pi/180)], 0.1)
        return None

    def kamBreit(self):
        """sammelt Bild aus Nao"""

        # 0 ist obere Kamera
        CamId = 0
        # 3 ist k4VGA,2 ist VGA
        Res = 4
        #BGR-13, YUV422-9
        ColorSpace = 13
        # FPS
        fps = 30
        # Parameter ruecksetzen
        self.video_cam.setAllParametersToDefault(CamId)
        # AutoFocushttps://zhuanlan.zhihu.com/p/45404840
        # self.video_cam.setParameter(0, 40, 1)
        # AutoExposition
        # self.video_cam.setParameter(0, 11, 1)
        # CameraSharpness
        # self.video_cam.setParameter(0, 24, 1)

        self.video_cam.setParameter(0,40,0)
        self.video_cam.setParameter(0,43,80)
        self.video_cam.setParameter(0,11,0)
        self.video_cam.setParameter(0,17,700)
        self.video_cam.setParameter(0,24,2)
                # Kamera Oeffnet
        self.video_cam.openCamera(CamId)

        subCamName = str(uuid.uuid4())
        self.subCamId = self.video_cam.subscribeCamera(subCamName, CamId, Res, ColorSpace, fps)
        # Stand testen
        if self.video_cam.isCameraOpen and self.subCamId != "":
            print "Kamera ist Laufend."
            print "subCamId: " + self.subCamId
            self.KamIsBreit = True
        else:
            raise RuntimeError("Kamera kann nicht initiziert werden!")
        return None


    def get_image(self):
        """nehme Foto"""
        image_raw = self.video_cam.getImageRemote(self.subCamId)
        image_array_binary = image_raw[6]
        w = image_raw[0]
        h = image_raw[1]
        image_array_string = str(bytearray(image_array_binary))
        image_array = np.fromstring(
            image_array_string, np.uint8).reshape(h, w, 3)  # array_bgr
        cv.imshow("", image_array)
        cv.waitKey(500)
        cv.destroyAllWindows()
        return image_array

    def stopp_Kamera(self):
        """Kamera stoppen"""
        return self.video_cam.unsubscribe(self.subCamId)

    def kontours(self):
        """Bild bearbeiten und kontours detectieren"""
        self.img = self.get_image()
        b,g,r = cv.split(self.img)
        # img_blur = cv.GaussianBlur(self.img, (3, 3), 0)
        img_blur = cv.bilateralFilter(self.img,11,35,35)
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
        # Dreiecks in Gruen
        img_gruen = cv.inRange(img_hsv, (60, 100, 60), (80, 255, 255))
        # open, closing
        kernel = np.ones((3, 3), np.uint8)
        # img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_OPEN, kernel)
        # img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_CLOSE, kernel)
        img_gruen = cv.dilate(img_gruen,kernel,iterations = 1)
        contours, hierarchy = cv.findContours(
            img_gruen, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        self.contours = self.contours_filter(contours)
        return self.contours

    def get_6Punkten(self):
        """6 Punkten aus DreiecksMark"""
        contours = self.kontours()
        # aussen und innen Kontour
        aussen = contours[-2]
        innen = contours[-1]
        # Dict
        sp_dict = dict()  # SchnittPunkte Dict
        # aussen
        max_auss = np.argmax(aussen, axis=0)
        min_auss = np.argmin(aussen, axis=0)
        sp_dict["a"] = aussen[min_auss[0][1]]
        sp_dict["b"] = aussen[min_auss[0][0]]
        sp_dict["c"] = aussen[max_auss[0][0]]
        # innen
        max_inn = np.argmax(innen, axis=0)
        min_inn = np.argmin(innen, axis=0)
        sp_dict["d"] = innen[max_inn[0][1]]
        sp_dict["e"] = innen[min_inn[0][0]]
        sp_dict["f"] = innen[max_inn[0][0]]
        # zeigen in Windows
        k = self.draw(sp_dict, contours)
        try:
            if k == ord("n"):
                raise RuntimeError
            else:
                pass
        except RuntimeError:
            print "Punkten sind nicht ordnet"
        return sp_dict

    def cam_zielen(self,contours):
        """Kamera zu der Schwerpunk der Dreiecks aimen"""
        print "Zielen...."
        moment = cv.moments(contours[-2])
        x = moment["m10"]/moment["m00"]
        y = moment["m01"]/moment["m00"]
        h, w, _ = self.img.shape
        x_nor = x/w
        y_nor = y/h

        names = ["Head"]
        angles = list(self.video_cam.getAngularPositionFromImagePosition(0, [x_nor, y_nor]))
        speed = 0.2
        useSensor = False
        self.motion_service.changeAngles(names, angles, speed)
        time.sleep(3)
        print "Zielen auf " , angles
        return None

    def markFinden(self):
        """Suche Mark"""
        angles = [angle*(pi/180) for angle in range(-90, 120, 30)] # Scannen von -90 Grad zu 90 Grad
        kontours = self.kontours()
        if len(kontours) != 2:
            try:
                for angle in angles:
                    self.motion_service.setAngles("Head", [angle, 0.0], 0.5)
                    time.sleep(1)
                    kontours = self.kontours()
                    len_nr = len(kontours)
                    if len(kontours) != 2 and angle == angles[-1]:
                        raise RuntimeError
                    if len(kontours) != 2:
                        continue
                    else:
                        print "Mark wird gefunden!"
                        break
            except RuntimeError:
                print "Keine Mark"
                self.error()
                sys.exit(0)
        else:
            print "Mark wird gefunden!"
        # KameraWinkels korrigieren
        self.cam_zielen(kontours)
        return None

    def load_Par(self):
        """laden mtx, dist auf"""
        with np.load("Zusammen/Dreiecks_Lokalisierung/Datei/zusammen_oben_960.npz") as file:
            mtx, dist, _, _ = [file[i]
                               for i in ("mtx", "dist", "rvecs", "tvecs")]
            return mtx, dist

    def solve_PnP(self):
        """Lokaliserung rechen"""
        sp_dict = self.get_6Punkten()
        ecks = [sp_dict[i][0].tolist() for i in ["a", "e", "f", "d", "b", "c"]]
        ecks = np.array(ecks, np.float32)  # List zu Array
        objp = np.array([[0, 0, 0], [-1.85, 4.65, 0], [1.85, 4.65, 0],
                         [0, 10.3, 0], [-7.5, 11.2, 0], [7.5, 11.2, 0]], np.float32)/100
        b, g, r = cv.split(self.img)
        criteria = (cv.TERM_CRITERIA_EPS +
                    cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        ecks_2 = cv.cornerSubPix(g, ecks, (5, 5), (-1, -1), criteria)
        mtx, dist = self.load_Par()
        ret, rvecs, tvecs = cv.solvePnP(
            objp, ecks_2, mtx, dist, flags=cv.SOLVEPNP_IPPE)
        # RotationsVektor zu Rotationstransform
        rvecs_tr = np.array(cv.Rodrigues(rvecs)[0])
        tvecs_tr = np.array(tvecs)  # cm
        # Koordinate zeichnen
        axis = np.float32([[15, 0, 0], [0, -15, 0], [0, 0, 15]]).reshape(-1, 3)
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        corner = tuple(ecks_2[0].ravel())
        self.img = cv.line(self.img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
        self.img = cv.line(self.img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
        self.img = cv.line(self.img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
        cv.imshow("Koordiante", self.img)
        k = cv.waitKey(0)
        cv.destroyAllWindows()
        try:
            if k == ord("n"):
                raise RuntimeError
        except RuntimeError:
            print "Koordinate ist False."
        return rvecs_tr, tvecs_tr

    def robot2Ziel(self):
        """Transform von Robot nach Ziel"""
        RotZ_1 = almath.Transform.fromRotZ(-pi/2)
        RotX_1 = almath.Transform.fromRotX(-pi/2)
        RotY_2 = almath.Transform.fromRotY(-pi/2)
        RotX_2 = almath.Transform.fromRotX(pi/2)
        joinPart = "CameraTop"
        # Koordinate ist unter Fuss
        Koordinate = 2
        ValueAusSensor = True
        robot2camROB = self.motion_service.getTransform(joinPart,
                                                   Koordinate,
                                                   ValueAusSensor)
        robot2camROB = almath.Transform(robot2camROB)
        rvecs_tr, tvecs_tr = self.solve_PnP()
        cam2zielOP = np.hstack((rvecs_tr, tvecs_tr))
        cam2zielOP = almath.Transform(cam2zielOP.flatten())
        robot2camOP = robot2camROB * RotZ_1 * RotX_1
        robot2zielOP = robot2camOP * cam2zielOP
        self.robot2zielROB = robot2zielOP * RotY_2 * RotX_2
        return self.robot2zielROB

    def motion(self, Transform):
        """bewegen zu ziel"""
        self.video_navigation.subscribe("VisualCompass_Mittelung")
        x_richtung = (-Transform.r1_c4/4) * 3
        x_transform = almath.Transform_fromPosition(x_richtung,0,0)
        Transform_neu = Transform * x_transform
        xy_2D = almath.pose2DFromTransform(Transform_neu).toVector()
        if Transform.r1_c4 > 0.3:
            print "xy_2D" , "\n" , xy_2D
            # self.video_navigation.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            self.motion_service.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            time.sleep(3)
            self.video_navigation.unsubscribe("VisualCompass_Mittelung")
        else:
            print "xy_2D" , "\n" , xy_2D
            x_transform = almath.Transform_fromPosition(-0.30,0,0)
            Transform_neu = Transform * x_transform
            xy_2D = almath.pose2DFromTransform(Transform_neu).toVector()
            # self.video_navigation.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            self.motion_service.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            time.sleep(3)
            self.video_navigation.unsubscribe("VisualCompass_Mittelung")
            self.motion_service.setAngles(["HeadPitch"], [15*(pi/180)], 0.1)
            self.motion_service.setAngles(["HeadYaw"], [0.], 0.1)
            self.motion_fertig = True
            return None

    def draw(self,sp_dict, contours):
        for key, value in sp_dict.items():
            cv.circle(self.img, tuple((value[0]).tolist()), 10, (0, 0, 255), -1)
            cv.putText(self.img, key, (-10,5), cv.FONT_HERSHEY_SIMPLEX, 2.0, (0,0,255), 3, )
        for contour in contours:
            cv.drawContours(self.img, [contour], -1, (0, 0, 255), 4)
        cv.imshow("6Punkten", self.img)
        k = cv.waitKey(0)
        cv.destroyAllWindows()
        return k

    def contours_filter(self,contours):
        """testen contours, kleine contour wird abgeloest"""
        contours_neu = []
        for contour in contours:
            flaeche = cv.contourArea(contour)
            if flaeche > 1000:
                contours_neu.append(contour)
        return contours_neu

    def error(self):
        return self.motion_service.rest()

    def run(self):
        self.pose_init()
        self.kamBreit()
        try:
            while True:
                self.markFinden()
                Transform = self.robot2Ziel()
                print "robot2Ziel_Transform: " , Transform
                time.sleep(3)
                self.motion(Transform)
                if self.motion_fertig:
                    time.sleep(3)
                    self.pose_service.goToPosture("Stand", 0.6)
                    break
            self.tts.say("Breit zu aufladen")
        except KeyboardInterrupt:
            self.motion_service.rest()
    
if __name__ == "__main__":
    url = "tcp://10.0.158.231:9559"
    try:
        app = qi.Application(url=url)
    except RuntimeError:
        print"error!!"
        sys.exit(1)
    doSomething = DreiecksLokalisierung(app)
    doSomething.run()
            
