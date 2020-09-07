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
# 3 ist k4VGA(1280*960),2 ist VGA(640), 1 ist 320*240, 0 ist 176*..
Res = 4
#BGR-13(nicht RGB)
ColorSpace = 13
# FPS
fps = 30

try:
    app = qi.Application(url="tcp://10.0.158.231:9559")
except RuntimeError:
    print"error!!"
    sys.exit(1)

app.start()
session = app.session
# Services
video_cam = session.service("ALVideoDevice")
# Subscribe Kamera
# Komischerweise kann ein gleicher Name des Subscriber(hier ist "Kamera_Get") nicht mehr als 6 mals angewendet werden, wenn es ein Fehler auftrete,
# Versuchen Sie zuerst diesen Name zu anderen.
nameId = video_cam.subscribeCamera("Kamera_Get100", CamId, Res, ColorSpace, fps)
video_cam.setParameter(0,40,0)
video_cam.setParameter(0,43,80)
video_cam.setParameter(0,11,0)
video_cam.setParameter(0,17,500)
video_cam.setParameter(0,24,5)

#File name 961.....
count = 20200828
while True:
    # Get Image
    time.sleep(3)
    # http://doc.aldebaran.com/2-8/naoqi/vision/alvideodevice-api.html#ALVideoDeviceProxy::setParameter__iCR.iCR.iCR
    # http://doc.aldebaran.com/2-8/family/nao_technical/video_naov6.html#supported-parameters
    # video_cam.setParameter(0, 40, 1)
    image_raw = video_cam.getImageRemote(nameId)
    print "save"
    np.savez("BGR.npz", datei=image_raw)
    image_array_binary = image_raw[6]
    w = image_raw[0]
    h = image_raw[1]

    image_array_string = str(bytearray(image_array_binary))
    image_array = np.fromstring(image_array_string, np.uint8)
    image_array = image_array.reshape(h, w, -1)
    image_array_bgr = image_array #BGR
    # #Show Bild
    cv.imshow("img", cv.resize(image_array_bgr,(640,480)))
    k = cv.waitKey(0)
    # k = cv.waitKey(5) # Kontinuierliche Frame
    # # cv.destroyAllWindows()
    # druck "s" zu speichen, "q" zu schliessen, anderer Taster zu naeschste Bild wechseln
    if k == ord("s"):
        count += 1
        name = str(count).zfill(3) + "_A.png"
        cv.imwrite("./Calibieren/datei/foto_1/" + name, image_array_bgr)
    if k == ord("q"):
        video_cam.unsubscribe(nameId)
        cv.destroyAllWindows()
        break
    else:
        pass
# unsubscribe
