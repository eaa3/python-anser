from anser import Anser
import numpy as np



# Simple object for storing all command arguments
class optionContainer(object):
    pass


# Miscellaneous functions.
def printInfo(channels=np.array([]),):
    print('\nAnser EMT')
    print('---------')
    print('An open-source electromagnetic tracking system')
    print('Copyright (c) 2017, Alex Jaeger, Kilian O\'Donoghue')
    print('All rights reserved.')
    print('This code is licensed under the BSD 3-Clause License.\n\n')

def printSettings(options):

    print('Sensor channels: ', end='')
    print(options.sensors_option)

    print('Transmitting frequencies: ', end='')
    print(options.freqselect_option)

    print('Sensor channels: ', end='')
    print(options.frequency_option)

    print('Samples per acquisition: ', end='')
    print(options.sample_option)

    print('Controller serial enabled: ', end='')
    print(controller_option)

    print('Serial port name: ', end='')
    print(options.controllername_option)

    print('Update rate: ', end='')
    print(1/(options.delay_option))


    print('Magnetic model type: ', end='')
    print(options.modeltype_option)

    print('Acquisition hardware type: ', end='')
    print(options.hardwaretype_option)

    print('Acquisition hardware name: ', end='')
    print(options.devicename_option)

    print('Server verbosity level: ', end='')
    print(options.verbosity_option)

    print('OpenIGTLink enable: ', end='')
    print(options.igt_option)

    print('OpenIGTLink port number: ', end='')
    print(options.port_option)

    print('Print positions enable: ', end='')
    print(options.print_option)

    print('Flip orientation enable: ', end='')
    print(options.flip_option)


    print('')







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
    parser.add_argument('-P', '--port', type=int,
                        help='The port used to host the server (default=18944)')
    parser.add_argument('-fl', '--flip', help='Flip the orientation of the 5-DOF sensor',
                        action='store_true', default=False)

    # Default system frequencies.
    default_freqs = [20000,22000,24000,26000,28000,30000,32000,34000]

    # Parse all arguments
    args = parser.parse_args()
    options = optionContainer()

    if args.sensors != None:
        sensors_option = ast.literal_eval(args.sensors)
    else:
        sensors_option = np.array([4,8,1])  # For Anser 1.0

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
        controllername_option = 'COM1'

    if args.updatespeed != None:
        delay_option =  1/args.updatespeed
    else:
        delay_option = 1e-10

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

    if args.port != None:
        port_option = args.port
    else:
        port_option = 18944

    igt_option = args.igt
    print_option = args.print
    flip_option = args.flip

    options.sensors_option = sensors_option
    options.freqselect_option = freqselect_option
    options.frequency_option = frequency_option
    options.sample_option = sample_option
    options.controller_option = controller_option
    options.controllername_option = controllername_option
    options.delay_option = delay_option
    options.modeltype_option = modeltype_option
    options.hardwaretype_option = hardwaretype_option
    options.devicename_option = devicename_option
    options.verbosity_option = verbosity_option
    options.port_option = port_option
    options.igt_option = igt_option
    options.print_option = print_option
    options.flip_option = flip_option


    printInfo()
    printSettings(options)

    # Create an instance of the tracking system
    anser = Anser(daqDeviceName=devicename_option, daqHardwareType=hardwaretype_option, sensors=sensors_option, igt=igt_option,
                           samples=sample_option, samplefreq=frequency_option, verbosity=verbosity_option,
                           solverType=1, modeltype=modeltype_option)

    # Initialise the tracking system DAQ
    anser.start()

    # Enable sensor flipping if needed. This should only be used for testing
    anser.angleFlip(flip_option)
    print("System Running")
    print("Press Ctrl-C to exit...")

    initcond1 = np.array([0.0, 0.0, 0.10, 0.0, 0.0])
    initcond2 = np.array([0.0, 0.0, 0.10, 0.0, 0.0])

    positions = np.zeros([150,5])
    means = np.zeros([49,5])
    index = 0
    try:

        while True:




           #positionVector = anser.getPosition(1)
           #initcond1 = positionVector
           #positionVector[3] = positionVector[3] + np.pi
           #positionMatrix = anser.vec2mat(positionVector)
           #anser.igtSendTransform(positionMatrix, device_name='Needle1')


            anser.solver.initialCond = initcond1
            anser.solver.calibration = anser.cal_Ch2
            positionVector = anser.getPosition(1)
            initcond1 = positionVector
            positionVector[3] = positionVector[3] + np.pi
            positionMatrix = anser.vec2mat(positionVector)
            anser.igtSendTransform(positionMatrix, device_name='Needle1')



            anser.solver.initialCond = initcond2
            anser.solver.calibration = anser.cal_Ch3
            positionVector = anser.getPosition(2)
            initcond2 = positionVector
            positionVector[3] = positionVector[3] + np.pi
            positionMatrix = anser.vec2mat(positionVector)
            anser.igtSendTransform(positionMatrix, device_name='Needle2')

            sleep(delay_option)








    except KeyboardInterrupt:
        exit()
        pass





