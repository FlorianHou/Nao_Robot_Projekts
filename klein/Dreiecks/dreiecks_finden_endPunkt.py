import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

sp_dict= dict()   #SchnittPunkte Dict

def get_dreieck():
    img = cv.imread("klein/Dreiecks/datei/322.png")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # img_blur_gau = cv.GaussianBlur(img, (3,3), 0)
    img_blur_gau = cv.bilateralFilter(img,9,75,75)
    img_hsv = cv.cvtColor(img_blur_gau, cv.COLOR_BGR2HSV)
    img_g = cv.inRange(img_hsv, (50,100,60), (70, 255,200))

    return img_blur_gau, img_g

def EndPunkt(contours):
    aussen = contours[0]
    innen = contours[1]
    #aussen
    max_auss = np.argmax(aussen, axis=0)
    min_auss = np.argmin(aussen, axis=0)
    sp_dict["a"] = aussen[min_auss[0][1]]
    sp_dict["b"] = aussen[min_auss[0][0]]
    sp_dict["c"] = aussen[max_auss[0][0]]

    #innen
    max_inn = np.argmax(innen, axis=0)
    min_inn = np.argmin(innen, axis=0)    
    sp_dict["d"] = innen[max_inn[0][1]]
    sp_dict["e"] = innen[min_inn[0][0]]
    sp_dict["f"] = innen[max_inn[0][0]]

    # print(sp_dict)


if __name__ == "__main__":
    img, img_g = get_dreieck()
    contours, hierarchy  = cv.findContours(img_g, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    cv.drawContours(img, contours, 0, (255,0,0),2)
    print(contours)
    EndPunkt(contours)
    for punkt in sp_dict.values():
        cv.circle(img, tuple(punkt[0]), 1, (0,0,255), -1)

    plt.subplot(121)
    plt.imshow(cv.cvtColor(img,cv.COLOR_BGR2RGB))
    plt.subplot(122)
    plt.imshow(img_g, "gray")

    plt.show()


    
