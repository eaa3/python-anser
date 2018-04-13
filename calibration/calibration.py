from model.constants import u0, pi
import numpy as np
from scipy.optimize import least_squares
from solver.objective import objectiveScalingOffsetZ
from utils.settings import get_calibration

class Calibration():

    def __init__(self, caltype, model, calfield):

        self.model = model
        self.calfield = calfield
        self.caltype = caltype
        self.calarray = get_calibration()

        if self.caltype.upper() == 'DUPLO':
            # These values can be edited depending on the setup
            blockno = 5
            calsensorposition = 0.5

            calTowerBlocks = blockno + calsensorposition
            BlockHeight = 19.2


            calTowerBlocks = blockno + calsensorposition

            x = np.array(np.linspace(-3, 3, 7) * 31.75e-3)

            self.x = np.array(np.concatenate((x, x, x, x, x, x, x)))
            self.y = [np.ones((1, 7))*95.25*1e-3, np.ones((1, 7))*63.5 * 1e-3,
                 np.ones((1, 7))*31.75*1e-3, np.ones((1, 7))*0,
                 np.ones((1, 7))*-31.75*1e-3, np.ones((1, 7))*-63.5 * 1e-3,
                 np.ones((1, 7))*-95.25*1e-3]

            boardDepth = 15
            self.z = (1e-3 * (boardDepth + calTowerBlocks * BlockHeight)) * np.ones(1, 49)

        elif self.caltype.upper() == '9X9':

            # Calibration points for Anser v1 using the 9x9 calibration grid
            spacing = (100 / 3) * 1e-3
            probeheight = 80e-3

            x = np.array(np.linspace(-4, 4, 9)) * spacing

            self.x = np.array(np.concatenate((x, x, x, x, x, x, x, x, x)))
            self.y = np.array(np.concatenate((np.ones((1, 9))*spacing*4, np.ones((1, 9))*spacing*3,  np.ones((1, 9))*spacing*2, np.ones((1, 9))*spacing*1,
                 np.ones((1, 9))*0, -np.ones((1, 9))*spacing*1, -np.ones((1, 9))*spacing*2, -np.ones((1, 9))*spacing*3,
                 -np.ones(1, 9)*spacing*4)))

            boardDepth = 4e-3
            self.z = ((boardDepth + probeheight)) * np.ones(1, 81)

        elif caltype.upper() == '7X7':

            # Calibration points for Anser v1 using the 9x9 calibration grid
            spacing = 42.86 * 1e-3
            probeheight = 72.2e-3

            x = np.array(np.linspace(-3, 3, 7)) * spacing

            self.x = np.array(np.concatenate((x, x, x, x, x, x, x)))
            self.y = np.array(np.concatenate((np.ones((7,))*spacing*3, np.ones((7,))*spacing*2,  np.ones((7,))*spacing*1, np.ones((7,))*spacing*0,
                 -np.ones((7,))*spacing*1, -np.ones((7,))*spacing*2, -np.ones((7,))*spacing*3)))

            boardDepth = 0# 4e-3
            self.z = ((boardDepth + probeheight)) * np.ones((49,))



    def calibrateZ(self):

        # The calibration of the system is based on scaling the magnetic field from each individual transmitter coil,
        # thus the number of calibration values to solve is equal to the number of transmitter coils.
        numcoils = self.model.numcoils

        # The orientation of the sensor during acquisition of the testpoint data. The sensor pointing towards the
        # transmitter board signifies an elevation angle of Pi radians.
        sensorOrientation = pi

        # A flat list of the points used in the calibration procedure.
        calpoints = [self.x, self.y, self.z]

        # The initial estimate for the calibration. Two variables are varied in this process
        # First entry is the sensor height offset (i.e z-axis). This needs to be part of the fitting procedure since
        # the precise height of the sensor varies depending on the manufacture of the calibration probe. The offset
        # value modifies the z-height of each testpoint during the fitting procedure
        # Second entry is the scaling factor for the actual magnetic field. This initially begins at '1' and converges
        # to a final value
        estimate = np.array([0, 1])

        # Storage for the calibration values
        cals = []

        # Iterate over each coil and calculate the scaling factors of each.
        for i in range(numcoils):

            result = least_squares(objectiveScalingOffsetZ, estimate, args=(self.calfield[i, :], i, self.model, calpoints),
                                   jac='3-point', method='trf', ftol=2.3e-14,
                                   xtol=1e-6, gtol=2.3e-16, verbose=0)

            cals.append(result.x)

        # Sensor is point towards the board (Theta = pi) during calibration. This sign change takes this into account.
        cals = np.array(cals) * np.sign(np.cos(sensorOrientation))

        print(cals)


if __name__ == '__main__':

    import scipy.io as sio

    # Test field data for proving the correctness of the calibration routine.
    dict = sio.loadmat('BStore1.mat')
    mat = dict['BStore']
    print(mat)
