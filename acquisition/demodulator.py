import numpy as np
from filters import filter
from nidaq import nidaq



def demodulateSignals(data, channelRow, filter):


    filtWindow = filter.filtMatrix
    demodMat = filter.demodMatrix

    refIndex = 0

    dataDemod = np.transpose(np.column_stack((data[:, refIndex], data[:, channelRow])))

    result = np.multiply(dataDemod, filtWindow)
    result = result * np.transpose(demodMat)

    magResult = 2 * abs(result)

    phaseResult = np.angle(result)
    phaseResult = phaseResult[0, :] - phaseResult[1, :]  # filter.DAQPhase

    fluxSign = np.sign(phaseResult)
    signedFlux = np.multiply(fluxSign, magResult[1,:])

    return np.transpose(signedFlux)


if __name__=='__main__':

    import matplotlib.pyplot as plt

    myfilt = filter()
    mydaq =  nidaq(dev_name='Dev3',channels=np.array([2, 4]), data_len=myfilt.numSamples, sampleFreq=myfilt.sampleFreq)
    mydaq.StartTask()
    data = mydaq.get_data_matrix()
    plt.plot(myfilt.filtArray)
    plt.show()
    plt.plot(myfilt.filtArray)
    plt.show()

    demodulateSignals(data,1, myfilt)