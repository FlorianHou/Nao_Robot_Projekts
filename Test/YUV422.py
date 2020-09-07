import qi
import uuid
import cv2 as cv
import numpy as np

session = qi.Session()
session.connect("tcp://192.168.1.101:2526")

video_cam = session.service("ALVideoDevice")

# 0 ist obere Kamera
CamId = 0
# 3 ist k4VGA,2 ist VGA
Res = 2
#BGR-13, YUV422-9
ColorSpace = 11
# FPS
fps = 30
# Parameter ruecksetzen
video_cam.setAllParametersToDefault(CamId)
# AutoFocus
video_cam.setParameter(0, 40, 1)
# AutoExposition
video_cam.setParameter(0, 11, 1)
# CameraSharpness
video_cam.setParameter(0, 24, 1)
# Kamera Oeffnet
video_cam.openCamera(CamId)
subCamName = str(uuid.uuid4())
subCamId = video_cam.subscribeCamera(subCamName, CamId, Res, ColorSpace, fps)
# Stand testen
if video_cam.isCameraOpen and subCamId != "":
    print "Kamera ist Laufend."
    print "subCamId: " + subCamId
    KamIsBreit = True
else:
    raise RuntimeError("Kamera kann nicht initiziert werden!")

img_raw = video_cam.getImageRemote(subCamId)[6]
result = video_cam.putImage(CamId, 320, 240, img_raw)
print result
