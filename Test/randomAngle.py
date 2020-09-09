import numpy as np
from math import pi
import time

angles = [angle*(pi/180) for angle in range(-90, 120, 30)]
angles_copy = angles[:]
for _ in angles:
    length = len(angles_copy)
    auswahl = np.random.randint(0,length)
    angle = angles_copy[auswahl]
    angles_copy.remove(angle)
    print angle
    print angles_copy
    time.sleep(2)