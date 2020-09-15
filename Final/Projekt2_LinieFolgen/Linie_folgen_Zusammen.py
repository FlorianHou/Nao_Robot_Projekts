import qi
import numpy as np
import cv2 as cv
import math
from simple_pid import PID
import time
import uuid
import sys

# 0 ist obere Kamera, 1 ist unter
CamId = 1
# 3 ist k4VGA,2 ist VGA,1 kQVGA
Res = 0
#BGR-13, YUV422-9, Yuv-1
ColorSpace = 0
# FPS
fps = 60

try:
    # app = qi.Application(url="tcp://10.0.158.231:9559")
    app = qi.Application(url="tcp://10.42.0.95:9559")    
    app.start()
    session = app.session
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Kamera_Vorbrereiten
    video_cam_service = session.service("ALVideoDevice")
    subName = str(uuid.uuid4())
    nameId_Cam = video_cam_service.subscribeCamera(subName, CamId, Res,
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
    video_cam_service.setParameter(CamId, 17, 80)
    print "nameId_Cam: ", nameId_Cam

    time.sleep(3)
    firsttime = True
    no_points_count = 0

    kp = 1.2
    ki = 0.
    kd = 0.5
    pid = PID(kp, ki, kd, setpoint=0.)

    while True:
        start = time.time()

        # Get RawImage
        raw = video_cam_service.getImageRemote(nameId_Cam)

        # Raw_Datei zu BGR_Array
        image_array_binary = raw[6]
        w = raw[0]
        h = raw[1]
        image_array_string = bytearray(image_array_binary)
        image_array = np.frombuffer(image_array_string, np.uint8)
        image_array = image_array.reshape(h, w)

        # MittelPunkt_folgen_OnlyY
        img_Y = image_array.copy()
        img_Y = img_Y[:,5:w-5,...]

        h, w = img_Y.shape[:2]
        image_bgr = cv.cvtColor(img_Y, cv.COLOR_GRAY2BGR)
        start_height = h - 4
        img_Y = cv.medianBlur(img_Y, 5)
        img_Y = cv.GaussianBlur(img_Y, (3,3), 0)
        ret, thresh = cv.threshold(img_Y, 75, 255, cv.THRESH_BINARY)
        thresh_bgr = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)
        # thresh = cv.adaptiveThreshold(image_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 17, 2)
        signed_thresh = thresh[start_height].astype(np.int16)
        diff = np.diff(signed_thresh)
        points = np.where(np.logical_or(diff > 220, diff < -220))
        cv.line(image_bgr, (0, start_height), (w, start_height), (0, 255, 0), 3)

        if len(points) > 0 and len(points[0]) > 1:  # schwarze linie gefunden
            middle = (float(points[0][0]) + float(points[0][1])) / 2
            exzentierung = (middle - w/2)/(w/2) # in Prozent

            cv.circle(image_bgr, (points[0][0], start_height), 5, (255, 0, 0), -1)  # zeichnen rechte grenze
            cv.circle(image_bgr, (points[0][1], start_height), 5, (255, 0, 0), -1)
            cv.circle(image_bgr, (int(middle), start_height), 5, (0, 0, 255), -1)
            cv.line(image_bgr, (int(middle), h/2), (int(middle), h), (0,0,255), 3)
            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(image_bgr, str(round(float(exzentierung*100),2))+"%",(int(middle), h-20), font, 0.5,(0,0,255),2,cv.LINE_AA)

            print "Exzentierung: ", exzentierung*100, "%", "\n", "middle: ", middle, "\n", "w/2: ", w/2

            # Move(exzentierung)
            x_Speed = 0.06
            y_Speed = 0.0

            if firsttime:
                pid.output_limits = (-2., 2.)
                firsttime = False
            
            u = pid(exzentierung)
            rot = (math.pi * 20./180.) * u
            print "Rot: ", 180*(rot/np.pi)
            print "u: ", u

            #ALMove
            motion_service.move(x_Speed, y_Speed, rot)
        else:
            start_height -= 5
            start_height = start_height % h
            no_points_count += 1
            if no_points_count > 20:
                # StopAll
                motion_service.stopMove()
                time.sleep(5)
                motion_service.rest()
                print "Kein Bahn."
                raise RuntimeError
        # Zeigen
        cv.imshow("Linie_Folgen", np.hstack((cv.resize(image_bgr,(640, 480)),cv.resize(thresh_bgr,(640,480)))))
        k = cv.waitKey(1)
        if k == ord("q"):
            cv.destroyAllWindows()

            # StopAll
            motion_service.stopMove()
            time.sleep(5)
            motion_service.rest()
            break
        end = time.time()
        print "Zeit: ", end - start

except RuntimeError:
    # StopAll
    motion_service.stopMove()
    time.sleep(5)
    motion_service.rest()
    app.stop()
    sys.exit()
