import cv2 as cv
import numpy as np

while True:
    # https://docs.opencv.org/4.4.0/d9/d6a/group__aruco.html#gac84398a9ed9dd01306592dd616c2c975
    dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_ARUCO_ORIGINAL)
    charou = cv.aruco.CharucoBoard_create(5,6,0.04,0.02,dictionary)
    img = charou.draw((480,640), 10,10)
    # cv.imwrite("Calibieren/choruBoard/datei", img)
    cv.imshow("",cv.resize(img,(480,640)))
    k = cv.waitKey(0)
    cv.destroyAllWindows()
    if k == ord("q"):
        break
    else:
        continue