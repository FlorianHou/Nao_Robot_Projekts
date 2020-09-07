import almath
import numpy as np
import cv2 as cv

a = np.array([[-0.18771717],
                [-0.04952767],
                [ 0.0052126 ]]  )
Trans = cv.Rodrigues(a)
Trans_rot = Trans[0]
b = np.hstack((Trans_rot, np.array([0,0,0]).reshape(-1,1)))
Transform = almath.Transform(b.flatten().tolist())
print Transform
print almath.position6DFromTransform(Transform)