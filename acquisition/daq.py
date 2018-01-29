import numpy as np
from nidaq import nidaq

class daq():

    def __init__(self, daqType='nidaq', daqName = 'Dev1', channels=np.array([0]), sampFreq=1e5, numSamples=1000):
        self.daqType = daqType
        self.daqName = daqName
        self.daqChannels = channels
        self.sampFreq = sampFreq
        self.numSamples = numSamples

        self._DAQTask = 0

        if daqType.upper() == 'NIDAQ':
            self._DAQTask = nidaq(self.daqName,self.daqChannels,self.numSamples,self.sampFreq)


    def daqStart(self):
        self._DAQTask.StartTask()

    def daqStop(self):
        self._DAQTask.StopTask()

    def getData(self):
        p =  self._DAQTask.get_data_matrix()
        return p
