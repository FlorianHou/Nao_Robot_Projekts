import almath
import qi
import cv2 as cv
import numpy as np


def RobotZuZiel():
    """Mit der Loesung der Pnp, rechnen wir die 
    relative Position zwischen Robot und Ziel"""

    #getTrandform()
    # name – Name of the item. Could be: any joint or chain or sensor (Use ALMotionProxy::getSensorNames for the list of sensors supported on your robot).
    # frame – Task frame {FRAME_TORSO = 0, FRAME_WORLD = 1, FRAME_ROBOT = 2}.
    # useSensorValues – If true, the sensor values will be used to determine the position.
    transform = motion_service.getTransform(currentCamkera, 2, True)
    transformList = almath.vectorFloat(transform)
    RobotToCamera = almath.Transform(transformList)

    # Rotationsmatrix
    rvecs_mat = cv.Rodrigues(rvec)[0]
    rvecs_mat_1D = np.ravel(rvecs_mat)
    cameraZuZiel_RotationMatrix = almath.Rotation(rvecs_mat_1D)

    CamToPointTransformation = almath.Transform()
    #CamToPoint_Rotation
    CamToPointTransformation.r1_c1 = rvecs_mat_1D[0]
    CamToPointTransformation.r1_c2 = rvecs_mat_1D[1]
    CamToPointTransformation.r1_c3 = rvecs_mat_1D[2]
    CamToPointTransformation.r2_c1 = rvecs_mat_1D[3]
    CamToPointTransformation.r2_c2 = rvecs_mat_1D[4]
    CamToPointTransformation.r2_c3 = rvecs_mat_1D[5]
    CamToPointTransformation.r3_c1 = rvecs_mat_1D[6]
    CamToPointTransformation.r3_c2 = rvecs_mat_1D[7]
    CamToPointTransformation.r3_c3 = rvecs_mat_1D[8]

    #CamToPoint_Translation
    CamToPointTransformation.r1_c4 = tvecs[0, 0]
    CamToPointTransformation.r2_c4 = tvecs[1, 0]
    CamToPointTransformation.r3_c4 = tvecs[2, 0]

    #CameraToPoint Gesamt Transformation
    print CamToPointTransformation

    #Robot Zu Punkt
    RobToPunkt_Transform = RobotToCamera * CamToPointTransformation

    return RobToPunkt_Transform


if __name__ == "__main__":
    with np.load("/media/florian/ESXI-7_0_0-/opencv/Robot/klein/4_Landmark/Robot2Ziel.py") as file:
        rvecs = file["rvecs"]
        tvecs = file["tvecs"]
        RobToPunkt_Transform = RobotZuZiel()
        print RobToPunkt_Transform
