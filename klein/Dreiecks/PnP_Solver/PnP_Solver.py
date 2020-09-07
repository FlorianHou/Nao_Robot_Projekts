import qi
import numpy as np
import cv2 as cv
import glob
import math
import almath
import time

url = "tcp://192.168.1.101:12916"
session = qi.Session()
session.connect(url)
motion = session.service("ALMotion")
visionCompass = session.service("ALVisualCompass")

with np.load("klein/Dreiecks/PnP_Solver/datei/zusammen_oben_960.npz") as file:
    mtx, dist, _, _ = [file[i] for i in ("mtx", "dist", "rvecs", "tvecs")]


def draw(img, corners, imgpts):
    for corner in corners:
        cv.circle(img, tuple(corner), 5, (255,0,0), -1)
    corner = tuple(corners[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 3)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 3)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 3)
    return img


def ecks_dreieck():
    with np.load("klein/Dreiecks/PnP_Solver/datei/6Punkten.npz",
                 allow_pickle=True) as file:
        sp_dict = file["dict"].tolist()
    ecks = [sp_dict[i][0].tolist() for i in ["a", "e", "f", "d", "b", "c"]]
    return np.array(ecks, np.float32)


def PnP_Solve():
    # objp = np.array([[0, 0, 0], [-7.49, 11.2,0], [7.45, 11.2,0], [0, 10.3, 0],
    #                 [-2.8, 4.7,0], [2.8, 4.7,0]], np.float32) # Punkt in realem Welt
    # objp = np.array([[0,0,0], [-7.5, 11.2,0],[7.5,11.2,0],
    #                     [0,10.3,0], [-2.9, 4.7,0],[2.9, 4.7,0]], np.float32)
    objp = np.array([[0, 0, 0], [-1.85, 4.65, 0], [1.85, 4.65, 0], 
                        [0, 10.3, 0], [-7.5, 11.25, 0], [7.5, 11.25, 0]], np.float32)/100
    corners2 = ecks_dreieck()  # Aus Bild

    b,g,r = cv.split(img)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corner_2 = cv.cornerSubPix(g, corners2,(5,5),(-1,-1),criteria)
    
    ret, rvecs, tvecs = cv.solvePnP(objp, corner_2, mtx, dist,flags=cv.SOLVEPNP_IPPE)
    # ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
    rvecs_tr = cv.Rodrigues(rvecs)[0]  # RotationsVektor zu Rotationstransform
    return rvecs, rvecs_tr, tvecs, corner_2


def Cam2Ziel_OP():
    a = np.array(PnP_Ergebnis_dict["rvecs_tr"])
    b = np.array(PnP_Ergebnis_dict["tvecs"]) # Einheit von cm zu m
    Transform_Cam2Ziel_OP = np.hstack((a, b))
    Transform_Cam2Ziel_OP = almath.Transform(Transform_Cam2Ziel_OP.flatten())
    return Transform_Cam2Ziel_OP


def Robot2Ziel_ROB(robot2CamROB):
    """Robot zu Ziel"""
    RotZ_1 = almath.Transform.fromRotZ(-math.pi/2)
    RotX_1 = almath.Transform.fromRotX(-math.pi/2)
    RotY_2 = almath.Transform.fromRotY(-math.pi/2)
    RotX_2 = almath.Transform.fromRotX(math.pi/2)
    Tr_X = almath.Transform.fromPosition(0.0, 0., 0.)
    robot2CamOP = robot2CamROB * RotZ_1 * RotX_1 
    robot2ZielOP = robot2CamOP * Cam2Ziel_OP()
    robot2ZielROB = robot2ZielOP * RotY_2 * RotX_2 * Tr_X
    print robot2ZielROB
    return robot2ZielROB


def get_ROB2CAM():

    robot2CamROB = motion.getTransform("CameraTop", 2, True)
    robot2CamROB = almath.Transform(robot2CamROB)
    return robot2CamROB


axis = np.float32([[0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]).reshape(-1, 3)

img = cv.imread("klein/Dreiecks/PnP_Solver/datei/961.png")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

rvecs, rvecs_tr, tvecs, corners2 = PnP_Solve()
print rvecs, "\n","##########","\n", tvecs

imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
PnP_Ergebnis_dict = {
    "rvecs_tr": rvecs_tr,
    "tvecs": tvecs
}

with open("klein\Dreiecks\PnP_Solver\datei\PnP_Ergebnis.npz", "wb") as file:
    np.savez(file, rvecs_tr=rvecs_tr, tvecs=tvecs)
robot2CamROB = get_ROB2CAM()
robot2ZielROB = Robot2Ziel_ROB(robot2CamROB)
robot2ZielROB_Pose2D = almath.pose2DFromTransform(robot2ZielROB).toVector()
img = draw(img, corners2, imgpts)
cv.imshow("img", cv.resize(img,(640,480)))
k = cv.waitKey(0)
if k == ord("s"):
    cv.imwrite("axis", img)
cv.destroyAllWindows()
print robot2ZielROB_Pose2D
print 180*(robot2ZielROB_Pose2D[2]/math.pi)
print almath.position6DFromTransform(robot2ZielROB)
result = visionCompass.setResolution(1)
print result

# visionCompass.moveTo(robot2ZielROB_Pose2D[0],robot2ZielROB_Pose2D[1],robot2ZielROB_Pose2D[2])
motion.moveTo(robot2ZielROB_Pose2D[0],robot2ZielROB_Pose2D[1],robot2ZielROB_Pose2D[2])
# motion.moveTo(0,0,math.pi*(180/180))
time.sleep(1)
motion.setAngles(["HeadPitch"], [10*(math.pi/180)], 0.1)
motion.setAngles(["HeadYaw"], [0*(math.pi/180)], 0.1)