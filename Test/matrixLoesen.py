import numpy as np
import cv2 as cv

rho_1 = 910
theta_1 = 1.57
rho_2 = 1189
theta_2 = 0.5934

a = np.array([[-1/np.tan(theta_1), 1/np.tan(theta_2)],[1, -1]])
b = np.array([[-(rho_1*np.sin(theta_1)-rho_2*np.sin(theta_2))],[-(rho_1*np.cos(theta_1)-rho_2*np.cos(theta_2))]])
print a
print b

res = np.linalg.solve(a,b)
x1, x2 = res
print x1, x2
print rho_1*np.cos(theta_1) + x1
print rho_1*np.sin(theta_1) - 1/np.tan(theta_1)*x1