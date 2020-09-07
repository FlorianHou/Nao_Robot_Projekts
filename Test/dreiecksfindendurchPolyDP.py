import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

img = cv.imread("klein/Dreiecks/PnP_Solver/datei/961.png")
blur_1 = cv.GaussianBlur(img,(5,5),0)
blur_2 = cv.medianBlur(img,5)
b, g, r  = cv.split(blur_1)


# BGR To HSV
img_hsv = cv.cvtColor(blur_1, cv.COLOR_BGR2HSV)
# Greun
bit = cv.inRange(img_hsv, (50,100,60), (80,255,255))
kernel = np.ones((3,3))
# Open Close
bit = cv.morphologyEx(bit, cv.MORPH_CLOSE, kernel)
# bit = cv.morphologyEx(bit, cv.MORPH_OPEN, kernel)
# kernel = np.ones((3,3))
# bit_dil = cv.dilate(bit, kernel, iterations = 2)
# bit = cv.Canny(bit_dil,100,200)
kontours, _ = cv.findContours(bit, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
kontours_neu = []
for contour in kontours:
    flaeche = cv.contourArea(contour)
    if flaeche > 500:
        kontours_neu.append(contour)
print cv.contourArea(kontours_neu[0])
approxCurve = cv.approxPolyDP(kontours_neu[1], 8, True)
bit_bgr = cv.cvtColor(bit, cv.COLOR_GRAY2BGR)
# img = cv.drawContours(img, [approxCurve], 0, (255,0,0), 5)
img = cv.drawContours(img, [approxCurve], 0, (255,0,0), 1)



plt.subplot(121), plt.imshow(img), plt.title("contours")
plt.subplot(122), plt.imshow(bit,"gray")


plt.show()