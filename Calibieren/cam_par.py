import numpy as np
import cv2 as cv
import glob
import os

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((7 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

objpoints = []
imgpoints = []
gray = np.array([])
# path = 'C:/Users/zhaoy/python/opencv/Kalibieren/datei'
# images = glob.glob(os.path.join(path, "foto_1/*.png"))
images = glob.glob("./Calibieren/datei/foto_1_960/*.png")
print(images)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, (9, 7), None)

    if ret is True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        cv.drawChessboardCorners(img, (9, 7), corners2, ret)
        cv.imshow("img", img)
        cv.waitKey(1000)

cv.destroyAllWindows()
print("Shape:", gray.shape)
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints,
                                                  gray.shape[::-1], None, None)

#Speichen
zusammen = {"mtx": mtx, "dist": dist, "rvecs": rvecs, "tvecs": tvecs}
with open("./Calibieren/datei/zusammen_oben_960_2.npz", "wb") as file:
    np.savez(file, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
print(zusammen)
