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

        self.daq = Daq(config)
        self.filter = Filter(config)

        self.data = np.matrix([])
        self.magnitudes = np.matrix([])

        # Create local OpenIGTLink server
        self.igtconn = None
        if config['system']['igt'] is True:
            self.igtconn = PyIGTLink(port=config['system']['igt_port'], localServer=config['system']['igt_local'])

    def vec2mat5DOF(self, array=np.array(np.zeros([1,5]))):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat

    def vec2mat6DOF(self, array=np.array(np.zeros([1,6]))):

        pass

    def igtSendTransform(self, mat, device_name=''):

        matmsg = TransformMessage(mat, device_name=device_name)
        self.igtconn.add_message_to_send_queue(matmsg)


    def sampleUpdate(self):
        self.data = self.daq.getData()

    def resolvePosition(self, sensorNo):

        magnitudes = self.filter.demodulateSignalRef(self.data, sensorNo)
        result = self.solver.solveLeastSquares(magnitudes)

        # Wrap around angles to preserve constraints
        wrapresult = self.angleWrap(result)

        self.solver.initialCond = wrapresult.x

        return np.array(wrapresult.x)

    def getPosition(self, sensorNo):

        self.solver.calibration = np.array(self.cal_dict[sensorNo])
        position = self.resolvePosition(self.channels.index(sensorNo) + 1)

        return position

    def angleWrap(self, result):
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] - 2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi
        return result

    def start(self):
        self.daq.daqStart()

    def stop(self):
        self.daq.daqStop()

    def printPosition(self, position):
        print('%0.4f %0.4f %0.4f %0.4f %0.4f'
              % (position[0] * 1000, position[1] * 1000, position[2] * 1000, position[3], position[4]))

    def angleFlip(self, flag):
        self.flipFlag = flag
