from model.constants import u0, pi
import numpy as np

class Calibration():

    def __init__(self, caltype):

        if caltype.toUpper == 'DUPLO':
            # These values can be edited depending on the setup
            blockno = 5
            calsensorposition = 0.5

            calTowerBlocks = blockno + calsensorposition
            BlockHeight = 19.2;


            calTowerBlocks = blockno + calsensorposition

            x = np.array(np.linspace(-3, 3, 7) * 31.75e-3)

            x = np.array(np.concatenate(x, x, x, x, x, x ,x))
            y = [np.ones(1, 7)*95.25*1e-3, np.ones(1, 7)*63.5 * 1e-3,
                 np.ones(1, 7)*31.75*1e-3, np.ones(1, 7)*0,
                 np.ones(1, 7)*-31.75*1e-3, np.ones(1, 7)*-63.5 * 1e-3,
                 np.ones(1, 7)*-95.25*1e-3]

            boardDepth = 15
            z = (1e-3 * (boardDepth + calTowerBlocks * BlockHeight)) * np.ones(1, 49)

        elif caltype.toUpper == '9x9':

            # Calibration points for Anser v1 using the 9x9 calibration grid
            spacing = (100 / 3) * 1e-3
            probeheight = 80e-3

            x = np.array(np.linspace(-4, 4, 9)) * spacing

            x = np.array(np.concatenate((x, x, x, x, x, x, x, x, x)))
            y = np.array(np.concatenate((np.ones(1, 9)*spacing*4, np.ones(1, 9)*spacing*3,  np.ones(1, 9)*spacing*2, np.ones(1, 9)*spacing*1,
                 np.ones(1, 9)*0, -np.ones(1, 9)*spacing*1, -np.ones(1, 9)*spacing*2, -np.ones(1, 9)*spacing*3,
                 -np.ones(1, 9)*spacing*4)))

            boardDepth = 4e-3
            z = ((boardDepth + probeheight)) * np.ones(1, 81)

        elif caltype.toUpper == '7x7':

            # Calibration points for Anser v1 using the 9x9 calibration grid
            spacing = 42.86 * 1e-3
            probeheight = 80e-3

            x = np.array(np.linspace(-3, 3, 7)) * spacing

            x = np.array(np.concatenate((x, x, x, x, x, x, x)))
            y = np.array(np.concatenate((np.ones(1, 7)*spacing*4, np.ones(1, 7)*spacing*2,  np.ones(1, 7)*spacing*1, np.ones(1, 7)*spacing*0,
                 np.ones(1, 7)*1, -np.ones(1, 7)*spacing*2, -np.ones(1, 7)*spacing*3)))

            boardDepth = 4e-3
            z = ((boardDepth + probeheight)) * np.ones(1, 81)