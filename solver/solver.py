from objective import objectiveCoilSquareCalc3D
from coilmodel import

class solver():
    def __init__(self, jac='2-point', bounds=([-0.5, -0.5, 0, 0, 0], [0.5, 0.5, 0.5, pi, 2*pi]), method='trf', ftol=1e-16, xtol=1e-8, gtol=1e-12, verbose=1):
        self.jac = jac
        self.bounds = bounds
        self.method = method
        self.ftol = ftol
        self.xtol = xtol
        self.gtol = gtol
        self.verbosity = verbose

    def solvePosition(self,):
