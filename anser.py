from utils.settings import get_settings, get_calibration
from model.model import MagneticModel
from solver.solver import Solver
from acquisition.daq import Daq
from filter.filter import Filter
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *
from model.constants import pi



class Anser():

    def __init__(self, config):

        self.cal_dict = get_calibration('calibration.yaml')
        self.cal = np.array(self.cal_dict[1])

        self.model = MagneticModel(config['model'])
        self.solver = Solver(self.cal, self.model, config['solver'])

        self.channels = config['system']['channels']
        self.flipflags = []

        self.daq = Daq(config)
        self.filter = Filter(config)

        self.data = np.matrix([])
        self.magnitudes = np.matrix([])

        # Create local OpenIGTLink server
        self.igtconn = None
        if config['system']['igt'] is True:
            self.igtconn = PyIGTLink(port=config['system']['igt_port'], localServer=config['system']['igt_local'])



    def _igt_send_transform(self, mat, device_name=''):

        matmsg = TransformMessage(mat, device_name=device_name)
        self.igtconn.add_message_to_send_queue(matmsg)


    def sample_update(self):
        self.data = self.daq.getData()

    def resolve_position(self, sensorNo):

        magnitudes = self.filter.demodulateSignalRef(self.data, self.channels.index(sensorNo) + 1)
        result = self.solver.solveLeastSquares(magnitudes)

        # Wrap around angles to preserve constraints
        wrapresult = self._angle_wrap(result)

        self.solver.initialCond = wrapresult.x

        return np.array(wrapresult.x)

    def get_position(self, sensorNo, igtname=''):

        self.solver.calibration = np.array(self.cal_dict[sensorNo])
        position = self.resolve_position(sensorNo)
        positionmat = self.vec_2_mat_5dof(position)

        if self.igtconn is True:
            igtposition = position
            if str(sensorNo) in self.flipflags:
                igtposition[4] = igtposition[4] + pi
            igtmat = self.vec_2_mat_5dof(igtposition)
            self._igt_send_transform(igtmat, igtname)

        return position, positionmat

    def start_acquisition(self):
        self.daq.daqStart()

    def stop_acquisition(self):
        self.daq.daqStop()

    @staticmethod
    def print_position(position):
        print('%0.4f %0.4f %0.4f %0.4f %0.4f'
              % (position[0] * 1000, position[1] * 1000, position[2] * 1000, position[3], position[4]))

    @staticmethod
    def _angle_wrap(result):
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] - 2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi
        return result

    @staticmethod
    def vec_2_mat_5dof(self, array=np.array(np.zeros([1,5]))):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat

    @staticmethod
    def vec_2_mat_6dof(self, array=np.array(np.zeros([1,6]))):

        pass



