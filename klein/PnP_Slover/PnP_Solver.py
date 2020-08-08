import numpy as np
import cv2 as cv
import glob

with np.load("./datei/cali_oben.npz") as file:
    mtx, dist, _, _ = [file[i] for i in ("mtx", "dist", "rvecs", "tvecs")]


def draw(img, corners, imgpts):
    corner = tuple(corners2[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


objp = np.array([[0, 0, 0], [16.43, 0, 0], [0, 19.69, 0], [16.43, 19.69, 0]], np.float32)
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)

img = cv.imread("./datei/gray.png")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
corners2 = np.array([[415, 344], [695, 333], [426, 664], [684, 678]],np.float32)

ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
img = draw(img, corners2, imgpts)
cv.imshow("img", img)
k = cv.waitKey(0)
if k == ord("s"):
    cv.imwrite("ver_2.png", img)
cv.destroyAllWindows()
