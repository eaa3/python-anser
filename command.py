""" launcher script to run the Anser EMT system"""

from emcalibration import EMCalibration
from emtracker import EMTracker
import argparse
import utils.utils as utils
from sensor.sensor import Sensor
import time
import sys

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

    print('speed: ', end='')
    speed = config['system']['speed']
    print(speed)

    print('Samples per acquisition: ', end='')
    print(config['filter']['num_samples'][speed])

    print('Sampling Frequency: ', end='')
    print(config['filter']['sampling_freq'])

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


def create_config(args):
    config = None
    if hasattr(args, 'config') and args.config is not None:
        config = utils.import_config_settings(args.config)
        if config is None:
            print('Config does not exist ')
            sys.exit(1)
    else:
        config = utils.import_config_settings('config_1.yaml')

    if hasattr(args, 'speed') and args.speed is not None:
        config['system']['speed'] = args.speed

    if hasattr(args, 'ports') and args.ports is not None:
        channels = []
        for port in args.ports:
            channel = utils.convert_port_num_to_channel_num(port)
            channels.append(channel)
        config['system']['channels'] = sorted(channels)

    if hasattr(args, 'grid') and args.grid is not None:
        config['system']['device_cal'] = args.grid

    if hasattr(args, 'frequencies') and args.frequencies is not None:
        config['filter']['freqs'] = list(args.frequencies)

    if hasattr(args, 'frequencysample') and args.frequencysample is not None:
        config['filter']['sampling_freq'] = args.frequencysample

    if hasattr(args, 'samplelength') and args.samplelength is not None:
        config['filter']['num_samples'] = args.samplelength

    if hasattr(args, 'controller') and args.controller is not None:
        controller_option = 1
        config['system']['serial_name'] = args.controller

    if hasattr(args, 'updaterate') and args.updaterate is not None:
        config['system']['update_delay'] = 1/args.updaterate

    if hasattr(args, 'modeltype') and args.modeltype is not None:
        config['model']['model_name'] = args.modeltype

    if hasattr(args, 'hardware') and args.hardware is not None:
        config['system']['device_type'] = args.hardware

    if hasattr(args, 'devicename') and args.devicename is not None:
        config['system']['device_name'] = args.devicename

    if hasattr(args, 'verbosity') and args.verbosity is not None:
        config['solver']['verbosity'] = args.verbosity

    if hasattr(args, 'igtport') and args.igtport is not None:
        config['system']['igt_port'] = args.igtport

    if hasattr(args, 'solver') and args.solver is not None:
        config['solver']['method'] = args.solver

    if hasattr(args, 'jacobian') and args.jacobian is not None:
        config['solver']['jacobian'] = args.jacobian

    if hasattr(args, 'igt') and args.igt is not None:
        config['system']['igt'] = args.igt

    if hasattr(args, 'print') and args.print is not None:
        config['system']['print'] = args.print

    if hasattr(args, 'flip') and args.flip is not None:
        config['system']['flip_list'] = list(args.flip)

    return config



def start_tracking(config, sensors):
    anser = None
    try:
        anser = EMTracker(config)
        anser.sensors = sensors
        anser.start_acquisition()
        #anser.flipflags = flip_option
        print("System Running")
        print("Press Ctrl-C to exit...")
        anser.run()
    except KeyboardInterrupt:
        anser.stop()
        time.sleep(.2)
        anser.stop_acquisition()
        print('System stopped')
        exit()
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    # Create Sensor Command
    create_sensor_parser = subparsers.add_parser('add', help='create a new sensor', description='EXAMPLE COMMAND: python command.py add sensor1 --description UCC --dof 5')
    create_sensor_parser.add_argument('sensorname', action='store', help='sensor name')
    create_sensor_parser.add_argument('-d', '--description', action='store', help='sensor description')
    create_sensor_parser.add_argument('-df','--dof', type=int, choices=[5,6], help='DOF - Degrees of Freedom', default=5)
    create_sensor_parser.set_defaults(which='add')

    # Remove Sensor Command
    remove_sensor_parser = subparsers.add_parser('remove', help='Remove sensor', description='EXAMPLE COMMAND: python command.py remove sensor1')
    remove_sensor_parser.add_argument('sensorname', action='store', help='name of sensor to remove')
    remove_sensor_parser.set_defaults(which='remove')

    # List all sensors Command
    list_parser = subparsers.add_parser('list', help='list all available sensors', description='EXAMPLE COMMAND: python command.py list')
    list_parser.add_argument('-c', '--calibration',action='store_true', help='show calibration data', default='store_false')
    list_parser.set_defaults(which='list')

    # Common arguments shared by Calibrate & Tracking commands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-d', '--devicename', type=str,
                               help='Name of the data acquisition instance being used (default="Dev1")')
    parent_parser.add_argument('-fs', '--frequencysample', type=int,
                        help='The desired sampling frequency for each sensor (default=100000)')
    parent_parser.add_argument('-f', '--frequencies', type=int,
                        help='(*Advanced*) List of transmission frequencies (Hz) to use.'
                             ' (default=[20000,22000,24000,26000,28000,30000,32000,34000])')
    parent_parser.add_argument('-c', '--controller', metavar='PORTNAME', type=int,
                        help='(*Advanced*) Connect to the MCU of the Anser system to allow programming of frequencies ')
    parent_parser.add_argument('-l', '--samplelength', type=int,
                        help='The block size or number of samples ')
    parent_parser.add_argument('-u', '--updaterate', type=int,
                        help='Speed in Hz for update rate of each sensor. This is approximate')
    parent_parser.add_argument('-m', '--modeltype', type=str,
                        help='Select the magnetic model to use with the system. (default="square")')
    parent_parser.add_argument('-t', '--hardwaretype', type=str,
                        help='Type of data acquisition unit being used (default="nidaq")')
    parent_parser.add_argument('-v', '--verbosity', type=int,
                        help='Set the level of verbosity of the solver algorithm (default=0)')
    parent_parser.add_argument('--grid', type=str,
                        help='Calibration grid type (7x7 (default, 9x9, Lego (prototype)))')
    parent_parser.add_argument('--config', type=str,
                               help='Configuration file used. Default is Config_1.yaml')

    # Calibrate Command
    calibrate_parser = subparsers.add_parser('calibrate', help='Perform Calibration', parents=[parent_parser], description='EXAMPLE COMMAND: python command.py calibrate sensor1 2')
    calibrate_parser.add_argument('sensorname', action='store', help='Name of sensor')
    calibrate_parser.add_argument('port',metavar='port', type=int, choices=range(1,5), help='The system port the sensor is connected to. Options={1,2,3,4}' )
    calibrate_parser.set_defaults(which='calibrate')

    # Tracking Command
    track_parser = subparsers.add_parser('track', help='Track sensors', parents=[parent_parser], description='EXAMPLE COMMAND: python command.py track sensor1,sensor2 1,2 --speed 1 ')
    track_parser.add_argument('sensornames',type=lambda s: list(map(str, s.split(","))), help='Name of sensors. Must be seperated by comma e.g sensor1, sensor2')
    track_parser.add_argument('ports', type=lambda s: list(map(int, s.split(","))), help='The system port the sensor is connected to. Must be seperated by comma e.g 1,2. Options={1,2,3,4}' )
    track_parser.add_argument('--speed', type=int, choices=range(1,5), help='Speed of the system', default=1)
    track_parser.add_argument('-i', '--igt', action='store_true', help='Enable an OpenIGTLink transform server. A seperate connection will be created for each sensor',default=False)
    track_parser.add_argument('-p', '--print', action='store_true', help='Print the positions as vectors on the command line')
    track_parser.add_argument('-P', '--igtport', type=int, help='port used to host the server (default=18944)')
    track_parser.add_argument('-fl', '--flip', type=lambda s: list(map(int, s.split(","))), help='Flip the orientation of the 5-DOF sensor', required=False)
    track_parser.add_argument('--solver', type=str, help='Type of solving algorithm to use (lm, trf, dogbox)')
    track_parser.add_argument('--jacobian', type=str, help='Method of computing the Jacobian matrix (2-point (fast), 3-point (slow, more accurate))')
    track_parser.set_defaults(which='track')

    args = parser.parse_args()
    print_info()

    if hasattr(args, 'which'):
        command = args.which
        if command == 'add':
            if utils.add_sensor(args.sensorname, args.description, args.dof):
                print('New sensor \'{}\' added'.format(args.sensorname))
            else:
                print('Could not add sensor\'{}\'.'.format(args.sensorname))
        elif command == 'remove':
            if utils.remove_sensor(args.sensorname):
                print('Sensor \'{}\' Removed.'.format(args.sensorname))
            else:
                print('Sensor \'{}\' could not be found.'.format(args.sensorname))
        elif command == 'list':
            print('List of available Sensors')
            print('--------------------------')
            for index, file in enumerate(utils.get_all_sensor_files()):
                sensor_settings = utils.import_sensor_settings(utils.convert_file_name_to_sensor_name(file.title()))
                sensor = Sensor(sensor_settings)
                print('{}.  Sensor Name: {}'.format(index+1, sensor.name))
                print('     Description: {}'.format(sensor.description))
                print('     DOF: {}'.format(sensor.dof))
                if args.calibration is True:
                    print('     Calibration: ')
                    for key, value in sensor.calibration.items():
                        print('         {}: {}'.format(key, value))
                print('\n')
        elif command == 'calibrate':
            try:
                config = create_config(args)
                sensor_settings = utils.import_sensor_settings(args.sensorname)
                if sensor_settings is None:
                    print('Sensor \'{}\' was not found'.format(args.sensorname))
                    sys.exit(1)
                sensor = Sensor(sensor_settings)
                sensor.channel = utils.convert_port_num_to_channel_num(args.port)

                calibration = EMCalibration(sensor, config)
                for i in range(calibration.cal.numPoints):
                    print('Point %d' % (i + 1), '...')
                    input('')
                    calibration.next()

                print('calibrating...')
                if calibration.calibrate():
                    print('Calibration was successful')
                else:
                    print('Calibration was unsuccessful')
            except Exception as e:
                print(str(e))

        elif command == 'track':
            try:
                config = create_config(args)
                sensors = []
                for name in args.sensornames:
                    sensor_settings = utils.import_sensor_settings(name)
                    if sensor_settings is None:
                        print('Sensor \'{}\' was not found'.format(name))
                        sys.exit(1)
                    sensor = Sensor(sensor_settings)
                    sensors.append(sensor)

                for sensor, port in zip(sensors, args.ports):
                    if port in range(1,9):
                        sensor.channel = utils.convert_port_num_to_channel_num(port)
                    else:
                        print('Invalid port please choose from (1-8) ')
                        sys.exit(1)
                print_settings(config)
                start_tracking(config, sensors)
            except Exception as e:
                print(str(e))


