from model.model import MagneticModel
from solver.solver import Solver
from acquisition.daq import Daq
from filter.filter import Filter
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *
from model.constants import pi



class Anser():

    def __init__(self, daqDeviceName, daqHardwareType, freqs, samples, samplefreq, serial, modeltype, sensors,
                 verbosity=0, igt=False):


        self.cal = np.array([0,0,0,0,0,0,0,0])

        self.model = MagneticModel(modeltype, 25, length=70e-3, width=0.5e-3, spacing=0.25e-3, thick=1.6e-3)
        self.solver = Solver(self.cal, self.model, verbose=verbosity,
                                 bounds=([-0.5, -0.5, 0, -pi, -3*pi], [0.5, 0.5, 0.5, pi, 3*pi]),
                                 initialCond=[0.0, 0.0, 0.10, 0.0, 0.0])

        self.daq = Daq(daqHardwareType, daqName=daqDeviceName, channels=sensors, numSamples=samples)
        self.filter = Filter(self.daq, freqs, sampleFreq=samplefreq)

        # Create local OpenIGTLink server
        if igt==True:
            self.igtconn = PyIGTLink(localServer=True)

    def vec2mat(self, array=np.array(np.zeros([1,5]))):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat

    def igtSendTransform(self, mat, device_name=''):

        matmsg = TransformMessage(mat, device_name=device_name)
        self.igtconn.add_message_to_send_queue(matmsg)

    def getResolveSensor(self, sensorNo):

        data = self.daq.getData()
        demod = self.filter.demodulateSignalRef(data, sensorNo)
        result = self.solver.solveLeastSquares(demod)

        # Wrap around angles to preserve constraints
        wrapresult = self.angleWrap(result)

        self.solver.initialCond = wrapresult.x

        return np.array(wrapresult.x)

    def getPosition(self, sensorNo):

        position = self.getResolveSensor(sensorNo)

        if self.flipFlag == True:
            position[3] = position[3] + pi

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
