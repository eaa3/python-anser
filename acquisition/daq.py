import numpy as np
from acquisition.nidaq import NIDAQ


class DAQ:

    def __init__(self, config):

        # Extract the system parameters
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
            self._DAQTask = NIDAQ(self.daqName, np.array(self.daqPins), self.numSamples, self.sampFreq, self.contSamps)

    # A flag to set how the DAQ performs its sampling operations
    # The DAQ task must be reset using resetDaq() for changes to take effect
    def setContSamps(self, flag):
        if flag is True or flag is False:
            self.contSamps = flag

    # Reset the DAQ and reinitialise the task to take into account any parameter changes.
    def resetDaq(self):
        if self.daqType.upper() == 'NIDAQ':
            self._DAQTask.ClearTask()
            self._DAQTask = NIDAQ(self.daqName, np.array(self.daqPins), self.numSamples, self.sampFreq, self.contSamps)

    # Start the DAQ task. Only called when using continuous sampling
    def daqStart(self):

        # Only need to start the continuous task if sampling is continuous.
        # When using finite sampling, the getData() function will call the task starting function on each iteration
        if self.contSamps is True:
            if self.daqType.upper() == 'NIDAQ':
                self._DAQTask.StartTask()

    # Stop the current DAQ task
    def daqStop(self):
        if self.daqType.upper() == 'NIDAQ':
            self._DAQTask.StopTask()

    # Retrieve data from the DAQ
    def getData(self):

        # DAQ task must be called each time when using finite sampling
        if self.contSamps is False:
            self._DAQTask.StartTask()

        # Retrieve the data from the DAQ in matrix form, where each column corresponds to an analog channel
        return self._DAQTask.get_data_matrix()
