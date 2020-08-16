import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt


def get_dreieck():
    img = cv.imread("klein/Dreiecks/datei/964.png")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_blur_gau = cv.GaussianBlur(img, (3,3), 0)
    img_hsv = cv.cvtColor(img_blur_gau, cv.COLOR_BGR2HSV)
    img_g = cv.inRange(img_hsv, (50,100,60), (70, 255,200))

    return img_blur_gau, img_g

if __name__ == "__main__":
    img, img_g = get_dreieck()
    contours, hierarchy  = cv.findContours(img_g, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(img, contours, 0, (255,0,0),3)


    plt.subplot(221)
    plt.imshow(cv.cvtColor(img,cv.COLOR_BGR2RGB))
    plt.subplot(222)
    plt.imshow(img_g, "gray")

    plt.show()


    
