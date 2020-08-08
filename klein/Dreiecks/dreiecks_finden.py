import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import math

img = cv.imread("/media/florian/ESXI-7_0_0-/opencv/Robot/klein/Dreiecks/datei/004.png")
img = cv.GaussianBlur(img, (5,5),0)
b, g, r = cv.split(img)
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
mask = cv.inRange(hsv, (50,100,40),(70,255,255))

kernel = np.ones((5,5),np.uint8)
morph = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
canny_1 = cv.Canny(morph, 100,200)

lines = cv.HoughLinesP(canny_1,1, math.pi / 180,100,minLineLength=50,maxLineGap=20)
for line in lines:
    x1,y1,x2,y2 = line[0]
    cv.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    print line[0]

plt.subplot(221), plt.imshow(mask, "gray")
plt.subplot(222), plt.imshow(morph, "gray")
plt.subplot(223), plt.imshow(canny_1,"gray")
plt.subplot(224), plt.imshow(cv.cvtColor(img,cv.COLOR_BGR2RGB))
plt.show()