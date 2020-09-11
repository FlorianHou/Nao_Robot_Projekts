import qi
import numpy as np
import cv2 as cv
import time
import csv
import uuid
import sys

session = qi.Session()
session.connect("tcp://10.0.147.226:9559")
# 0 ist obere Kamera
CamId = 0
# # 3 ist k4VGA,2 ist VGA
Res = 4
#BGR-13, YUV422-9
ColorSpace = 0
# FPS
fps = 60


video_cam = session.service("ALVideoDevice")
# Subscribe Kamera
subName = str(uuid.uuid4)
nameId = video_cam.subscribeCamera(subName, CamId, Res, ColorSpace, fps)
video_cam.setParameter(0,40,0)
video_cam.setParameter(0,43,80)
video_cam.setParameter(0,11,0)
video_cam.setParameter(0,17,700)
video_cam.setParameter(0,24,2)
print nameId

count = 2000
while True:
    contain = video_cam.getImageRemote(nameId)
    img_buffer = np.frombuffer(contain[6], np.uint8)
    img_Yuv = img_buffer.reshape(contain[1],contain[0],-1)
    cv.imshow("", img_Yuv)
    k = cv.waitKey(1)
    if k == ord("s"):
        count += 1
        name = str(count).zfill(3) + "_A.png"
        cv.imwrite("./Calibieren/datei/foto_1/" + name, img_Yuv)
    if k == ord("q"):
        cv.destroyAllWindows()
        sys.exit(1)
        break
    else:
        pass
    
video_cam.unsubscribe(nameId)













