import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import math

k_dict = {}

img = cv.imread("./klein/Dreiecks/datei/031.png")
##Blur
# img = cv.GaussianBlur(img, (5,5), 0)
img = cv.bilateralFilter(img, 9, 75, 75)
# Spilt in B,G,R
b, g, r = cv.split(img)
#Zu HSV
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
# masken durch inRange
mask = cv.inRange(hsv, (50, 150, 30), (80, 255, 255))
mask = cv.GaussianBlur(mask, (5, 5), 0)
#Kontour
kernel = np.ones((5, 5), np.uint8)
morph = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
canny_1 = cv.Canny(morph, 50, 200)
#Linien
lines = cv.HoughLinesP(canny_1,
                       1,
                       math.pi / 180,
                       80,
                       minLineLength=100,
                       maxLineGap=20)
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    print(line[0])
    k = (y2 - y1) / (x2 - x1)
    b = (y1 - ((x1 * y2) / x2)) * (x2 / (x2 - x1))
    print(str(int(k)))
    k_dict[int(k)] = [x1, y1, x2, y2, k, b]

#SchnittPunkt
x = int((k_dict[0][5] - k_dict[-1][5]) / (k_dict[-1][4] - k_dict[0][4]))
y = int(k_dict[0][4] * x + k_dict[0][5])
p1 = (x, y)
x = int((k_dict[1][5] - k_dict[-1][5]) / (k_dict[-1][4] - k_dict[1][4]))
y = int(k_dict[1][4] * x + k_dict[1][5])
p2 = (x, y)
x = int((k_dict[1][5] - k_dict[0][5]) / (k_dict[0][4] - k_dict[1][4]))
y = int(k_dict[1][4] * x + k_dict[1][5])
p3 = (x, y)
##Zeichnen auf dem Bild
# print(p1, p2, p3)
cv.circle(img, p1, 10, (255, 0, 0), -1)
cv.circle(img, p2, 10, (255, 0, 0), -1)
cv.circle(img, p3, 10, (255, 0, 0), -1)

# print(k_dict)
plt.subplot(221), plt.imshow(mask, "gray"),
plt.subplot(222), plt.imshow(morph, "gray")
plt.subplot(223), plt.imshow(canny_1, "gray")
plt.subplot(224), plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
plt.show()
