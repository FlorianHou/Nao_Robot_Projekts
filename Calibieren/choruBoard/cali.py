import cv2 as cv
import numpy as np
import time
import glob

aruco = cv.aruco
dictionary = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
charou_board = aruco.CharucoBoard_create(7,9,0.04,0.02,dictionary)
detectorParams = aruco.DetectorParameters_create()
allchrucoCorners = []
allchrucoIds = []

img_files = glob.glob("/home/florian/Robot_Lokal/Calibieren/choruBoard/datei/*.png")

for path in img_files:

    #detktieren nur Markes
    img = cv.imread(path,0)
    # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    markcorners, markids, _ = aruco.detectMarkers(img, dictionary)

    if markids is None or markids.size <= 4:
        continue

    else:
        #detektiern Ecke
        ret, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(markcorners, markids, img, charou_board)

        imageCopy = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds, (255,0,0))
        cv.imshow("", cv.resize(imageCopy,(640,480)))
        print path
        cv.waitKey(5)
        cv.destroyAllWindows()
        allchrucoCorners.append(charucoCorners)
        allchrucoIds.append(charucoIds)

print len(allchrucoCorners)
shape = img.shape[:2]
ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraCharuco(allchrucoCorners, allchrucoIds,
                                        charou_board,img.shape[::-1], None, None)

print mtx
print dist

with open("Calibieren/choruBoard/oben_charu_2560.npz", "w") as f:
    np.savez(f, mtx=mtx,dist=dist)