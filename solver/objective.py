import numpy as np
from model.constants import u0


def objectiveSolve(currentPandO, fluxSense, calibration, model):
    x = currentPandO[0]
    y = currentPandO[1]
    z = currentPandO[2]
    theta = currentPandO[3]
    phi = currentPandO[4]

    [Hx, Hy, Hz] = model.getField(np.array([x, y, z]))

    Bx = u0 * Hx
    By = u0 * Hy
    Bz = u0 * Hz

    Bxsensor = Bx * np.sin(theta)*np.cos(phi)
    Bysensor = By * np.sin(theta)*np.sin(phi)
    Bzsensor = Bz * np.cos(theta)

    fluxModel = Bxsensor + Bysensor + Bzsensor

    fluxModel = np.multiply(fluxModel, np.transpose(np.matrix(calibration)))

    out = fluxModel - fluxSense
    out = np.array(out)
    out = np.ndarray.flatten(out)

    return out

def objectiveCalibrate(parameters, calfield, coilindex, model, calpoints):

    zoffset = parameters[0]
    bscale = parameters[1]

    numpoints = len(calpoints[0])

    x = calpoints[0]
    y = calpoints[1]
    z = calpoints[2] - zoffset

    Hx = np.zeros([numpoints, ])
    Hy = np.zeros([numpoints, ])
    Hz = np.zeros([numpoints, ])

    for i in range(numpoints):
        Hx[i], Hy[i], Hz[i] = model.getFieldSingle([x[i], y[i], z[i]], coilindex)


    Bz = u0 * Hz * bscale

    deltaB = calfield - np.transpose(Bz)

    return deltaB.flatten()