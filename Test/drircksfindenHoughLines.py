import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from math import pi

def nothing(_):
    pass

img_raw = cv.imread("Calibieren/datei/foto_1/20200832_A.png")
blur_1 = cv.GaussianBlur(img_raw,(5,5),0)
blur_2 = cv.medianBlur(img_raw,9)
b, g, r  = cv.split(blur_2)
cv.namedWindow('image')
cv.createTrackbar("Blur","image", 1, 300, nothing)
cv.createTrackbar("Threshold","image", 1, 300, nothing)
cv.createTrackbar("min","image",1, 300, nothing)
cv.createTrackbar("max","image",1, 300, nothing)
cv.createTrackbar("threshold_1","image",1, 300, nothing)
cv.createTrackbar("threshold_2","image",1, 300, nothing)
cv.createTrackbar("solbe","image",1, 300, nothing)
img_hsv_raw = cv.cvtColor(blur_2, cv.COLOR_BGR2HSV)
h,w,_ = img_raw.shape
bit = np.ones((h,w,3))
img = np.ones((h,w,3))
cv.setTrackbarPos("Threshold", "image", 80)


# Greun

# while True:
#     cv.imshow("image", np.hstack((cv.resize(img, (640,480)), cv.resize(bit, (640,480)))))
#     k = cv.waitKey(1)
#     if k == ord("q"):
#         break

#     img = blur_2.copy()
#     img_hsv = img_hsv_raw.copy()
#     blur = cv.getTrackbarPos("Blur", "image")
#     threshold = cv.getTrackbarPos("Threshold", "image")
#     min = cv.getTrackbarPos("min", "image")
#     max = cv.getTrackbarPos("max", "image")
#     threshold_1 = cv.getTrackbarPos("threshold_1", "image")
#     threshold_2 = cv.getTrackbarPos("threshold_2", "image")
#     solbe = cv.getTrackbarPos("solbe", "image")

#     bit_b = cv.inRange(img_hsv, (90,100,80), (115,255,255))
#     bit_g = cv.inRange(img_hsv, (50, 100, 50), (80,255,255))
#     kernel = np.ones((15,15))
#     bit_b = cv.morphologyEx(bit_b, cv.MORPH_CLOSE, kernel)
#     kernel = np.ones((10,10))
#     bit_b = cv.dilate(bit_b, kernel)
#     bit = cv.bitwise_or(bit_b, bit_g)
#     # Open Close
#     kernel = np.ones((5,5))
#     bit = cv.morphologyEx(bit, cv.MORPH_OPEN, kernel)
#     bit = cv.GaussianBlur(bit, (3,3), 0)
#     bit = cv.Canny(bit, threshold_1, threshold_2, solbe)
#     lines = cv.HoughLinesP(bit, 1, pi/180, threshold, minLineLength=min,maxLineGap=max)
#     for line in lines:
#         x1,y1,x2,y2 = line[0]
#         cv.line(img, (x1,y1),(x2,y2), (255,0,0), 10)
#     bit = cv.cvtColor(bit, cv.COLOR_GRAY2BGR)
#     cv.putText(img, str(len(lines)),(100,100), 0, 4,(255,0,0),thickness = 3)
# cv.destroyAllWindows()




while True:
    cv.imshow("image", np.hstack((cv.resize(img, (640,480)), cv.resize(bit, (640,480)))))
    k = cv.waitKey(1)
    if k == ord("q"):
        break

    img = blur_2.copy()
    img_hsv = img_hsv_raw.copy()
    blur = cv.getTrackbarPos("Blur", "image")
    threshold = cv.getTrackbarPos("Threshold", "image")

    min = cv.getTrackbarPos("min", "image")
    max = cv.getTrackbarPos("max", "image")
    threshold_1 = cv.getTrackbarPos("threshold_1", "image")
    threshold_2 = cv.getTrackbarPos("threshold_2", "image")
    solbe = cv.getTrackbarPos("solbe", "image")

    bit_b = cv.inRange(img_hsv, (100,100,40), (120,255,255))
    bit_g = cv.inRange(img_hsv, (60, 100, 40), (80,255,255))
    kernel = np.ones((15,15))
    bit_b = cv.morphologyEx(bit_b, cv.MORPH_CLOSE, kernel)
    kernel = np.ones((10,10))
    bit_b = cv.dilate(bit_b, kernel)
    bit = cv.bitwise_or(bit_b, bit_g)
    # Open Close
    kernel = np.ones((5,5))
    bit = cv.morphologyEx(bit, cv.MORPH_OPEN, kernel)
    bit = cv.GaussianBlur(bit, (3,3), 0)
    bit = cv.Canny(bit, threshold_1, threshold_2, solbe)
    lines = cv.HoughLines(bit, 1, pi/180, threshold)
    for line in lines:
        rho,theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv.line(img,(x1,y1),(x2,y2),(0,0,255),2)
    bit = cv.cvtColor(bit, cv.COLOR_GRAY2BGR)
    # print lines
    lines_sort = np.argsort(lines, axis=0)[...,0]
    lines = lines[lines_sort[:,0]]
    diff = np.diff(lines[:,0,0])
    result = np.where(np.abs(np.diff(lines[:,0,0]))>100)[0]+1
    print lines

    gruppe_0 = lines[0:result[0]]
    gruppe_1 = lines[result[0]:result[1]]
    gruppe_2 = lines[result[1]:]
    rand_list = []
    for i in (gruppe_0,gruppe_1,gruppe_2):
        rand_list.append(np.sum(i, axis=0)/i.shape[0])

    rand_list.append(rand_list[0])
    aussen = []
    for i in range(0,3):
        print "+"*40
        rho_1, theta_1 = rand_list[i][0]
        rho_2, theta_2 = rand_list[i+1][0]
        a = np.array([[-1/np.tan(theta_1), 1/np.tan(theta_2)],[1, -1]])
        b = np.array([[-(rho_1*np.sin(theta_1)-rho_2*np.sin(theta_2))],[-(rho_1*np.cos(theta_1)-rho_2*np.cos(theta_2))]])
        print a
        print b
        res = np.linalg.solve(a,b)
        x1, x2 = res
        print x1, x2
        x = rho_1*np.cos(theta_1) + x1
        y = rho_1*np.sin(theta_1) - 1/np.tan(theta_1)*x1
        print "x: ", x
        print "y: ", y
        cv.circle(img, (int(x),int(y)), 10, (255,0,0),-1)
        aussen.append(np.array([x[0],y[0]]))
    print aussen
    # break
cv.destroyAllWindows()

# # # # while True:
# # # #     cv.imshow("image", np.hstack((cv.resize(img, (640,480)), cv.resize(bit, (640,480)))))
# # # #     k = cv.waitKey(1)
# # # #     if k == ord("q"):
# # # #         break

# # # #     img = blur_2.copy()
# # # #     img_hsv = img_hsv_raw.copy()
# # # #     blur = cv.getTrackbarPos("Blur", "image")
# # # #     threshold = cv.getTrackbarPos("Threshold", "image")

# # # #     min = cv.getTrackbarPos("min", "image")
# # # #     max = cv.getTrackbarPos("max", "image")
# # # #     threshold_1 = cv.getTrackbarPos("threshold_1", "image")
# # # #     threshold_2 = cv.getTrackbarPos("threshold_2", "image")
# # # #     solbe = cv.getTrackbarPos("solbe", "image")

# # # #     bit_b = cv.inRange(img_hsv, (90,100,80), (115,255,255))
# # # #     bit_g = cv.inRange(img_hsv, (50, 100, 50), (80,255,255))
# # # #     kernel = np.ones((9,9))
# # # #     bit = cv.morphologyEx(bit_b, cv.MORPH_CLOSE, kernel)
# # # #     # Open Close
# # # #     kernel = np.ones((5,5))
# # # #     bit = cv.GaussianBlur(bit, (3,3), 0)
# # # #     bit = cv.Canny(bit, threshold_1, threshold_2, solbe)
# # # #     lines = cv.HoughLines(bit, 1, pi/180, threshold)
# # # #     for line in lines:
# # # #         rho,theta = line[0]
# # # #         a = np.cos(theta)
# # # #         b = np.sin(theta)
# # # #         x0 = a*rho
# # # #         y0 = b*rho
# # # #         x1 = int(x0 + 1000*(-b))
# # # #         y1 = int(y0 + 1000*(a))
# # # #         x2 = int(x0 - 1000*(-b))
# # # #         y2 = int(y0 - 1000*(a))
# # # #         cv.line(img,(x1,y1),(x2,y2),(0,0,255),2)
# # # #     bit = cv.cvtColor(bit, cv.COLOR_GRAY2BGR)
# # # #     # print lines
# # # #     result = np.where(np.abs(np.diff(lines[:,0,0]))>10)[0]+1
# # # #     print lines

# # # #     gruppe_0 = lines[0:result[0]]
# # # #     gruppe_1 = lines[result[0]:result[1]]
# # # #     gruppe_2 = lines[result[1]:]
# # # #     rand_list = []
# # # #     for i in (gruppe_0,gruppe_1,gruppe_2):
# # # #         rand_list.append(np.sum(i, axis=0)/i.shape[0])

# # # #     rand_list.append(rand_list[0])
# # # #     innen = []
# # # #     for i in range(0,3):
# # # #         print "+"*40
# # # #         rho_1, theta_1 = rand_list[i][0]
# # # #         rho_2, theta_2 = rand_list[i+1][0]
# # # #         a = np.array([[-1/np.tan(theta_1), 1/np.tan(theta_2)],[1, -1]])
# # # #         b = np.array([[-(rho_1*np.sin(theta_1)-rho_2*np.sin(theta_2))],[-(rho_1*np.cos(theta_1)-rho_2*np.cos(theta_2))]])
# # # #         print a
# # # #         print b
# # # #         res = np.linalg.solve(a,b)
# # # #         x1, x2 = res
# # # #         print x1, x2
# # # #         x = rho_1*np.cos(theta_1) + x1
# # # #         y = rho_1*np.sin(theta_1) - 1/np.tan(theta_1)*x1
# # # #         print "x: ", x
# # # #         print "y: ", y
# # # #         cv.circle(img, (int(x),int(y)), 20, (255,0,0),-1)
# # # #         innen.append(np.array([x[0],y[0]]))
# # # #     print innen
# # # #     # break
# # # # cv.destroyAllWindows()

