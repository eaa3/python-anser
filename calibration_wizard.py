from anser import Anser
from calibration.calibration import Calibration
import scipy.io as sio
from utils.settings import get_settings
import numpy as np














if __name__ == '__main__':
    config = get_settings()
    config['system']['device_name'] = 'Dev3'
    anser = Anser(config)



    dict = sio.loadmat('BStore1.mat')
    mat = np.array(dict['BStore'])

    cal = Calibration('7x7', anser.model, mat)

    result = cal.calibrateZ()

    d=0
