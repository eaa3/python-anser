import numpy as np
from scipy.optimize import least_squares
from model.constants import u0, pi
from model.model import MagneticModel
from solver.objective import objectiveCoilSquareCalc3D

class Solver():
    def __init__(self, calibration, model, solver_config):

        # Solver settings
        self.jac = solver_config['jacobian']
        self.bounds = solver_config['bounds_min']
        self.method = solver_config['bound_max']
        self.ftol = solver_config['ftol']
        self.xtol = solver_config['xtol']
        self.gtol = solver_config['gtol']
        self.verbosity = solver_config['verbosity']
        self.conditions = solver_config['initial_cond']

        self.modelObject = model

        # Matrix of calibration values
        self.calibration = calibration

        # Variables to hold results of the solver
        self.result = np.zeros([1, self.conditions.size[1]])
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

