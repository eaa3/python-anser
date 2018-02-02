import numpy as np
from objective import objectiveCoilSquareCalc3D as obj
from scipy.optimize import least_squares

def getposition(signedFlux, solverSettings, coilSettings, initialConditions, sensorList='all'):

    f = signedFlux

    s = sensorList

    ic = initialConditions

    ub = solverSettings.upperbounds
    lb = solverSettings.lowerbounds

    jac = solverSettings.jac
    mthd = solverSettings.method
    ftol = solverSettings.functionTolerance
    xtol = solverSettings.xTolerance
    gtol = solverSettings.globalTolerance
    verb = solverSettings.solverVerbosity

    x = coilSettings.xcoil
    y = coilSettings.ycoil
    z = coilSettings.zcoil

    least_squares(obj, ic[], args=(x, y, z, f), jac=jac, bounds=(lb, ub), method=mthd, ftol=ftol, xtol=xtol, gtol=gtol, verbose=verb)