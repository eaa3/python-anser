from anser import Anser
from calibration.calibration import Calibration
from time import sleep, time
import ast
import argparse
import numpy as np
from utils.settings import get_settings

# Miscellaneous functions.
def print_info():
    print('\nAnser EMT')
    print('---------')
    print('An open-source electromagnetic tracking system')
    print('Copyright (c) 2017, Alex Jaeger, Kilian O\'Donoghue')
    print('All rights reserved.')
    print('This code is licensed under the BSD 3-Clause License.\n\n')


def print_settings(config):

    print('Sensor channels: ', end='')
    print(config['system']['channels'])

    print('Transmitting frequencies: ', end='')
    print(config['filter']['freqs'])

    print('Samples per acquisition: ', end='')
    print(config['filter']['num_samples'])

    print('Serial port name: ', end='')
    print(config['system']['serial_name'])

    print('Update rate: ', end='')
    print(1 / (config['system']['update_delay']))

    print('Magnetic model type: ', end='')
    print(config['model']['model_name'])

    print('Acquisition hardware type: ', end='')
    print(config['system']['device_type'])

    print('Acquisition hardware name: ', end='')
    print(config['system']['device_name'])

    print('Server verbosity level: ', end='')
    print(config['solver']['verbosity'])

    print('OpenIGTLink enable: ', end='')
    print(config['system']['igt'])

    print('OpenIGTLink port number: ', end='')
    print(config['system']['igt_port'])

    print('Print positions enable: ', end='')
    print(config['system']['print'])

    print('Flip orientation enable: ', end='')
    print(config['system']['flip_enable'])

    print('')


if __name__ == '__main__':

    config = get_settings()

    parser = argparse.ArgumentParser(description='Settings for the Anser EMT system. If no settings are provided then'
                                                 ' tracking using the defauly config file with begin')
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
                        action='append', required=False)
    parser.add_argument('--calibrate', action='store_true', help='Perform calibration', default=False)

    # Parse all arguments
    args = parser.parse_args()

    if args.sensors is not None:
        config['system']['channels'] = ast.literal_eval(args.sensors)

    if args.frequencies is not None:
        config['filter']['freqs'] = ast.literal_eval(args.frequencies)

    if args.frequencysample is not None:
        config['filter']['sampling_freq'] = args.frequencysample

    if args.samplelength is not None:
        config['filter']['num_samples'] = args.samplelength

    if args.controller is not None:
        controller_option = 1
        config['system']['serial_name'] = args.controller

    if args.updatespeed is not None:
        config['system']['update_delay'] = 1/args.updatespeed

    if args.modeltype is not None:
        config['model']['model_name'] = args.modeltype

    if args.hardwaretype is not None:
        config['system']['device_type'] = args.hardware

    if args.devicename is not None:
        config['system']['device_name'] = args.devicename

    if args.verbosity is not None:
        config['solver']['verbosity'] = args.verbosity

    if args.port is not None:
        config['system']['igt_port'] = args.port

    flip_option = []
    if args.flip is not None:
        flip_option = list(args.flip)
    igt_option = args.igt
    print_option = args.print

    print_info()


    if args.calibrate == True:

        sensorNo = int(input('\n Enter sensor id to calibrate: '))
        anser = Anser(config)
        cal = Calibration('7x7', anser.model)
        cal.fieldData = np.zeros([cal.numCoils, cal.numPoints])


        anser.start_acquisition()
        for i in range(cal.numPoints):
            print('Point %d' % (i + 1), '...')
            input('')
            anser.sample_update()
            cal.fieldData[:, i] = np.column_stack(anser.filter.demodulateSignalRef(anser.data, sensorNo))
        pass
        anser.stop_acquisition()

        print('Calibrating...')
        result = cal.calibrateZ()
        print('Done\n')
    else:

        # Print system info
        print_settings(config)

        # Create an instance of the tracking system
        anser = Anser(config)
        # Initialise the tracking system DAQ
        anser.start_acquisition()
        anser.flipflags = flip_option

        print("System Running")
        print("Press Ctrl-C to exit...")

        delay = config['system']['update_delay']


        try:

            while True:

                sleep(delay)
                t = time()
                anser.sample_update()
                positionVector1, positionMatrix1 = anser.get_position(1, igtname='Needle1')



        except KeyboardInterrupt:
            anser.stop_acquisition()
            exit()
            pass








