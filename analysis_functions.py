import time
import math
import numpy as np

def calc_d(x, y):
    """ Calculates the first derivatives of the input arrays """

    dx, dy = [], []

    for i in range(0, len(x)-1):
        dx.append(x[i+1] - x[i])
        dy.append(y[i+1] - y[i])
    
    dx.append(dx[-1])
    dy.append(dy[-1])
    return dx, dy

def calc_yaw_curvature(x, y):
    """ Calculates the yaw and curvature given an input path """

    dx, dy = calc_d(x,y)
    ddx, ddy = calc_d(dx, dy)
    yaw = []
    k = []

    for i in range(0, len(x)):
        yaw.append(math.atan2(dy[i], dx[i]))
        k.append( (ddy[i] * dx[i] - ddx[i] * dy[i]) / ((dx[i]**2 + dy[i]**2)**(3/2)) )

    return yaw, k