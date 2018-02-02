import numpy as np
from constants import u0, pi
from model import model as modelClass
from scipy.optimize import least_squares
from objective import objectiveCoilSquareCalc3D

class solver():
    def __init__(self, calibration, model=modelClass, initialCond=np.array([0.0, 0.0, 0.14, 0.0, 0.0]), jac='2-point',
                 bounds=([-0.5, -0.5, 0, 0, 0], [0.5, 0.5, 0.5, pi, 2*pi]),
                 method='trf', ftol=1e-16, xtol=1e-6, gtol=1e-16, verbose=1):

        self.jac = jac
        self.bounds = bounds
        self.method = method
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.verbosity = verbose

        self.modelObject = model
        self.initialCond = initialCond

        self.calibration = calibration

        self.result = np.array([])
        self.resCost = 0
        self.residuals = 0
        self.optimality = 0
        self.success = 0

    def solveLeastSquares(self, flux):

        result = least_squares(objectiveCoilSquareCalc3D, self.initialCond,
                               args=(self.modelObject.xPointsTrans,self.modelObject.yPointsTrans,self.modelObject.zPointsTrans,flux,self.calibration),
                              jac=self.jac, bounds=self.bounds, method=self.method, ftol=self.ftol, xtol=self.xtol,
                              gtol=self.gtol, verbose=self.verbosity)

        return result

