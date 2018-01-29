import numpy as np
from numpy.matlib import repmat
from scipy.signal import firwin, get_window, chebwin
from constants import pi

class filter():
    def __init__(self, numSamples=1000, transFreqs=np.array([20000,24000,24000,26000,28000,30000,32000,34000]), sampleFreq=1e5):
        self.numSamples = numSamples


        # Define parameters
        self.transFreqs = transFreqs
        self.numFreqs = self.transFreqs.shape[0]
        self.sampleFreq = sampleFreq
        self.filtArray = np.array([])
        self.filtMatrix = np.matrix(self.filtArray)
        self.demodArray = np.zeros([self.numFreqs, self.numSamples], dtype=complex)
        self.demodMatrix = np.matrix(self.demodArray)


        # Generate filter
        self.cutoff = 5e-5
        self.window = ('chebwin', 200)
        self.width = None
        self.passDC = True
        self.scale = True
        self.filterGen(cutoff=5e-5, window=('chebwin', 200), width=None, passDC=True, scale=True)

        # TODO Create an intelligent way of calculating the DAQ phase offsets
        # self.daqPhaseOffset = 0

        # Generate demodulation matrix
        self.samplePeriod = 1/self.sampleFreq
        self.timeArray = np.linspace(0, (self.numSamples - 1) * self.samplePeriod, self.numSamples)
        for i in range(self.numFreqs):
            self.demodMatrix[i, :] = [np.exp(2*pi*self.transFreqs[i]*self.timeArray * 1j)]



    def filterGen(self, cutoff=5e-5, window=('chebwin', 200), width=None, passDC=True, scale=True):
        self.filtArray = firwin(self.numSamples, cutoff, width=width, window=window, pass_zero=passDC, scale=scale)
        self.filtMatrix = np.matrix(repmat(self.filtArray, 2, 1))

    def demodulateSignalRef(self, data, channel):
        filtWindow = self.filtMatrix
        demodMat = self.demodMatrix

        refIndex = 0

        dataDemod = np.transpose(np.column_stack((data[:, refIndex], data[:, channel])))

        result = np.multiply(dataDemod, filtWindow)
        result = result * np.transpose(demodMat)

        magResult = 2 * abs(result)

        phaseResult = np.angle(result)
        phaseResult = phaseResult[0, :] - phaseResult[1, :]  # filter.DAQPhase

        fluxSign = np.sign(phaseResult)
        signedFlux = np.multiply(fluxSign, magResult[1, :])

        return np.transpose(signedFlux)





if __name__=='__main__':

    import matplotlib.pyplot as plt
    myfilt = filter(1000,np.array([20000,22000,24000,26000,28000,30000,32000,34000]), 100000)


    myfilt.filterGen(0.0005)

    plt.plot(myfilt.filtArray)
    plt.show()
    b = 0