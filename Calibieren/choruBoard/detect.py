import cv2 as cv
import numpy as np
import time
import glob

def lade_Parameters():
    global mtx
    global dist
    with np.load("Calibieren/choruBoard/oben_charu_2560.npz") as f:
        mtx = f["mtx"]
        dist = f["dist"]
    return None
    
mtx = np.array([])
dist = np.array([])
lade_Parameters()

aruco = cv.aruco
dictionary = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
charou_board = aruco.CharucoBoard_create(7,9,0.04,0.02,dictionary)
detectorParams = aruco.DetectorParameters_create()
paths = glob.glob("Calibieren/choruBoard/datei/*.png")
for path in paths:
    #detktieren nur Markes
    img = cv.imread(path)
    markcorners, markids, _ = aruco.detectMarkers(img, dictionary)
    if markids is None or markids.size < 4:
        continue
    else:
        #detektiern Ecke
        ret, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(markcorners, markids, img, charou_board, cameraMatrix=mtx, distCoeffs=dist)
        ret, rvec, tvec = aruco.estimatePoseCharucoBoard(charucoCorners, charucoIds, charou_board, mtx, dist, None, None)
        img = aruco.drawAxis( img, mtx, dist, rvec, tvec, 0.04)
        imageCopy = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds, (255,0,0))
        cv.imshow("", imageCopy)
        cv.waitKey(0)
cv.destroyAllWindows()
