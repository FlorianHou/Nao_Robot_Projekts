import cv2 as cv
import numpy as np

img = cv.imread("klein\PnP_Slover\datei\gray.png",0)
img_flat = img.flatten()
img_by = img_flat.tobytes()

load_array_dir = np.frombuffer(img_by,dtype=np.uint8)
pass