import numpy as np
from numpy.matlib import repmat
from scipy.signal import firwin
from model.constants import pi

class Filter():
    def __init__(self, config):

        # The number of samples per frame acquired by the DAQ unit
        filter_config = config['filter']
        self.numSamples = filter_config['num_samples']
        # Define filter parameters
        self.numFreqs = filter_config['num_freqs']
        self.transFreqs = np.array([])
        for key, value in filter_config['freqs'].items():
            self.transFreqs = np.append(self.transFreqs, value)

        self.sampleFreq = filter_config['sampling_freq']
        self.cutoff = filter_config['cutoff_freq']
        self.windowType = filter_config['window_type']
        self.attenuation = filter_config['attenuation']
        self.passDC = filter_config['passdc']
        self.scale = filter_config['scale']

        self.numChannels = len(config['system']['channels'])
        # Generate digital input filter
        self.filtArray = np.array([])
        self.filtMatrix = np.matrix(self.filtArray, dtype=float)
        self.filterGen(self.cutoff, (self.windowType, self.attenuation), width=None, passDC=self.passDC,
                       scale=self.scale)

        self.demodArray = np.zeros([self.numFreqs, self.numSamples], dtype=complex)
        self.demodMatrix = np.matrix(self.demodArray)


        # TODO Create an intelligent way of calculating the DAQ phase offsets
        # self.daqPhaseOffset = 0

        # Generate demodulation matrix
        self.samplePeriod = 1/self.sampleFreq
        self.timeArray = np.linspace(0, (self.numSamples - 1) * self.samplePeriod, self.numSamples)
        for i in range(self.numFreqs):
            self.demodMatrix[i, :] = [np.exp(2*pi*self.transFreqs[i]*self.timeArray * 1j)]

    def filterGenAll(self, cutoff, window, numChannels, width=None, passDC=True, scale=True):
        self.filtArrayAll = firwin(self.numSamples, cutoff, width=width, window=window, pass_zero=passDC, scale=scale)
        self.filtMatrixAll = np.matrix(repmat(self.filtArrayAll, numChannels, 1))

    def filterGen(self, cutoff, window, width=None, passDC=True, scale=True):
        self.filtArray = firwin(self.numSamples, cutoff, width=width, window=window, pass_zero=passDC, scale=scale)
        self.filtMatrix = np.matrix(repmat(self.filtArray, 2, 1))

    def demodulateSignalAll(self, data):
        # This scaler approximately takes into account various sensor acquisition constants (cross sectional area, sensor
        # coil turns, amplifier gain etc.)
        # All these content parameters can be lumped into this single parameter 'mag_scale'
        # This initial scaling behaves as a _very_ rough calibration approximation, and merely serves to scale the
        # acquired sensor voltages (i.e. fluxes) at each frequency such that they lie when the same order of magnitude as the magnetic
        # field model. This helps convergence of the final calibration algorithm which yields the actual calibration results.
        mag_scale = 1e6

        # Reference channel for the current sensing
        refIndex = 0

        dataDemod = np.transpose(data)

        result = np.multiply(dataDemod, self.filtMatrixAll)
        result = result * np.transpose(self.demodMatrix)

        magResult = 2 * abs(result)
        phaseResult = np.angle(result)

        # Convert any negative angles to positive angles
        for x in np.nditer(phaseResult, op_flags=['readwrite']):
            if x < 0:
                x[...] = 2 * pi + x
            else:
                pass

        phaseDiff = phaseResult[1, :] - (phaseResult[0, :] - np.array(
            [0.3142, 0.3456, 0.3770, 0.4084, 0.4398, 0.4712, 0.5027, 0.5341]))  # filter.DAQPhase

        for x in np.nditer(phaseDiff, op_flags=['readwrite']):
            if np.abs(x) > pi:
                x[...] = -np.sign(x) * (2 * pi - np.abs(x))
            else:
                pass

        fluxSign = np.sign(phaseDiff)
        signedFlux = np.multiply(fluxSign, magResult[1, :])
        signedFlux = np.divide(signedFlux, np.ones([1, 8]) * mag_scale)

        return np.transpose(signedFlux)

    def demodulateSignalRef(self, data, channel):

        # This scaler approximately takes into account various sensor acquisition constants (cross sectional area, sensor
        # coil turns, amplifier gain etc.)
        # All these content parameters can be lumped into this single parameter 'mag_scale'
        # This initial scaling behaves as a _very_ rough calibration approximation, and merely serves to scale the
        # acquired sensor voltages (i.e. fluxes) at each frequency such that they lie when the same order of magnitude as the magnetic
        # field model. This helps convergence of the final calibration algorithm which yields the actual calibration results.
        mag_scale = 1e6

        # Reference channel for the current sensing
        # TODO This should be obtained from a file.
        refIndex = 0

        dataDemod = np.transpose(np.column_stack((data[:, refIndex], data[:, channel])))

        result = np.multiply(dataDemod, self.filtMatrix)
        result = result * np.transpose(self.demodMatrix)

        magResult = 2 * abs(result)
        phaseResult = np.angle(result)

        # Convert any negative angles to positive angles
        for x in np.nditer(phaseResult, op_flags=['readwrite']):
            if x < 0:
                x[...] = 2*pi + x
            else:
                pass

        phaseDiff = phaseResult[1, :] - (phaseResult[0, :] - np.array([0.3142, 0.3456, 0.3770, 0.4084, 0.4398, 0.4712, 0.5027, 0.5341]))# filter.DAQPhase

        for x in np.nditer(phaseDiff, op_flags=['readwrite']):
            if np.abs(x) > pi:
                x[...] = -np.sign(x)*(2*pi-np.abs(x))
            else:
                pass

        fluxSign = np.sign(phaseDiff)
        signedFlux = np.multiply(fluxSign, magResult[1, :])
        signedFluxScaled = np.divide(signedFlux, np.ones([1,8]) * mag_scale)

        return np.transpose(signedFluxScaled)
