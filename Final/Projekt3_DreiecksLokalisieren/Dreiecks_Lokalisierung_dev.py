import qi
import almath
import time
import sys
import uuid
import cv2 as cv
import numpy as np
from math import pi
from functools import wraps
from matplotlib import pyplot as plt

## Decorater log
schritt = 0
gruen_start = (60,100,50)
gruen_end = (80, 255, 255)
blau_start = (100,100,50)
blau_end = (120,255,255)

def log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global schritt
        print "*"*40
        print "Schritt: ", schritt
        schritt += 1
        print func.__name__
        print time.strftime("%x, %X")
        res = func(*args, **kwargs)
        print "*"*60
        return res

    return wrapper

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
        # self.video_navigation.enableReferenceRefresh(True)
        # 2: 640*480
        # self.video_navigation.setResolution(1)
        self.autonomous_service = session.service("ALAutonomousLife")
        self.motion_fertig = False
        self.KamIsBreit = False
        self.switchToGetKon_3 = False

    @log
    def pose_init(self):
        """Zusand ruecksetzen"""
        print "Pose_Init..."
        self.autonomous_service.setState("disabled")
        self.pose_service.goToPosture("Stand", 0.6)
        self.motion_service.setAngles(["HeadPitch"], [5*(pi/180)], 0.1)
        return None

    @log
    def kamBreit(self,CamId = 0,Res = 3,ColorSpace = 13,fps = 30):
        """sammelt Bild aus Nao"""
        print "Kamera vorberiten"
        # 0 ist obere Kamera
        # 3 ist k4VGA,2 ist VGA
        #BGR-13, YUV422-9
        # FPS
        # Parameter ruecksetzen
        self.video_cam.setAllParametersToDefault(CamId)
        # AutoFocus
        self.video_cam.setParameter(CamId,40,0)
        self.video_cam.setParameter(CamId,43,80)
        # AutoExposition
        self.video_cam.setParameter(CamId,11,0)
        self.video_cam.setParameter(CamId,17,800)
        # CameraSharpness
        self.video_cam.setParameter(CamId,24,4)
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

    @log
    def get_image(self):
        """nehme Foto"""
        _ = self.video_cam.getImageRemote(self.subCamId)
        time.sleep(2)
        image_raw = self.video_cam.getImageRemote(self.subCamId)
        image_array_binary = image_raw[6]
        w = image_raw[0]
        h = image_raw[1]
        image_array_byte = bytearray(image_array_binary)
        image_array = np.frombuffer(
            image_array_byte, np.uint8).reshape(h, w, 3)  # array_bgr
        # image_array = cv.imread("Calibieren/datei/foto_1/20200832_A.png")
        cv.imshow("", cv.resize(image_array,(640,480)))
        cv.waitKey(500)
        cv.destroyAllWindows()
        return image_array

    @log
    def stopp_Kamera(self):
        """Kamera stoppen"""
        return self.video_cam.unsubscribe(self.subCamId)

    @log
    def get_kontours(self):
        """Bild bearbeiten und kontours detectieren"""
        print "Kontours detektieren"
        self.img = self.get_image()
        # self.img = cv.imread("klein/Dreiecks/datei/2002.png")
        b,g,r = cv.split(self.img)
        # img_blur = cv.GaussianBlur(self.img, (3, 3), 0)
        img_blur = cv.bilateralFilter(self.img,11,35,35)
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
        # Dreiecks in Gruen
        img_gruen = cv.inRange(img_hsv, gruen_start, gruen_end)
        cv.imshow("", cv.resize(img_gruen, (640,480)))
        cv.waitKey(500)
        cv.destroyAllWindows()
        kernel = np.ones((3, 3), np.uint8)
        if self.img.shape[:2] == (960, 1280):
            img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_OPEN, kernel)
        # open, closing
        # img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_OPEN, kernel)
        # img_gruen = cv.morphologyEx(img_gruen, cv.MORPH_CLOSE, kernel)
        if self.img.shape[:2] == (1920, 2560):
            img_gruen = cv.dilate(img_gruen,kernel,iterations = 1)
        kontours, hierarchy = cv.findContours(
            img_gruen, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        kontours = self.kontours_filter(kontours)
        print str(len(kontours))
        return kontours

    @log
    def get_kontours_2(self):
        self.img = self.get_image()
        # self.img = cv.imread("klein/Dreiecks/datei/2001.png")
        img_blur = cv.medianBlur(self.img,5)
        # BGR To HSV
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
        # Greun
        bit = cv.inRange(img_hsv, gruen_start, gruen_end)
        kernel = np.ones((3,3), np.uint8)
        # Open Close
        bit = cv.morphologyEx(bit, cv.MORPH_CLOSE, kernel)

        kontours, _ = cv.findContours(bit, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        kontours = self.kontours_filter(kontours)
        print str(len(kontours))
        approxCurves = []
        for kontour in kontours:
            approxCurve = cv.approxPolyDP(kontour, 8, True)
            approxCurves.append(approxCurve)
        bit_bgr = cv.cvtColor(bit, cv.COLOR_GRAY2BGR)
        return approxCurves

    @log
    def get_kontours_3(self):
        self.img = self.get_image()
        # self.img = cv.imread("klein/Dreiecks/datei/2001.png")
        blur = cv.medianBlur(self.img,9)
        img_hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        h, w, _ = self.img.shape
        #aussen
        img_gruen = cv.inRange(img_hsv, gruen_start, gruen_end)
        img_blau = cv.inRange(img_hsv, blau_start, blau_end)
        kernel = np.ones((15,15))
        img_blau = cv.morphologyEx(img_blau, cv.MORPH_CLOSE, kernel)
        kernel = np.ones((10,10))
        img_blau = cv.dilate(img_blau, kernel)
        img_bg = cv.bitwise_or(img_blau, img_gruen)
        kernel = np.ones((5,5))
        img_bg = cv.morphologyEx(img_bg, cv.MORPH_OPEN, kernel)
        img_bg = cv.GaussianBlur(img_bg, (3,3), 0)
        edge = cv.Canny(img_bg, 100, 200, 5)
        lines = cv.HoughLines(edge, 1, pi/180, 115)
        cv.imshow("", cv.resize(edge, (640,480)))
        cv.waitKey(500)
        cv.destroyAllWindows()
        aussen = np.array(self.end_Punkt(lines))
        aussen = (aussen.reshape(-1,1,2))
        #Innen
        img_blau = cv.inRange(img_hsv, blau_start, blau_end)
        kernel = np.ones((9,9))
        img_blau = cv.morphologyEx(img_blau, cv.MORPH_CLOSE, kernel)
        kernel = np.ones((5,5))
        img_blau = cv.GaussianBlur(img_blau, (3,3), 0)
        edge = cv.Canny(img_blau, 100, 200, 3)
        lines = cv.HoughLines(edge, 1, pi/180, 50)
        cv.imshow("", cv.resize(edge, (640,480)))
        cv.waitKey(500)
        cv.destroyAllWindows()
        innen = np.array(self.end_Punkt(lines))
        innen = (innen.reshape(-1,1,2))
        kontours = [aussen, innen]
        return kontours
    
    @log
    def linien_Sortieren(self, lines):
        """Linien werden sortiert nach Distanz zu obenlinks."""
        lines_sort = np.argsort(lines, axis=0)[...,1]
        lines = lines[lines_sort[:,0]]
        diff = np.diff(lines[:,0,1])
        result = np.where(np.abs(np.diff(lines[:,0,1]))>0.5)[0]+1
        return lines, result

    @log
    def end_Punkt(self, lines):
        """durch np.linalg.solve rechnet die Schnittepunkten"""
        lines, result = self.linien_Sortieren(lines)
        gruppe_0 = lines[0:result[0]]
        gruppe_1 = lines[result[0]:result[1]]
        gruppe_2 = lines[result[1]:]
        rand_list = []
        for i in (gruppe_0,gruppe_1,gruppe_2):
            rand_list.append(np.sum(i, axis=0)/i.shape[0])
        rand_list.append(rand_list[0])
        xy_list = []
        for i in range(0,3):
            print "+"*40
            rho_1, theta_1 = rand_list[i][0]
            rho_2, theta_2 = rand_list[i+1][0]
            a = np.array([[-1/np.tan(theta_1), 1/np.tan(theta_2)],[1, -1]])
            b = np.array([[-(rho_1*np.sin(theta_1)-rho_2*np.sin(theta_2))],[-(rho_1*np.cos(theta_1)-rho_2*np.cos(theta_2))]])
            print a
            print b
            res = np.linalg.solve(a,b)
            x1, x2 = res
            print x1, x2
            x = rho_1*np.cos(theta_1) + x1
            y = rho_1*np.sin(theta_1) - 1/np.tan(theta_1)*x1
            print "x: ", x
            print "y: ", y
            cv.circle(self.img, (int(x),int(y)), 10, (255,0,0),-1)
            xy_list.append(np.array([x[0],y[0]]))
        return xy_list

    @log
    def get_6Punkten(self):
        """6 Punkten aus DreiecksMark"""
        print "6Punkten suchen"
        result = self.video_cam.setResolution(self.subCamId, 4) # Aufloesung auf "4" gestellt wird
        print "Aufloesung auf '4' stellen.", result
        if self.switchToGetKon_3:
            kontours = self.get_kontours_3()
        else:
            kontours = self.get_kontours()

        # aussen und innen Kontour
        aussen = kontours[-2]
        innen = kontours[-1]
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
        k = self.draw(sp_dict, kontours)
        try:
            if k == ord("n"):
                raise RuntimeError
            else:
                pass
        except RuntimeError:
            print "Punkten sind nicht ordnet"
        return sp_dict

    @log
    def cam_zielen(self,kontours):
        """Kamera zu der Schwerpunk der Dreiecks aimen"""
        print "Zielen...."
        moment = cv.moments(kontours[-2])
        x = moment["m10"]/moment["m00"]
        y = moment["m01"]/moment["m00"]
        h, w, _ = self.img.shape
        x_nor = x/w
        y_nor = y/h

        names = ["Head"]
        angles = list(self.video_cam.getAngularPositionFromImagePosition(0, [x_nor, y_nor]))
        speed = 0.5
        useSensor = False
        self.motion_service.changeAngles(names, angles, speed)
        time.sleep(1)
        print "Zielen auf " , angles
        return None

    @log
    def markFinden(self):
        """Suche Mark"""
        angles = [angle*(pi/180) for angle in range(-90, 120, 30)] # Scannen von -90 Grad zu 90 Grad
        kontours = self.get_kontours()
        if len(kontours) != 2:
            try:
                angles_copy = angles[:]
                for _ in angles:
                    #Random Angle
                    length = len(angles_copy)
                    auswahl = np.random.randint(0,length)
                    angle = angles_copy[auswahl]
                    angles_copy.remove(angle)
                    print angle
                    #Kopf dreht zu gegebne angle
                    self.motion_service.setAngles("Head", [angle, 0.0], 0.5)
                    time.sleep(1)
                    kontours = self.get_kontours()
                    if len(kontours) != 2 and angles_copy == []:
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

    # @log
    # def load_Par(self):
    #     """laden mtx, dist auf"""
    #     with np.load("Zusammen/Dreiecks_Lokalisierung/Datei/zusammen_oben_2000.npz") as file:
    #         mtx, dist = [file[i]
    #                            for i in ("mtx", "dist")]
    #     return mtx, dist
    @log
    def load_Par(self):
        """laden mtx, dist auf"""
        with np.load("Calibieren/choruBoard/oben_charu_2560.npz") as file:
            mtx, dist = [file[i] for i in ("mtx", "dist")]
            dist = None
        return mtx, dist


    @log
    def solve_PnP(self):
        """Lokaliserung rechen"""
        sp_dict = self.get_6Punkten()
        ecks = [sp_dict[i][0].tolist() for i in ["a", "e", "f", "d", "b", "c"]]
        ecks = np.array(ecks, np.float32)  # List zu Array
        objp = np.array([[0, 0, 0], [-1.85, 4.65, 0], [1.85, 4.65, 0],
                         [0, 10.3, 0], [-7.5, 11.25, 0], [7.5, 11.25, 0]], np.float32)/100 # Einheit cm zu m
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
        axis = np.float32([[.1, 0, 0], [0, .1, 0], [0, 0, 0.1]])
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        corner = tuple(ecks_2[0].ravel())
        self.img = cv.line(self.img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
        self.img = cv.line(self.img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
        self.img = cv.line(self.img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
        cv.imshow("Koordiante", cv.resize(self.img, (640,480)))
        k = cv.waitKey(500)
        cv.destroyAllWindows()
        try:
            if k == ord("n"):
                raise RuntimeError
        except RuntimeError:
            print "Koordinate ist False."
            self.error()
            sys.exit(0)
        return rvecs_tr, tvecs_tr

    @log
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

    @log
    def motion(self, Transform):
        """bewegen zu ziel. wenn das Distanz groesser als 30cm ist, wird der Robot nur 1/4 der Distanz in x richtung gehen."""
        print "gehen nach vorner"
        # self.video_navigation.subscribe("VisualCompass_Mittelung")
        x_richtung = -Transform.r1_c4*3/4
        x_transform = almath.Transform_fromPosition(x_richtung,0,0)
        Transform_neu = Transform * x_transform
        xy_2D = almath.pose2DFromTransform(Transform_neu).toVector()
        if Transform.r1_c4 - Transform_neu.r1_c4 > 0.3:
            print "ende Punkt > 0.3 Meter."
            print "xy_2D" , "\n" , xy_2D
            # self.video_navigation.moveTo(xy_2D[0], xy_2D[1],xy_2D[2]) # Vision navi
            self.motion_service.moveTo(xy_2D[0], xy_2D[1],xy_2D[2]) # Ohne Vision
            # self.video_navigation.unsubscribe("VisualCompass_Mittelung")
            self.motion_service.setAngles(["HeadPitch"], [5*(pi/180)], 0.1)
            self.motion_service.setAngles(["HeadYaw"], [0.], 0.1)
        else:
            x_transform = almath.Transform_fromPosition(-0.30,0,0)
            Transform_neu = Transform * x_transform
            xy_2D = almath.pose2DFromTransform(Transform_neu).toVector()
            print "xy_2D" , "\n" , xy_2D
            # self.video_navigation.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            self.motion_service.moveTo(xy_2D[0], xy_2D[1],xy_2D[2])
            # time.sleep(3)
            # self.video_navigation.unsubscribe("VisualCompass_Mittelung")
            self.motion_service.setAngles(["HeadPitch"], [5*(pi/180)], 0.1)
            self.motion_service.setAngles(["HeadYaw"], [0.], 0.1)
            self.motion_fertig = True
        if Transform.r1_c4 - Transform_neu.r1_c4 < 1.:
            self.switchToGetKon_3 = True 
        return None

    @log
    def draw(self,sp_dict, kontours):
        for key, value in sp_dict.items():
            cv.circle(self.img, tuple((value.astype(np.int32)[0])), 8, (0, 0, 255), -1)
            cv.putText(self.img, key, tuple((value.astype(np.int32)[0]+np.array([10,5]))), cv.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
        for contour in kontours:
            cv.drawContours(self.img, [contour.astype(np.int32)], -1, (0, 0, 255), 5)
        # plt.subplot(), plt.imshow(self.img), plt.show()
        cv.imshow("6Punkten", cv.resize(self.img,(640,480)))
        k = cv.waitKey(500)
        cv.destroyAllWindows()
        return k

    @log
    def kontours_filter(self,kontours):
        """testen contours, kleine contour wird abgeloest"""
        kontours_neu = []
        for contour in kontours:
            flaeche = cv.contourArea(contour)
            if self.img.shape[:2] == (960, 1280) and flaeche > 500:
                kontours_neu.append(contour)
            if self.img.shape[:2] == (1920, 2560) and flaeche > 2000:
                kontours_neu.append(contour)
        return kontours_neu

    @log
    def error(self):
        return self.motion_service.rest()

    def run(self):
        self.pose_init()
        self.kamBreit()
        try:
            while True:
                for _ in range(5):
                    # 5 Mals versuchen, um Kontours zu finden.
                    result = self.video_cam.setResolution(self.subCamId, 3)        
                    print "Aufloesung auf '3' stellen.", result
                    kontours_temp = self.get_kontours()
                    if len(kontours_temp) != 2:
                        self.markFinden()
                    else:
                        self.cam_zielen(kontours_temp)
                        break
                Transform = self.robot2Ziel()
                print "robot2Ziel_Transform: \n" , Transform
                print "Postion6D", almath.position6DFromTransform(Transform)
                # time.sleep(3)
                print "motion."
                self.motion(Transform)
                if self.motion_fertig:
                    time.sleep(2)
                    self.pose_service.goToPosture("Stand", 0.6)
                    break
            self.tts.say("Breit zu aufladen")
        except KeyboardInterrupt:
            self.error()
        return None
    
if __name__ == "__main__":
    url = "tcp://10.42.0.95:9559"
    # url = "tcp://10.0.147.226:9559"
    try:
        app = qi.Application(url=url)
    except RuntimeError:
        print"error!!"
        sys.exit(1)
    doSomething = DreiecksLokalisierung(app)
    doSomething.run()
