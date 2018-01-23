from coilmodel import spiralCoilFieldCalcMatrix
import numpy as np
from constants import u0

def objectiveCoilSquareCalc3D(currentPandO, xcoil, ycoil, zcoil, fluxReal):
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

    out = fluxModel - fluxReal
    out = np.array(out)
    out = np.ndarray.flatten(out)
    return out
