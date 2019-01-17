import numpy as np
from scipy.optimize import least_squares
from solver.objective import objectiveSolve
from model.constants import pi
import datetime
import os


class Solver:
    def __init__(self, lookup_table, model, solver_config):
        self.lookup_table = lookup_table
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
        self.calibration = None

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
            result = least_squares(objectiveSolve, self.conditions,
                                   args=(flux, self.calibration, self.modelObject),
                                         jac=self.jac, bounds=self.bounds, method=self.method,
                                         ftol=self.ftol, xtol=self.xtol,
                                         gtol=self.gtol, verbose=self.verbosity)
            return result
        elif self.method.upper() == 'LM':
            result = least_squares(objectiveSolve, self.conditions,
                                   args=(flux, self.calibration, self.modelObject),
                                   jac=self.jac, method=self.method,
                                   ftol=self.ftol, xtol=self.xtol,
                                   gtol=self.gtol, verbose=self.verbosity)
        elif self.method.upper() == 'DOGBOX':
            result = least_squares(objectiveSolve, self.conditions,
                                   args=(flux, self.calibration, self.modelObject),
                                   jac=self.jac, bounds=self.bounds, method=self.method,
                                   ftol=self.ftol, xtol=self.xtol,
                                   gtol=self.gtol, verbose=self.verbosity)
        else:
            exit('Unrecognised solving algorithm type; Levenburg-Marquardt (LM) and trust-region (TRF) are supported')
            result = 0
        return result

    def get_position(self, sensorName, magnitudes):
        self.calibration, self.conditions = self.lookup_table[sensorName]
        result = self.solveLeastSquares(magnitudes)
        wrapresult = self._angle_wrap(result)
        position = np.array(wrapresult.x)
        self.lookup_table[sensorName] = (self.calibration, position)
        positionmat = self.vec_2_mat_5dof(wrapresult.x)
        return sensorName, positionmat

    @staticmethod
    def vec_2_mat_5dof(array):

        mat = np.matrix([[np.cos(array[4]) * np.cos(array[3]), -np.sin(array[4]), np.cos(array[4]) * np.sin(array[3]),
                          array[0] * 1000],
                         [np.sin(array[4]) * np.cos(array[3]), np.cos(array[4]), np.sin(array[4]) * np.sin(array[3]),
                          array[1] * 1000],
                         [-np.sin(array[3]), 0, np.cos(array[3]), array[2] * 1000],
                         [0, 0, 0, 1]])
        return mat


    @staticmethod
    def _angle_wrap(result):
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] - 2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi
        return result