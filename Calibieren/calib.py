import numpy as np
import cv2 as cv
import glob
import os

path = 'C:/Users/zhaoy/python/opencv/Kalibieren/datei'
with np.load(os.path.join(path, "zusammen_oben.npy"), allow_pickle=True) as file:
    mtx = file["mtx"]
    dist = file["dist"]


def draw(img, coeners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0, 0.001)
objp = np.zeros((7 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape[-1, 2]
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, 3]]).reshape(-1, 3)

path = 'C:/Users/zhaoy/python/opencv/Kalibieren/datei'
fname = glob.glob(os.path.join(path, "foto_1/*.png"))
for fname in fname:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (9, 7), None)
    if ret == True:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        ret, rvecs, tvecs = cv.solvePnp(objp, corners2, mtx, dist)

        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        img = draw(img, corners, imgpts)
        cv.imshow("img", img)
        k = cv.waitKey(0)
        if k == ord("s"):
            cv.imwrite(fname[:6] + ".png", img)
cv.detroyAllWindows()
