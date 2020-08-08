import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img = cv.imread("./klein/Dreiecks/datei/001.png")
b, g, r = cv.split(img)
blur_b = cv.GaussianBlur(b, (25, 25), 0)
ret, thresh_1 = cv.threshold(b, 100, 255, cv.THRESH_BINARY_INV)
th3 = cv.adaptiveThreshold(blur_b, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv.THRESH_BINARY_INV, 11, 2)

kernel = np.zeros((10, 10), np.uint8)
dst = cv.morphologyEx(thresh_1, cv.MORPH_OPEN, kernel)

edges = cv.Canny(dst, 10, 10)

contours, hierarchy = cv.findContours(thresh_1, cv.RETR_TREE,
                                      cv.CHAIN_APPROX_SIMPLE)

img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
# define range of blue color in HSV
lower_blue = np.array([0, 50, 50])
upper_blue = np.array([10, 255, 255])
# Threshold the HSV image to get only blue colors
mask = cv.inRange(img_hsv, lower_blue, upper_blue)
mask_dst = cv.dst = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
edges = cv.Canny(mask, 10, 10)

img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

# # lines = cv.HoughLines(edges, 1, np.pi / 180, 100)
# # for line in lines:
# #     rho, theta = line[0]
# #     a = np.cos(theta)
# #     b = np.sin(theta)
# #     x0 = a*rho
# #     y0 = b*rho
# #     x1 = int(x0 + 6000*(-b))
# #     y1 = int(y0 + 6000*(a))
# #     x2 = int(x0 - 6000*(-b))
# #     y2 = int(y0 - 6000*(a))

# #     cv.line(edges,(x1,y1), (x2,y2),255,2)
lines = cv.HoughLinesP(edges,
                       1,
                       np.pi / 180,
                       125,
                       minLineLength=1000,
                       maxLineGap=1000)
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv.line(edges, (x1, y1), (x2, y2), 255, 5)
    print(line)

plt.subplot(121), plt.imshow(edges, "gray")
plt.subplot(122), plt.imshow(mask, "gray")
plt.show()