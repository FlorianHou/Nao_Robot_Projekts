import numpy as np
import cv2 as cv
import glob
import time


with np.load("klein/Dreiecks/PnP_Solver/datei/zusammen_oben_960.npz") as file:
    mtx, dist, _, _ = [file[i] for i in ("mtx", "dist", "rvecs", "tvecs")]


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)

    return img


def ecks_dreieck():
    with np.load("klein/Dreiecks/PnP_Solver/datei/6Punkten.npz",
                 allow_pickle=True) as file:
        sp_dict = file["dict"].tolist()
    ecks = [sp_dict[i][0].tolist() for i in ["a", "e", "f", "d", "b", "c"]]
    return np.array(ecks, np.float32)


objp = np.array([[0, 0, 0], [-2.9, 4.7, 0], [2.9, 4.7, 0], 
                    [0, 10.3, 0], [-7.5, 11.2, 0], [7.5, 11.2, 0]], np.float32)
corners = ecks_dreieck()  # Aus Bild
axis = np.float32([[15, 0, 0], [0, 15, 0], [0, 0, -15]]).reshape(-1, 3)
img = cv.imread("klein/Dreiecks/PnP_Solver/datei/962.png")
b,g,r = cv.split(img)
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
corner_2 = cv.cornerSubPix(g, corners,(5,5),(-1,-1),criteria)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, rvecs, tvecs = cv.solvePnP(objp, corners, mtx, dist, flags=cv.SOLVEPNP_IPPE)
print rvecs, "\n##########\n", tvecs

imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
img = draw(img, corners, imgpts)
cv.imshow("img", img)
k = cv.waitKey(0)
if k == ord("s"):
    cv.imwrite("axis", img)
cv.destroyAllWindows()