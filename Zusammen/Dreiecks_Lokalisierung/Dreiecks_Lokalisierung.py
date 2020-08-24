import qi
import almath
import time
import sys
import uuid
import cv2 as cv
import numpy as np
from math import pi
from matplotlib import pyplot as plt


class DrLokalisierung():
    """Lokalisierung durch Dreiecks Mark"""

    def __init__(self, app):
        """initisierung"""
        app.start()
        session = app.session
        self.motion_service = session.service("ALMotion")
        self.memory_service = session.service("ALMemory")
        self.video_cam = session.service("ALVideoDevice")
        self.KamIsBreit = False

    def kamBreit(self):
        """sammelt Bild aus Nao"""

        # 0 ist obere Kamera
        CamId = 0
        # 3 ist k4VGA,2 ist VGA
        Res = 3
        #BGR-13, YUV422-9
        ColorSpace = 13
        # FPS
        fps = 30
        # Parameter ruecksetzen
        self.video_cam.setAllParametersToDefault(CamId)
        # AutoFocus
        self.video_cam.setParameter(0, 40, 1)
        # AutoExposition
        self.video_cam.setParameter(0, 11, 1)
        # CameraSharpness
        self.video_cam.setParameter(0, 24, 1)
        # Kamera Oeffnet
        self.video_cam.openCamera(CamId)
        subCamName = uuid.uuid()
        self.subCamId = video_cam.subscribeCamera(subCamName, CamId, Res,
                                                  ColorSpace, fps)
        # Stand testen
        if self.video_cam.isCameraOpen and subCamId != "":
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
        return image_array

    def stopp_Kamera(self):
        """Kamera stoppen"""
        return self.video_cam.unsubscribe(self.subCamId)

    def get_6Punkten(self):
        """6 Punkten aus DreiecksMark"""
        self.img = self.get_image()
        img_blur = cv.GaussianBlur(img, (3, 3), 0)
        # img_blur = cv.bilateralFilter(img,11,75,75)
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
        # Dreiecks in Gruen
        img_gruen = cv.inRange(img_hsv, (60, 100, 60), (80, 255, 255))
        # open, closing
        kernel = np.ones((3, 3), np.uint8)
        img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_OPEN, kernel)
        img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_CLOSING, kernel)
        contours, hierarchy = cv.findConours(
            img_gruen, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
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
        return sp_dict

    def load_Par(self):
        """laden mtx, dist auf"""
        with np.load("datei/Kam_Parameter/oben_960.npz") as file:
            mtx, dist, _, _ = [file[i]
                               for i in ("mtx", "dist", "rvecs", "tvecs")]
            return mtx, dist

    def solve_PnP(self):
        """Lokaliserung rechen"""
        sp_dict = self.get_6Punkten()
        ecks = [sp_dict[i][0].tolist() for i in ["a", "e", "f", "d", "b", "c"]]
        ecks = np.array(ecks, np.float32)  # List zu Array
        objp = np.array([[0, 0, 0], [-2.9, 4.7, 0], [2.9, 4.7, 0],
                         [0, 10.3, 0], [-7.5, 11.2, 0], [7.5, 11.2, 0]], np.float32)
        b, g, r = cv.split(self.img)
        criteria = (cv.TERM_CRITERIA_EPS +
                    cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        ecks_2 = cv.cornerSubPix(g, ecks, (5, 5), (-1, -1), criteria)
        mtx, dist = self.load_Par()
        ret, rvecs, tvecs = cv.solvePnP(
            objp, ecks_2, mtx, dist, flags=cv.SOLVEPNP_IPPE)
        # RotationsVektor zu Rotationstransform
        rvecs_tr = np.array(cv.Rodrigues(rvecs)[0])
        tvecs_tr = np.array(tvecs)/100  # cm zu m
        return rvecs_tr, tvecs_tr

    def Robot2Ziel(self):
        """Transform von Robot nach Ziel"""
        RotZ_1 = almath.Transform.fromRotZ(-pi/2)
        RotX_1 = almath.Transform.fromRotX(-pi/2)
        RotY_2 = almath.Transform.fromRotY(-pi/2)
        RotX_2 = almath.Transform.fromRotX(pi/2)
        joinPart = "CameraTop"
        # Koordinate ist unter Fuss
        Koordinate = 2
        ValueAusSensor = True
        robot2camROB = motion_service.getTransform(joinPart,
                                                   Koordinate,
                                                   ValueAusSensor)
        robot2camROB = almath.Transform(robot2camROB)
        rvecs_tr, tvecs_tr = self.solve_PnP()
        cam2zielOP = np.hstack((rvecs_tr, tvecs_tr))
        cam2zielOP = almath.Transform(cam2zielOP.flatten())
        robot2camOP = robot2camROB * RotZ_1 * RotX_1
        robot2zielOP = robot2camOP * cam2zielOP
        self.robot2zielROB = robot2zielOP * RotY_2 * RotX_2
        return None

    def motion(self, Transform):
        """bewegen zu ziel"""
        self.


