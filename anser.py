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
                      samplefreq=1e5, serial='', modeltype='square', verbosity=0, igt=False, sensors=np.array([])):


        self.cal = np.array([0.0968, 0.0998, 0.1010, 0.1000, 0.0992, 0.0986, 0.0962, 0.0932])

        self.model = model(modeltype, 25, length=70e-3, width=0.5e-3, spacing=0.25e-3, thick=1.6e-3)
        self.solver = solver(self.cal, self.model, verbose=verbosity)
        self.daq = daq('nidaq', daqName=daqDeviceName, channels=sensors)
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
        self.solver.initialCond = result.x
        return np.array(result.x)

    def start(self):
        self.daq.daqStart()

    def stop(self):
        self.daq.daqStop()







if __name__ == '__main__':

    from time import sleep
    anser = TrackingSystem(daqDeviceName='Dev3', sensors=np.array([4,0]), igt=True, samples=250)
    anser.start()

    while True:
        po = anser.getPosition(1)
        po[3] = po[3] + pi
        po_mat = anser.vec2mat(po)
        anser.igtSend(po_mat)
        sleep(0.01)
