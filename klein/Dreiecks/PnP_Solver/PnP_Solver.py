import numpy as np
import cv2 as cv
import glob
import math
import almath

with np.load("klein/Dreiecks/PnP_Solver/datei/zusammen_oben_320.npz") as file:
    mtx, dist, _, _ = [file[i] for i in ("mtx", "dist", "rvecs", "tvecs")]


def draw(img, corners, imgpts):
    corner = tuple(corners2[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 3)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 3)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 3)
    return img


def ecks_dreieck():
    with np.load("klein/Dreiecks/PnP_Solver/datei/6Punkten.npz",
                 allow_pickle=True) as file:
        sp_dict = file["dict"].tolist()
    ecks = [sp_dict[i][0].tolist() for i in ["a","b","c","d","e","f"]]
    return np.array(ecks, np.float32)

def PnP_Solve():

    objp = np.array([[0, 0, 0], [-7.49, 11.2,0], [7.45, 11.2,0], [0, 10.3, 0],
                    [-2.8, 4.7,0], [2.8, 4.7,0]], np.float32) # Punkt in realem Welt
    corners2 = ecks_dreieck() # Aus Bild
    ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
    rvecs_tr=cv.Rodrigues(rvecs)[0] #RotationsVektor zu Rotationstransform
    return rvecs, rvecs_tr, tvecs, corners2

def Koordination_Opencv2RobotKamera():
    RotX_1 = almath.Transform.fromRotX(-math.pi/2)
    RotZ_1 = almath.Transform.fromRotY(-math.pi/2)
    RotY_2 = almath.Transform.fromRotY(-math.pi/2)
    RotX_2 = almath.Transform.fromRotX(math.pi/2)
    a = np.array(PnP_Ergebnis_dict["rvecs_tr"])
    b = np.array(PnP_Ergebnis_dict["tvecs"])
    Transform_Cam2Ziel_OP = np.hstack((a,b))
    return Transform_Cam2Ziel_OP = almath.Transform(Transform_Cam2Ziel_OP.flatten())

def Robot2Ziel(session):
    



axis = np.float32([[5, 0, 0], [0, 5, 0], [0, 0, 5]]).reshape(-1, 3)

img = cv.imread("klein/Dreiecks/PnP_Solver/datei/322.png")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

rvecs, rvecs_tr, tvecs, corners2 = PnP_Solve()
print (rvecs, "\n##########\n", tvecs)

imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
PnP_Ergebnis_dict = {
    "rvecs_tr"  : rvecs_tr,
    "tvecs"     : tvecs
                }

with open("klein\Dreiecks\PnP_Solver\datei\PnP_Ergebnis.npz", "wb") as file:
    np.savez(file, rvecs_tr=rvecs_tr, tvecs=tvecs)

img = draw(img, corners2, imgpts)
cv.imshow("img", img)
k = cv.waitKey(0)
if k == ord("s"):
    cv.imwrite("axis", img)
cv.destroyAllWindows()
