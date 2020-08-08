import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import qi
# import tempfile
import random
import time
import sys

# 0 ist obere Kamera
CamId = 0
# 3 ist k4VGA,2 ist VGA
Res = 3
#BGR-13, YUV422-9
ColorSpace = 13
# FPS
fps = 5
# tempFile
# frame_path = tempfile.mkstemp()[1]
try:
    app = qi.Application(url="tcp://10.0.158.231:9559")
except RuntimeError:
    print"error!!"
    sys.exit(1)

app.start()
session = app.session
# Services
motion = session.service("ALMotion")
pose = session.service("ALRobotPosture")
video_cam = session.service("ALVideoDevice")
# Subscribe Kamera
nameId = video_cam.subscribeCamera("Kamera_Get", CamId, Res, ColorSpace, fps)
video_cam.setParameter(0,40,0)
count = 60
while True:
    # Get Image
    time.sleep(3)
    video_cam.setParameter(0,43,30)
    image_raw = video_cam.getImageRemote(nameId)
    image_array_binary = image_raw[6]
    w = image_raw[0]
    h = image_raw[1]
    image_array_string = str(bytearray(image_array_binary))
    image_array = np.fromstring(image_array_string, np.uint8)
    image_array = image_array.reshape(h, w, 3)
    # print len(image_array)
    image_array_bgr = image_array
    # #show Image
    cv.imshow("img", image_array_bgr)
    k = cv.waitKey(0)
    cv.destroyAllWindows()
    # cv.imwrite("lol.png",image_array_bgr)
    # Save, Destory, Next, Destory
    if k == ord("s"):
        count += 1
        name = str(count).zfill(3) + ".png"
        cv.imwrite("./klein/Dreiecks/datei/"+ name, image_array_bgr)
    elif k == ord("n"):
        pass
    else:
        video_cam.unsubscribe(nameId)
        break
# unsubscribe
