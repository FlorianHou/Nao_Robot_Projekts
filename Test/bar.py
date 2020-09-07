import cv2 as cv
import numpy as np
from math import pi
def nothing(x):
    pass

img = cv.imread("klein/Dreiecks/datei/961.png")
# img_blur = cv.GaussianBlur(img, (5,5),-1)
img_blur = cv.bilateralFilter(img,11,15,15)

hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
in_g = cv.inRange(hsv, (60,100,70),(90,255,255))
in_b = cv.inRange(hsv, (90,100,100),(110,255,255))
kernel = np.ones((3,3))
in_g_1 = cv.morphologyEx(in_g, cv.MORPH_OPEN, kernel)
# kernel = np.ones((9,9))
# in_b_1 = cv.morphologyEx(in_b, cv.MORPH_OPEN, kernel)
# kernel = np.ones((11,11))
# in_b_1 = cv.dilate(in_b_1,kernel,iterations = 1)
# # in_g_1 = cv.bitwise_or(in_g_1, in_b_1)
kernel = np.ones((9,9))
# in_g_1 = cv.morphologyEx(in_g_1, cv.MORPH_CLOSE, kernel)
in_g_1_BGR = cv.cvtColor(in_g_1, cv.COLOR_GRAY2BGR)
lines = cv.Canny(in_g_1, 500,600)
lines_cp = lines.copy()
lines_cp = cv.cvtColor(lines, cv.COLOR_GRAY2BGR)
contours, hierarchy  = cv.findContours(in_g_1, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

for k in contours:
    approxCurve  = cv.approxPolyDP(k, 2.5, True)
    _ = cv.drawContours(img, [approxCurve], -1, (255,0,0))
cv.imshow("", np.hstack((img,in_g_1_BGR)))
cv.waitKey(0)
cv.destroyAllWindows()


# cv.namedWindow('image')
# cv.createTrackbar("Threshold","image",0,500,nothing)
# cv.createTrackbar("Min","image",0,500,nothing)
# cv.createTrackbar("Max","image",0,500,nothing)

# img_1 = img.copy()
# while True:
#     cv.imwrite("in_g.png",img_1)
#     cv.imshow("image", np.hstack((cv.resize(img_1,(640,480)),cv.resize(lines_cp,(640,480)))))
#     k = cv.waitKey(1)
#     if k == 27:
#         break
#     h = cv.getTrackbarPos("Threshold", "image")
#     min = cv.getTrackbarPos("Min", "image")
#     max = cv.getTrackbarPos("Max", "image")
#     img_1 = img_blur.copy()
#     a = cv.HoughLinesP(lines, 1, pi/180, h, minLineLength=min,maxLineGap=max)
#     _ = cv.putText(img_1, str(len(a)),(100,100), 0, 4,(255,0,0),thickness = 3)
#     for i in a:
#         x1,y1,x2,y2 = i[0]
#         _ = cv.line(img_1, (x1,y1), (x2,y2), (0,255,0),5)
#         _ = cv.circle(img_1, (x1,y1),7,(255,0,0),-1)
#         _ = cv.circle(img_1, (x2,y2),7,(255,0,0),-1)
 
# cv.destroyAllWindows()
