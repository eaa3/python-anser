import numpy as np
from model.model import model
from solver.solver import solver
from acquisition.daq import daq
from acquisition.filters import filter
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *
from constants import pi


class TrackingSystem():

    def __init__(self, daqDeviceName='Dev1', freqs=np.array([20000,22000,24000,26000,28000,30000,32000,34000]), samples=1000,
                      samplefreq=1e5, serial='', modeltype='square', solverType=1, verbosity=0, igt=False, sensors=np.array([])):


        self.cal = np.array([0.0890,   0.0930,    0.0945,    0.0939,    0.0946,    0.0936,    0.0922,    0.0888])

        self.model = model(modeltype, 25, length=70e-3, width=0.5e-3, spacing=0.25e-3, thick=1.6e-3)


        if solverType == 1:
            self.solver = solver(self.cal, solverType, self.model, verbose=verbosity,
                                 bounds=([-0.5, -0.5, 0, -pi, -3*pi], [0.5, 0.5, 0.5, pi, 3*pi]),
                                 initialCond=[0.0, 0.0, 0.10, 0.0, 0.0])
        elif solverType == 2:
            self.solver = solver(self.cal, solverType, self.model, verbose=verbosity,
                                 bounds=([-0.3, -0.3, 0, -1,-1,-1],[0.3, 0.3, 0.3, 1, 1, 1]),
                                 initialCond=[0.0, 0.0, 0.15, 0, 0, 1])



        self.daq = daq('nidaq', daqName=daqDeviceName, channels=sensors, numSamples=samples)
        self.filter = filter(self.daq, freqs, sampleFreq=samplefreq)

        # Create OpenIGTLink client connection
        if igt==True:
            self.igtconn = PyIGTLink(localServer=True)




    def vec2mat(self, array=np.array(np.zeros([1,5]))):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat


    def igtSend(self, mat):

        matmsg = TransformMessage(mat)
        self.igtconn.add_message_to_send_queue(matmsg)

    def getPosition(self, sensorNo):

        data = self.daq.getData()
        demod = self.filter.demodulateSignalRef(data, sensorNo)
        result = self.solver.solveLeastSquares(demod)

        # Wrap around angles to preserve contraints
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] -2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi

        self.solver.initialCond = result.x
        return np.array(result.x)

    def start(self):
        self.daq.daqStart()

    def stop(self):
        self.daq.daqStop()







if __name__ == '__main__':

    from time import sleep
    anser = TrackingSystem(daqDeviceName='Dev3', sensors=np.array([4,0]), igt=True, samples=250, solverType=1)
    anser.start()

    while True:
        po = anser.getPosition(1)
        print(po)
        po[3] = po[3] + pi
        po_mat = anser.vec2mat(po)
        anser.igtSend(po_mat)
        sleep(0.001)
