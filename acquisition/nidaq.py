""" Class definition for national instruments data acquisition system"""

from PyDAQmx import *
from numpy import zeros
import numpy as np
from ctypes import byref
import threading
import platform


class NIDAQ(Task):
    """
    Class definition for national instruments data acquisition system
    """
    def __init__(self, dev_name='Dev1', channels=np.array([0]), data_len=1000, sampleFreq=100000.0, contSample=True):
        Task.__init__(self)
        if dev_name is None:
            dev_name = dev_name
        self.dev_name = dev_name
        self._data = zeros(data_len * channels.shape[0])
        self.channels = channels
        self.data_len = data_len
        self.read = int32()
        self.contSample = contSample
        for i in range(channels.shape[0]):
            self.CreateAIVoltageChan(dev_name+"/ai"+str(channels[i]),"", DAQmx_Val_RSE, -10.0,10.0, DAQmx_Val_Volts, None)

        if contSample is True:
            self.CfgSampClkTiming("", sampleFreq, DAQmx_Val_Rising, DAQmx_Val_ContSamps, data_len)
        else:
            self.CfgSampClkTiming("", sampleFreq, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, data_len)

        if platform.system() == 'Windows' and contSample is True:
            self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,data_len,0)
            self.AutoRegisterDoneEvent(0)
        elif (platform.system() == 'Linux' or platform.system() == 'Darwin'):
            pass

        self._data_lock = threading.Lock()
        self._newdata_event = threading.Event()

    def EveryNCallback(self):
        with self._data_lock:
            self.ReadAnalogF64(self.data_len, 10.0, DAQmx_Val_GroupByChannel, self._data, self.data_len*self.channels.shape[0], byref(self.read), None)
            self._newdata_event.set()
        return 0 # The function should return an integer

    def DoneCallback(self, status):
        try:
            print("Status",status.value)
            return 0 # The function should return an integer
        except Exception as e:
            print(str(e))
            return 0

    def get_data(self, blocking=True, timeout=None):
        if platform.system() == 'Windows' and self.contSample is True:
            if blocking:
                if not self._newdata_event.wait(timeout):
                    raise ValueError("timeout waiting for data from device")
            with self._data_lock:
                self._newdata_event.clear()
                return self._data.copy()
        elif platform.system() == 'Linux' or platform.system() == 'Darwin' or self.contSample is False:
            self.ReadAnalogF64(self.data_len, 10.0, DAQmx_Val_GroupByChannel, self._data, self.data_len*self.channels.shape[0], byref(self.read), None)
            return self._data.copy()

    def get_data_matrix(self, timeout=None):
        data = self.get_data(timeout=timeout)
        data_mat = np.matrix(np.reshape(data, (self.channels.shape[0], self.data_len)).transpose())
        return data_mat

    def resetDevice(self):
        DAQmxResetDevice(self.dev_name)

if __name__=="__main__":

    # Test script for NI acqusition unit
    import matplotlib.pyplot as plt

    channels = np.array([0])
    sampleFreq = 100000
    noSamples = 1000
    deviceID = 'Dev3'
    task = NIDAQ(dev_name=deviceID,channels=channels, sampleFreq=sampleFreq, data_len=noSamples)
    task.StartTask()

    print("Acquiring 10 * 1000 samples in continuous mode.")
    for _ in range(10):
        p = task.get_data_matrix(timeout=10.0)
        print("Acquired %d points" % task.read.value)

    task.StopTask()
    task.ClearTask()

    mag = abs(np.fft.fft(p[0:1000]))

    p = np.array(p)
    pmat=np.array(np.reshape(p, (channels.shape[0],noSamples)).transpose())
    b=0
    plt.plot(mag)
    plt.show()
    b = 0
