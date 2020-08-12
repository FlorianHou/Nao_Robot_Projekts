import numpy as np
import almath
import qi
import cv2 as cv
from matplotlib import pyplot as plt
import math
from simple_pid import PID

# 0 ist obere Kamera
CamId = 0
# 3 ist k4VGA,2 ist VGA,1 kQVGA
Res = 1
#BGR-13, YUV422-9
ColorSpace = 13
# FPS
fps = 30



def Kamera_Vorbrereiten():
    video_cam_service = session.service("ALVideoDevice")
    global.nameId_Cam = video_cam_service.subscribeCamera("Kamera_Get", CamId, Res, ColorSpace, fps)
    effector = 43 # Foucs
    video_cam_service.setParameter(CamId,effector,30)
    return video_cam_service

def get_raw(video_cam_service):
    return video_cam_service.getImageRemote(nameId_Cam)


def image_array(raw_datei):
    """Raw_Datei zu BGR_Array"""
    image_array_binary = raw_datei[6]
    w = raw_datei[0]
    h = raw_datei[1]
    image_array_string = str(bytearray(image_array_binary))
    image_array = np.fromstring(image_array_string, np.uint8)
    image_array_bgr = image_array.reshape(h, w, 3)
    return image_array_bgr


def image_array_2(raw_datei):
    """Raw_Datei zu BGR_Array"""
    image_array_binary = raw_datei[6]
    w = raw_datei[0]
    h = raw_datei[1]
    image_array_bin = bytearray(image_array_binary)
    image_array_0 = np.frombuffer(image_array_bin, dtype=np.uint8)
    image_array_1 = np.frombuffer(image_array_binary, dtype=np.uint8)
    image_array_2 = np.fromfile(image_array_binary, dtype=np.uint8)
    image_array_bgr = image_array.reshape(h, w, 3)
    return image_array_bgr


def close_Camera():
    return video_cam_service.unsubscribe(nameId_Cam)


def MittelPunkt_folgen(image):
    h, w = image.shape[:2]
    start_height = h - 5
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    thresh = cv.adaptiveThreshold(image_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    signed_thresh = thresh[start_height].astype(np.int16)
    diff = np.diff(signed_thresh)
    points = where(np.logical_or(diff > 200, diff < 200))
    cv.line(image_rgb, (0,start_height),(w, start_height), (0, 255,0), 1)

    if len(points) > 0 and len(points[0]) > 1:   # schwarze linie gefunden
        middle = (points[0][0] + points[0][-1]) / 2
        cv.circle(image_rgb, (points[0][0], start_height), 2, (255,0,0), -1) # zeichnen rechte grenze
        cv.circle(image_rgb, (points[0][1], start_height), 2, (255,0,0), -1)
        cv.circle(image_rgb, (middle, start_height), 2, (0,0,255), -1)
        exzentierung = middle - w/2
        print exzentierung
        Move(exzentierung)
    else:
        start_height -= 5
        start_height = start_height % h
        no_points_count += 1
        Speed -= 0.01
        if Speed <= 0:
            StopAll()
            break
    return middle, image_rgb


def Move(exzentierung):
    x_Speed = 0.08
    y_Speed = 0
    kp = 0.5
    ki = 0.0
    kd = 0.0
    count = 

    pid = PID(kp,ki,kd, setpoint=0.)
    if firsttime:
        pid.id.output_limits = (-1., 1.)

    rot = (math.pi/4) * pid(exzentierung)
    # rot = kp * (math.pi / 4) * (-exzentierung * 2/ w)
    motion_service.move(x_Speed, y_Speed, rot)


def StopAll():
    motion_service.stopMove()
    motion_service.rest()
    


if __name__ == "__main__":
    session = qi.session()
    session.connect(""tcp://10.0.158.231:9559"")
    motion_service = session.service("ALMotion")
    video_cam_service = Kamera_Vorbrereiten()
    while True:
        raw = get_raw()
        image_array_bgr = image_array(raw)
        middle, image_rgb = MittelPunkt_folgen(image_array_bgr)
        cv.imshow("Linie_Folgen", image_rgb)
        k = cv.waitKey(0)
        if k == ord("q"):
            cv.destroyAllWindows()
            StopAll()
            break
        time.sleep(1)
