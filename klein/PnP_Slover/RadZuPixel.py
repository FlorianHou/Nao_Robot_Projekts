import math
import numpy as np
import cv2 as cv


def r2p(alpha, beta):
    """wanden Alpha und Beta zu Pixel umwanden"""
    dfov = 67.4  #Grad
    dfov_rad = dfov / 180 * math.pi
    # h und w von Bild
    h, w = img.shape[:2]
    # Pixels in
    d = math.sqrt(h**2 + w**2)
    # Pixels pro Rad
    einheit = d / dfov_rad
    # In Kamera Koordinaten
    alpha_pixel = alpha * einheit
    beta_pixel = beta * einheit
    # In Opencv Koordinaten System
    w_pixel = w / 2 - alpha_pixel
    h_pixel = h / 2 + beta_pixel
    return int(w_pixel), int(h_pixel)


if __name__ == "__main__":
    img = cv.imread("001.png")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    with np.load("landmark.npz", allow_pickle=True) as file:
        datei = file["datei"]
    positions_list = []
    mark_infos = datei[1]
    for mark_info in mark_infos:
        alpha = mark_info[0][1]
        beta = mark_info[0][2]
        position = r2p(alpha, beta)
        print(position)
        positions_list.append(position)
        cv.circle(gray, position, 20, 255, -1)
    cv.imwrite("gray.png", gray)