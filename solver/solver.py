import numpy as np
from scipy.optimize import least_squares
from solver.objective import objectiveCoilSquareCalc3D

class Solver():
    def __init__(self, calibration, model, solver_config):

        # Solver settings
        self.jac = solver_config['jacobian']
        self.bounds = (solver_config['bounds_min'], solver_config['bounds_max'])
        self.method = solver_config['method']
        self.ftol = solver_config['ftol']
        self.xtol = solver_config['xtol']
        self.gtol = solver_config['gtol']
        self.verbosity = solver_config['verbosity']
        self.conditions = np.array(solver_config['initial_cond'])

        self.modelObject = model

        # Matrix of calibration values
        self.calibration = calibration

        # Initial conditions for the calibration routine
        self.calinit = [0, 1]

        # Variables to hold results of the solver
        self.result = np.zeros(self.conditions.shape[0])
        self.resCost = 0
        self.residuals = 0
        self.optimality = 0
        self.success = 0

    def solveLeastSquares(self, flux):

        if self.method.upper() == 'TRF':
            result = least_squares(objectiveCoilSquareCalc3D, self.conditions,
                                   args=(flux, self.calibration, self.modelObject),
                                         jac=self.jac, bounds=self.bounds, method=self.method,
                                         ftol=self.ftol, xtol=self.xtol,
                                         gtol=self.gtol, verbose=self.verbosity)
            return result
        elif self.method.upper() == 'LM':
            result = least_squares(objectiveCoilSquareCalc3D, self.conditions,
                                   args=(flux, self.calibration, self.modelObject),
                                   jac=self.jac, method=self.method,
                                   ftol=self.ftol, xtol=self.xtol,
                                   gtol=self.gtol, verbose=self.verbosity)
            return result
        else:
            exit('Unrecognised solving algorithm type; Levenburg-Marquardt (LM) and trust-region (TRF) are supported')
            result = 0
        return result
