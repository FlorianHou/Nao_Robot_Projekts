import qi
import numpy as np
import cv2 as cv
import math
from simple_pid import PID
import time

# 0 ist obere Kamera
CamId = 1
# 3 ist k4VGA,2 ist VGA,1 kQVGA
Res = 1
#BGR-13, YUV422-9, Yuv-1
ColorSpace = 1
# FPS
fps = 60


def Kamera_Vorbrereiten():
    video_cam_service = session.service("ALVideoDevice")
    nameId_Cam = video_cam_service.subscribeCamera("Kamera_Get", CamId, Res,
                                                   ColorSpace, fps)
    time.sleep(3)
    motion_service.rest()
    posture_service.goToPosture("Stand", 0.6)
    motion_service.setIdlePostureEnabled("Body", False)
    motion_service.setStiffnesses("Head", 1.0)
    motion_service.setAngles(["Head"], (0., (35 / 180) * math.pi), 0.02)
    video_cam_service.setParameter(CamId, 43, 30)
    video_cam_service.setParameter(CamId, 0, 50)
    video_cam_service.setParameter(CamId, 1, 32)
    video_cam_service.setParameter(CamId, 11, 0)
    video_cam_service.setParameter(CamId, 17, 16)
    return video_cam_service, nameId_Cam


def get_raw():
    return video_cam_service.getImageRemote(nameId_Cam)

def close_Camera():
    return video_cam_service.unsubscribe(nameId_Cam)

def image_array_Y(raw_datei):
    """Raw_Datei zu BGR_Array"""
    image_array_binary = raw_datei[6]
    w = raw_datei[0]
    h = raw_datei[1]
    image_array_string = str(bytearray(image_array_binary))
    image_array = np.fromstring(image_array_string, np.uint8)
    return image_array.reshape(h, w)


def MittelPunkt_folgen_OnlyY(img_Y):
    h, w = img_Y.shape[:2]
    image_bgr = cv.cvtColor(img_Y, cv.COLOR_GRAY2BGR)
    start_height = h - 10
    img_Y = cv.medianBlur(img_Y, 5)
    img_Y = cv.GaussianBlur(img_Y, (3,3), 0)
    ret, thresh = cv.threshold(img_Y, 80, 255, cv.THRESH_BINARY)
    # thresh = cv.adaptiveThreshold(image_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 17, 2)
    signed_thresh = thresh[start_height].astype(np.int16)
    diff = np.diff(signed_thresh)
    points = np.where(np.logical_or(diff > 220, diff < -220))
    cv.line(image_bgr, (0, start_height), (w, start_height), (0, 255, 0), 3)

    if len(points) > 0 and len(points[0]) > 1:  # schwarze linie gefunden
        middle = (points[0][0] + points[0][-1]) / 2
        cv.circle(image_bgr, (points[0][0], start_height), 15, (255, 0, 0),
                  -1)  # zeichnen rechte grenze
        cv.circle(image_bgr, (points[0][-1], start_height), 15, (0, 255, 0),
                  -1)
        cv.circle(image_bgr, (middle, start_height), 15, (0, 0, 255), -1)
        exzentierung = (middle - w / 2) / w # in Prozent
        print exzentierung, middle, w / 2
        Move(exzentierung)
    else:
        start_height -= 5
        start_height = start_height % h
        no_points_count += 1
        if no_points_count > 20:
            StopAll()
    return middle, image_bgr, thresh


def Move(exzentierung):
    x_Speed = 0.02
    y_Speed = 0.0
    #PID
    kp = 0.5
    ki = 0.0
    kd = 0.0
    pid = PID(kp, ki, kd, setpoint=0.)
    global firsttime
    if firsttime:
        pid.output_limits = (-1., 1.)
        firsttime = False

    rot = (math.pi * (20/180)) * pid(exzentierung)
    print rot
    motion_service.move(x_Speed, y_Speed, rot)

    return None


def StopAll():
    motion_service.stopMove()
    time.sleep(5)
    motion_service.rest()


if __name__ == "__main__":
    try:
        app = qi.Application(url="tcp://10.0.158.231:9559")
        app.start()
        session = app.session
        motion_service = session.service("ALMotion")
        posture_service = session.service("ALRobotPosture")
        video_cam_service, nameId_Cam = Kamera_Vorbrereiten()
        time.sleep(5)
        firsttime = True
        no_points_count = 0
        while True:
            start = time.time()
            raw = get_raw()
            image_array = image_array(raw)
            middle, image_bgr, thresh = MittelPunkt_folgen_OnlyY(image_array)
            cv.imshow("Linie_Folgen", image_bgr)
            k = cv.waitKey(1)
            if k == ord("q"):
                cv.destroyAllWindows()
                StopAll()
                break
            # time.sleep(1)
            end = time.time()
            print "Zeit: ", end - start

    except RuntimeError:
        StopAll()
        app.stop()
