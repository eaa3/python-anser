from coilmodel import spiralCoilFieldCalcMatrix
import numpy as np
from constants import u0

def objectiveCoilSquareCalc3D(currentPandO, xcoil, ycoil, zcoil, fluxReal, calibration):
    x = currentPandO[0]
    y = currentPandO[1]
    z = currentPandO[2]
    theta = currentPandO[3]
    phi = currentPandO[4]

    [Hx, Hy, Hz] = spiralCoilFieldCalcMatrix(1, xcoil, ycoil, zcoil, x, y, z)

    Bx = u0 * Hx
    By = u0 * Hy
    Bz = u0 * Hz

    Bxsensor = Bx * np.sin(theta)*np.cos(phi)
    Bysensor = By * np.sin(theta)*np.sin(phi)
    Bzsensor = Bz * np.cos(theta)

    fluxModel = Bxsensor + Bysensor + Bzsensor

    fluxModel = np.multiply(fluxModel, np.transpose(np.matrix(calibration)))

    out = fluxModel - fluxReal
    out = np.array(out)
    out = np.ndarray.flatten(out)

    return out



def objectiveCoilSquareCalc3D_2(currentPandO, xcoil, ycoil, zcoil, fluxReal, calibration):
    x = currentPandO[0]
    y = currentPandO[1]
    z = currentPandO[2]
    a = currentPandO[3]
    b = currentPandO[4]
    c = currentPandO[5]
    s = 1

    [Hx, Hy, Hz] = spiralCoilFieldCalcMatrix(1, xcoil, ycoil, zcoil, x, y, z)

    Bx = u0 * Hx
    By = u0 * Hy
    Bz = u0 * Hz

    Bxsensor = Bx * a
    Bysensor = By * b
    Bzsensor = Bz * c
    scalc = np.sqrt(a**2 + b**2 + c**2)
    fluxModel = Bxsensor + Bysensor + Bzsensor

    fluxModel = np.multiply(fluxModel, np.transpose(np.matrix(calibration)))

    out = fluxModel - fluxReal
    vecmag = s - scalc
    out = np.array(out)
    out = np.ndarray.flatten(out)
    out = np.append(out, vecmag)
    return out

