import numpy as np
from acquisition.nidaq import nidaq

class Daq():

    def __init__(self, config):
        self.daqType = config['system']['device_type']
        self.daqName = config['system']['device_name']
        self.daqChannels = config['system']['channels']
        self.pinMap = config['pinmap'][config['system']['system_version']]

        self.contSamps = True

        # Stores the daq device specific pinout corresponding to the selected channels
        self.daqPins = []
        # Coil current sense channel iis defined as channel 0, and is always the first in the list.
        self.daqPins.append(self.pinMap[0])
        for channel in self.daqChannels:
            self.daqPins.append(self.pinMap[channel])

        self.sampFreq = config['filter']['sampling_freq']
        self.numSamples = config['filter']['num_samples']

        self._DAQTask = 0

        if self.daqType.upper() == 'NIDAQ':
            self._DAQTask = nidaq(self.daqName, np.array(self.daqPins), self.numSamples, self.sampFreq, self.contSamps)

    def setContSamps(self, flag):
        if flag is True or flag is False:
            self.contSamps = flag


    def resetDaq(self):
        if self.daqType.upper() == 'NIDAQ':
            self._DAQTask.resetDevice()
            self._DAQTask = nidaq(self.daqName, np.array(self.daqPins), self.numSamples, self.sampFreq, self.contSamps)

    def daqStart(self):

        # Only need to start the task if sampling is continuous
        if self.contSamps is True:
            if self.daqType.upper() == 'NIDAQ':
                self._DAQTask.StartTask()

    def daqStop(self):
        if self.daqType.upper() == 'NIDAQ':
            self._DAQTask.StopTask()

    def getData(self):
        p = self._DAQTask.get_data_matrix()
        return p
