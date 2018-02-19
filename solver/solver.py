import numpy as np
from model.constants import u0, pi
from model import model as modelClass
from scipy.optimize import least_squares
from solver.objective import objectiveCoilSquareCalc3D, objectiveCoilSquareCalc3D_2

class solver():
    def __init__(self, calibration, solverType, model=modelClass, initialCond=np.array([0.0, 0.0, 0.10, 0.0, 0.0]), jac='2-point',
                 bounds=([-0.3, -0.3, 0.0, 0, 0], [0.3, 0.3, 0.3, pi, 2*pi]),
                 method='trf', ftol=2.3e-16, xtol=1e-6, gtol=2.3e-16, verbose=1):

        self.jac = jac
        self.bounds = bounds
        self.method = method
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.verbosity = verbose

        self.solverType = solverType
        self.modelObject = model
        self.initialCond = initialCond

        self.calibration = calibration

        self.result = np.array([])
        self.resCost = 0
        self.residuals = 0
        self.optimality = 0
        self.success = 0

    def solveLeastSquares(self, flux):

        # result =np.ones([1,5])
        if self.solverType == 1:
            result = least_squares(objectiveCoilSquareCalc3D, self.initialCond,
                                   args=(flux,self.calibration, self.modelObject),
                                         jac=self.jac, bounds=self.bounds, method=self.method,
                                         ftol=self.ftol, xtol=self.xtol,
                                         gtol=self.gtol, verbose=self.verbosity)
            return result
        elif self.solverType == 2:
            result = least_squares(objectiveCoilSquareCalc3D_2, self.initialCond,
                                   args=(flux, self.calibration, self.modelObject),
                                         jac=self.jac, bounds=self.bounds, method=self.method,
                                         ftol=self.ftol, xtol=self.xtol,
                                         gtol=self.gtol, verbose=self.verbosity)

            return result

