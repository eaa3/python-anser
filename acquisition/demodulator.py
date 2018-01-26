import numpy as np


def demodulateSignals(data, demodOptions):


    filtWindow = demodOptions.Window
    demodMat = demodOptions.Demod


    refIndex = 0

    noSignals = data.shape[1]


    data = np.transpose(data)

    result = (np.multiply(data, filtWindow) * demodMat)

    magResult = 2 * abs(result)
    phaseResult = np.angle(result)



    phaseResult = phaseResult[0, :] - phaseResult - demodOptions.DAQPhase


    fluxSign = np.sign(phaseResult)
    fluxSensors = magResult[1:noSignals, :]

    signedFlux = np.multiply(fluxSign, fluxSensors)



    return np.transpose(signedFlux)



