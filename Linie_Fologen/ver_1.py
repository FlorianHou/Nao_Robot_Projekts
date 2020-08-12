import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import sys

img = cv.imread("./Linie_Fologen/Datei/Sim/Sim_bild/1_kl.png")
img = cv.GaussianBlur(img, (7, 7), 0)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                             cv.THRESH_BINARY, 11, 2)
h, w, _ = img.shape
start_height = h - 15
signed_thresh = thresh[start_height].astype(np.int16)
diff = np.diff(signed_thresh)
points = np.where(np.logical_or(diff > 200, diff < -200))
cv.line(img, (0, start_height), (160, start_height), (0, 255, 0),
        thickness=5)
middle = int((points[0][0] + points[0][-1]) / 2)

cv.circle(img, (points[0][0], start_height), 5, (255, 0, 0), -1)
cv.circle(img, (points[0][-1], start_height), 5, (255, 0, 0), -1)
cv.circle(img, (middle, start_height), 5, (0, 0, 255), -1)
print(points[0][1], start_height)
print(int((middle - 160 / 2)))

plt.imshow(img)
plt.show()