import numpy as np
from model.model import model
from solver.solver import solver
from acquisition.daq import daq
from acquisition.filters import filter
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *
from model.constants import pi



class TrackingSystem():

    def __init__(self, daqDeviceName='Dev1', daqHardwareType='nidaq', freqs=np.array([20000,22000,24000,26000,28000,30000,32000,34000]), samples=1000,
                      samplefreq=1e5, serial='', modeltype='square', solverType=1, verbosity=0, igt=False, sensors=np.array([])):


        self.cal = np.array([0.0890,   0.0930,    0.0945,    0.0939,    0.0946,    0.0936,    0.0922,    0.0888])

        self.model = model(modeltype, 25, length=70e-3, width=0.5e-3, spacing=0.25e-3, thick=1.6e-3)


        if solverType == 1:
            self.solver = solver(self.cal, solverType, self.model, verbose=verbosity,
                                 bounds=([-0.5, -0.5, 0, -pi, -3*pi], [0.5, 0.5, 0.5, pi, 3*pi]),
                                 initialCond=[0.0, 0.0, 0.10, 0.0, 0.0])
        elif solverType == 2:
            self.solver = solver(self.cal, solverType, self.model, verbose=verbosity,
                                 bounds=([-0.3, -0.3, 0, -1,-1,-1],[0.3, 0.3, 0.3, 1, 1, 1]),
                                 initialCond=[0.0, 0.0, 0.15, 0, 0, 1])



        self.daq = daq('nidaq', daqName=daqDeviceName, channels=sensors, numSamples=samples)
        self.filter = filter(self.daq, freqs, sampleFreq=samplefreq)

        # Create OpenIGTLink client connection
        if igt==True:
            self.igtconn = PyIGTLink(localServer=True)

        self.flipFlag = False



    def vec2mat(self, array=np.array(np.zeros([1,5]))):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat


    def igtSendTransform(self, mat):

        matmsg = TransformMessage(mat)
        self.igtconn.add_message_to_send_queue(matmsg)

    def getResolveSensor(self, sensorNo):

        data = self.daq.getData()
        demod = self.filter.demodulateSignalRef(data, sensorNo)
        result = self.solver.solveLeastSquares(demod)

        # Wrap around angles to preserve contraints
        wrapresult = self.angleWrap(result)

        self.solver.initialCond = wrapresult.x

        return np.array(wrapresult.x)

    def getPosition(self, sensorNo):

        position = self.getResolveSensor(sensorNo)

        if self.flipFlag == True:
            position[3] = position[3] + pi

        return position


    def angleWrap(self, result):
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] - 2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi
        return result

    def start(self):
        self.daq.daqStart()

    def stop(self):
        self.daq.daqStop()

    def printInfo(self):
        print('\nAnser EMT')
        print('---------')
        print('An open-source electromagnetic tracking system')
        print('Copyright (c) 2017, Alex Jaeger, Kilian O\'Donoghue')
        print('All rights reserved.')
        print('This code is licensed under the BSD 3-Clause License.\n')



    def printPosition(self, position):
        print('%0.4f %0.4f %0.4f %0.4f %0.4f'
              % (position[0] * 1000, position[1] * 1000, position[2] * 1000, position[3], position[4]))


    def angleFlip(self, flag):
        self.flipFlag = flag


if __name__ == '__main__':

    from time import sleep
    import ast
    import argparse


    parser = argparse.ArgumentParser(description='Settings for the Anser EMT system. If no settings are provided then tracking for sensor channel 1 will begin.')
    parser.add_argument('-s', '--sensors', help='A list of sensors to track')
    parser.add_argument('-i', '--igt', action='store_true', help='Enable an OpenIGTLink transform server. A seperate '
                                                                 'connection will be created for each sensor', default=True)
    parser.add_argument('-fs', '--frequencysample', type=int,
                        help='The desired sampling frequency for each sensor (default=100000)')
    parser.add_argument('-f', '--frequencies', type=int,
                        help='(*Advanced*) List of transmission frequencies (Hz) to use.'
                             ' (default=[20000,22000,24000,26000,28000,30000,32000,34000])')
    parser.add_argument('-c', '--controller', metavar='PORTNAME', type=int,
                        help='(*Advanced*) Connect to the MCU of the Anser system to allow programming of frequencies ')
    parser.add_argument('-l', '--samplelength', type=int,
                        help='The desired sampling frequency for each sensor (default=100000)')
    parser.add_argument('-u', '--updatespeed', type=int,
                        help='Speed in Hz for update rate of each sensor. This is approximate')
    parser.add_argument('-p', '--print', action='store_true',
                        help='Print the positions as vectors on the command line')
    parser.add_argument('-m', '--modeltype', type=str,
                        help='Select the magnetic model to use with the system. (default="square")')
    parser.add_argument('-d', '--devicename', type=str,
                        help='Name of the data acquisition instance being used (default="Dev1")')
    parser.add_argument('-t', '--hardwaretype', type=str,
                        help='Type of data acquisition unit being used (default="nidaq")')
    parser.add_argument('-v', '--verbosity', type=int,
                        help='Set the level of verbosity of the solver algorithm (default=0)')
    parser.add_argument('-a', '--ipaddress', type=int,
                        help='The port used to host the server (default=18944)')



    # Defaults
    default_freqs = [20000,22000,24000,26000,28000,30000,32000,34000]





    args = parser.parse_args()

    if args.sensors != None:
        sensors_option = ast.literal_eval(args.sensors)
    else:
        sensors_option = np.array([4,0])  # For Anser 1.0

    if args.frequencies != None:
        freqselect_option = ast.literal_eval(args.frequencies)
    else:
        freqselect_option = default_freqs  # For Anser 1.0

    if args.frequencysample != None:
        frequency_option = args.frequencysample
    else:
        frequency_option = 100000

    if args.samplelength != None:
        sample_option = args.samplelength
    else:
        sample_option = 1000

    if args.controller != None:
        controller_option = 1
        controllername_option = args.controller
    else:
        controller_option = 0

    if args.updatespeed != None:
        delay_time =  1/args.updatespeed
    else:
        delay_time = 0

    if args.modeltype != None:
        modeltype_option = args.modeltype
    else:
        modeltype_option = 'square'

    if args.hardwaretype != None:
        hardwaretype_option = args.hardware
    else:
        hardwaretype_option = 'nidaq'

    devicename_option = 'Dev1'
    if args.devicename != None:
        devicename_option = args.devicename
    else:
        if hardwaretype_option == 'nidaq':
            devicename_option = 'Dev1'
        elif hardwaretype_option == 'mccdaq':
            devicename_option = 'board1'

    if args.verbosity != None:
        verbosity_option = args.verbosity
    else:
        verbosity_option = 0

    if args.ipaddress != None:
        ipaddress_option = args.ipaddress
    else:
        ipaddress_option_option = 18944


    igt_option = args.igt
    print_option = args.print

    anser = TrackingSystem(daqDeviceName=devicename_option, daqHardwareType=hardwaretype_option, sensors=sensors_option, igt=igt_option,
                           samples=sample_option, samplefreq=frequency_option, verbosity=verbosity_option,
                           solverType=1, modeltype=modeltype_option)
    anser.printInfo()
    anser.start()

    try:
        print("System Running")
        print("Press Ctrl-C to exit...")
        anser.angleFlip(True)
        while True:

            po = anser.getPosition(1)





            po_mat = anser.vec2mat(po)
            anser.igtSendTransform(po_mat)


            if print_option == True:
                anser.printPosition(po)

            sleep(delay_time)
    except KeyboardInterrupt:
        exit()
        pass
