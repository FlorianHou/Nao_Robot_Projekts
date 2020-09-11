import qi
import numpy as np
import cv2 as cv
import time
import csv


session = qi.Session()
session.connect("tcp://10.42.0.95:9559")
# 0 ist obere Kamera
CamId = 0
# # 3 ist k4VGA,2 ist VGA    plt.imshow(contours,"gray")
# Res = 4
#BGR-13, YUV422-9
ColorSpace = 13
# FPS
fps = 60
#ColorSpace List
ResList = [0, 1, 2, 3, 4]

"""neheme Datei aus Nao, dann uebersetzen YUV zu BGR"""
video_cam = session.service("ALVideoDevice")

# Speichen in csv File
header = ["Res", "Round", "Delta_t", "Zeit Per Frame"]
with open("SpeedTest_image/BGR2BGR.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(header)

for res in ResList:
    print "Res: ", res

    # Subscribe Kamera
    nameId = video_cam.subscribeCamera("Kamera_Get98", CamId, res, ColorSpace, fps)
    video_cam.setParameter(0,40,0)
    video_cam.setParameter(0,43,80)
    video_cam.setParameter(0,11,0)
    video_cam.setParameter(0,17,700)
    video_cam.setParameter(0,24,2)
    print nameId

    zeitList = []
    for round in range(3):

        for f in range(50):
            if f == 20:
                t1 = time.time()
            contain = video_cam.getImageRemote(nameId)
            img_buffer = np.frombuffer(contain[6], np.uint8)
            img_BGR = img_buffer.reshape(contain[1],contain[0],-1)
            # cv.imshow("", img_BGR)
            # cv.waitKey(1)
            
        t2 = time.time()
        
        delta_t = t2-t1
        print "round: ", round, "delta_t: ", delta_t, "Zeit Per Frame: ", delta_t/30.
        with open("SpeedTest_image/BGR2BGR.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([res, round, delta_t, delta_t/30.])
        zeitList.append(delta_t)        
    print "durchschnittliche Zeit per frame:(10 round) ", sum(zeitList)/(float(len(zeitList))*30.)
    with open("SpeedTest_image/BGR2BGR.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(["", "", "durchschnittliche Zeit per frame", sum(zeitList)/(float(len(zeitList))*30.)])
    # cv.destroyAllWindows()
    video_cam.unsubscribe(nameId)













