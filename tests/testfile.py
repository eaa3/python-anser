from solver import solver
from daq import daq
from model import model
from filters import filter
from constants import u0, pi
import numpy as np


if __name__ == '__main__':
    myModel = model('square',25,length=70e-3,width=0.5e-3,spacing=0.25e-3, thick=1.6e-3 )
    mySolver = solver(myModel)

    myDaq = daq('nidaq', daqName='Dev3', channels=np.array([0,4]))
    myDaq.daqStart()

    myFilter = filter(1000)

    data = myDaq.getData()

    demodresult = myFilter.demodulateSignalRef(data, 1)

    # Enter simulated sensor position and orientation here
    testPoint = np.array([0.0, 0.0, 0.14, 0.8, 0.2])
    # Calculate the flux density at the simulated sensor position
    [Hx, Hy, Hz] = myModel.getField(testPoint)

    Bx = Hx * u0
    By = Hy * u0
    Bz = Hz * u0

    # Determine the flux cutting the sensor at the simulated orientation.
    # Dot product of the B vector with the A vector (the sensor orientation)
    Bxsensor = Bx * (np.sin(testPoint[3]) * np.cos(testPoint[4]))
    Bysensor = By * (np.sin(testPoint[3]) * np.sin(testPoint[4]))
    Bzsensor = Bz * (np.cos(testPoint[3]))

    Btest = Bxsensor + Bysensor + Bzsensor

    initialCond = np.array([0.1, 0.14, 0.14, 0.2, 0.3])

    mySolver.initialCond = initialCond
    result = mySolver.solveLeastSquares(Btest)


    for i in result.x:
        print('%f' % i)
