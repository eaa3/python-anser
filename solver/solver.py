import numpy as np
from scipy.optimize import least_squares
from model.constants import u0, pi
from model.model import MagneticModel
from solver.objective import objectiveCoilSquareCalc3D

class Solver():
    def __init__(self, calibration, model=MagneticModel, initialCond=np.array([0.0, 0.0, 0.10, 0.0, 0.0]), jac='2-point',
                 bounds=([-0.3, -0.3, 0.0, 0, 0], [0.3, 0.3, 0.3, pi, 2*pi]),
                 method='trf', ftol=2.3e-16, xtol=1e-6, gtol=2.3e-16, verbose=1):

        # Solver settings
        self.jac = jac
        self.bounds = bounds
        self.method = method
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.verbosity = verbose
        self.modelObject = model
        # Initial conditions for the solver
        self.conditions = initialCond
        # Matrix of calibration values
        self.calibration = calibration

        # Variables to hold results of the solver
        self.result = np.zeros([1, initialCond.size[1]])
        self.resCost = 0
        self.residuals = 0
        self.optimality = 0
        self.success = 0

    def solveLeastSquares(self, flux):


        result = least_squares(objectiveCoilSquareCalc3D, self.conditions,
                               args=(flux, self.calibration, self.modelObject),
                                     jac=self.jac, bounds=self.bounds, method=self.method,
                                     ftol=self.ftol, xtol=self.xtol,
                                     gtol=self.gtol, verbose=self.verbosity)
        return result

