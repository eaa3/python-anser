from solver import solver
from daq import daq
from model import model
from filters import filter
from constants import u0, pi
import numpy as np
from time import sleep
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *

if __name__ == '__main__':
    myModel = model('square',25,length=70e-3,width=0.5e-3,spacing=0.25e-3, thick=1.6e-3 )

    myCal = np.array([0.0968, 0.0998, 0.1010, 0.1000, 0.0992, 0.0986, 0.0962, 0.0932])
    mySolver = solver(myCal, myModel, verbose=0)

    myDaq = daq('nidaq', daqName='Dev3', channels=np.array([4, 0]))
    myDaq.daqStart()

    myFilter = filter(1000)

    initialCond = np.array([0.0, 0.0, 0.14, 0.0, 0.0])
    mySolver.initialCond = initialCond

    myigt = PyIGTLink(localServer=True)



    while(1):
        data = myDaq.getData()

        demodresult = myFilter.demodulateSignalRef(data, 1)

        result = mySolver.solveLeastSquares(demodresult)
        mySolver.initialCond = np.array([0.0, 0.0, 0.14, 0.0, 0.0])
        mySolver.initialCond = np.array(result.x)
        #print('%f' % result.x[0], end=' ')
        #print('%f' % result.x[1], end=' ')
        #print('%f' % result.x[2], end=' ')
        #print('%f' % result.x[3], end=' ')
        #print('%f' % result.x[4])
        #print('')

        x = result.x[0]
        y = result.x[1]
        z = result.x[2]
        theta = result.x[3] + pi
        phi = result.x[4]


        positionMatrix = np.matrix([[np.cos(phi)*np.cos(theta), -np.sin(phi), np.cos(phi)*np.sin(theta), x*1000],
                                    [np.sin(phi)*np.cos(theta), np.cos(phi), np.sin(phi)*np.sin(theta), y*1000],
                                    [-np.sin(theta), 0, np.cos(theta), z*1000],
                                    [0, 0, 0, 1]])
        mymsg = TransformMessage(positionMatrix)
        myigt.add_message_to_send_queue(mymsg)
        sleep(0.001)



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
