import time
import numpy as np
from serial import Serial
import serial.tools.list_ports
import os
import sys
from shutil import copyfile
import utils.settings as settings
import ruamel.yaml as ruamel_yaml
from sensor.sensor import Sensor

SENSOR_PREFIX = 'sensor_'
CONFIG_PREFIX = 'config_'
SENSOR_DIR_NAME = 'config/sensors'
TEMPLATE_DIR_NAME='templates'
CONFIG_DIR_NAME = 'config/configs'
YAML_EXTENSION = '.yaml'
SENSOR_TEMPLATE_FILE_PATH = 'config/templates/sensor_template.yaml'
PACKAGE_NAME = 'python-anser'


def convert_igt_message_to_text(message):
    text = ''
    for k, v in message.items():
        if k is 'timestamp':
            v = time.ctime(int(v) / 1000)

        text += '\n' + '<html><p><b>{}:</b> {}</p></html>'.format(k.title(), v) + '\n'
    return text


#TODO: include dof parameter
def convert_port_num_to_channel_num(port_num):
    return port_num * 2 - 1


def convert_channels_to_ports(channels):
    ports = []
    for index, channel in enumerate(channels):
        ports.append(int(np.floor((channel + 1)/2)))
    return ports


def convert_samples_to_fft_dbs(samples, channel):
    if channel < len(samples[0]):
        samples = samples[:, channel]
        block_size = len(samples)
        ft = np.fft.fft(samples, axis=0)
        n = len(ft) / 2
        ft = ft[range(int(n))]
        magnitudes = abs(ft)
        magnitudes_in_dbs = 20 * np.log10(magnitudes / block_size)
        magnitudes_in_dbs = [val for sublist in magnitudes_in_dbs for val in sublist]
        average = np.average(magnitudes_in_dbs)
        magnitudes_in_dbs[0] = average
        return magnitudes_in_dbs
    return None


def is_frequency_active(freq, samples, sampling_freq,):
    block_size = len(samples)
    magnitudes = convert_samples_to_fft_dbs(samples, 0)
    flattened_sorted = sorted(magnitudes)
    top_8_frequencies = []
    for i in range(1, 9):
        top_8_frequencies.append(flattened_sorted[i * -1])
    # better to check if frequency is above a threshold
    if magnitudes[int(freq / (sampling_freq/ block_size))] in top_8_frequencies:
            return True
    return False


def are_frequencies_active(freq_list, samples, sampling_freq):
    fs = sampling_freq
    block_size = len(samples)
    magnitudes = convert_samples_to_fft_dbs(samples, 0)
    flattened_sorted = sorted(magnitudes)
    top_8_frequencies = []
    for i in range(1, 9):
        top_8_frequencies.append(flattened_sorted[i * -1])
    # better to check if frequency is above a threshold

    for index, frequency in enumerate(freq_list):
        if magnitudes[int(frequency / (fs / block_size))] not in top_8_frequencies:
            print('coil causing failure:  {}, freq: {}'.format(index + 1, frequency))
            return False
    return True


def write_frequencies_to_teensy_from_list(freq_list):
    ports = list(serial.tools.list_ports.comports())
    response = '-1'
    command = 'FREQ'
    for index, freq in enumerate(freq_list):
            command += ':{}@{}'.format(index+1, freq)
    print(str(command))
    command += '\n'
    try:
        for p in ports:
            port = Serial(p.device)
            port.write(command.encode())
            time.sleep(.3)
            if port.in_waiting:
                response = port.read()
                if 0 == ord(response):
                    print('FREQUENCIES HAVE BEEN CHANGED - Talking to port {}, got response {}'.format(str(p), str(ord(response))))
                    return 0
    except Exception as e:
        print('FREQUENCIES HAVE NOT BEEN CHANGED' + str(e))
        return 1


def get_all_sensor_files():
    sensor_files = []
    for file in os.listdir(resource_path('./config/sensors/')):
        if YAML_EXTENSION and SENSOR_PREFIX in file.title().lower():
            sensor_files.append(file)
    return sensor_files


def get_all_config_files():
    config_files = []
    for file in os.listdir(resource_path('./config/configs/')):
        if YAML_EXTENSION and CONFIG_PREFIX in file.title().lower():
            config_files.append(file)
    return config_files


def convert_file_name_to_sensor_name(file):
    sensor_name = file.title().lower().replace(SENSOR_PREFIX, '').replace(YAML_EXTENSION, '')
    return sensor_name.title()


def convert_sensor_name_to_file_name(sensor_name):
    file_name = SENSOR_PREFIX + sensor_name.strip().lower() + YAML_EXTENSION
    return file_name.title().lower()


def add_sensor(sensor_name, description, dof):
    if sensor_name != '':
        file_name = convert_sensor_name_to_file_name(sensor_name)
        try:
            # Creates a sensor file
            open(os.path.join(SENSOR_DIR_NAME, file_name), 'w')
            copyfile(SENSOR_TEMPLATE_FILE_PATH, os.path.join(SENSOR_DIR_NAME, file_name))
            sensor_settings = settings.import_settings_file('./config/sensors/' + file_name)
            sensor_settings['name'] = sensor_name
            sensor_settings['description'] = description
            sensor_settings['dof'] = dof
            settings.write_calibration(sensor_settings, './config/sensors/'+file_name)
            return True
        except Exception as e:
            print(str(e))
    return False


def remove_sensor(sensor_name):
    for file in os.listdir('./config/sensors/'):
        #TODO: this only works when lowercase
        if YAML_EXTENSION and SENSOR_PREFIX and sensor_name.lower() in file.title().lower():
            try:
                os.remove(os.path.join(SENSOR_DIR_NAME, convert_sensor_name_to_file_name(sensor_name)))
                return True
            except Exception as e:
                print(str(e))
                return False

def get_sensors():
    sensors = []
    sensorFiles = get_all_sensor_files()
    for file in sensorFiles:
        name = convert_file_name_to_sensor_name(file)
        sensor_settings = import_sensor_settings(name)
        sensor = Sensor(sensor_settings)
        channels = get_working_channels(sensor.calibration)
        sensor.ports = convert_channels_to_ports(channels)
        sensors.append(sensor)
    return sensors


#TODO: change this so it uses the get_calibration() function
def get_working_channels(calibration):
    channels = []
    for channel in calibration.keys():
        if calibration[channel] != [0]*8:
            if channel not in channels:
                channels.append(channel)
    return channels


def convert_samples_to_fft(samples, channel, sampling_freq):
    sessionData = samples[:, channel]
    # FFT
    ft = np.fft.fft(sessionData, axis=0)
    # length of signal
    block_size = len(ft)  # 3000
    block_size_half = block_size / 2  # 1500
    freq = np.arange(block_size_half) / block_size_half
    # One side frequency range
    ft = ft[range(int(block_size_half))]
    # magnitudes
    magnitudes = abs(ft)
    # log + + Normalisation
    magnitudes_in_dbs = 20 * np.log10(magnitudes / block_size)
    magnitudes_in_dbs = [val for sublist in magnitudes_in_dbs for val in sublist]
    # remove dc component at point 1
    magnitudes_in_dbs[0] = np.average(magnitudes_in_dbs)
    # TODO: fix this
    fs = sampling_freq
    #block_size = blocksize
    frequency_resolution =  fs / block_size
    frequencies = np.arange(block_size_half * frequency_resolution, step=frequency_resolution)
    #for index, num in enumerate(magnitudes_in_dbs):
    #    print('{}: {}'.format(index, num))
    '''
    text_file = open("test.txt", "w")
    for index, f in enumerate(frequencies):
        line = str(f) + ' <--->' + str(magnitudes_in_dbs[int(round(f / (sampling_freq/block_size)))]) + ' exactly:{} '.format(f/(sampling_freq/block_size)) + ' resources:{}'.format(frequency_resolution) + 'bin nr:{}'.format(index) + '\n'
        text_file.write(line)
        print(line)
    text_file.close()
    '''
    return frequencies, magnitudes_in_dbs


def import_config_settings(name):
    try:
        name = name.strip().lower()
        if YAML_EXTENSION not in name:
            filename = name + YAML_EXTENSION
        else:
            filename = name
        filepath = os.path.join(CONFIG_DIR_NAME, filename)
        return import_settings(filepath)
    except Exception as e:
        return None


def import_sensor_settings(name):
    try:
        name = name.strip().lower()
        if YAML_EXTENSION not in name:
            filename = convert_sensor_name_to_file_name(name)
        else:
            filename = name
        filepath = os.path.join(SENSOR_DIR_NAME, filename)
        return import_settings(filepath)
    except Exception as e:
        return None


def import_settings(filename):
    try:
        with open(filename, 'r') as stream:
            settings_dict = ruamel_yaml.load(stream, Loader=ruamel_yaml.Loader)
            stream.close()
            return settings_dict
    except Exception as e:
        return None


def export_settings(settings, filepath):
    try:
        with open(filepath, 'w') as stream:
            ruamel_yaml.dump(settings, stream)
    except Exception as e:
        return False
    return True


def get_sensor_filepath(name):
    try:
        name = name.strip().lower()
        if YAML_EXTENSION not in name:
            filename = convert_sensor_name_to_file_name(name)
        else:
            filename = name
        filepath = os.path.join(SENSOR_DIR_NAME, filename)
        return filepath
    except Exception as e:
        return None


def get_config_filepath(name):
    try:
        name = name.strip().lower()
        if YAML_EXTENSION not in name:
            filename = name + YAML_EXTENSION
        else:
            filename = name
        filepath = os.path.join(CONFIG_DIR_NAME, filename)
        return filepath
    except Exception as e:
        return None


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


# Necessary if current working directory is not python-anser e.g qt-anser
def get_relative_filepath(file):
    cwd = os.getcwd()
    if cwd is PACKAGE_NAME:
        return file
    else:
        path = os.path.abspath(os.path.dirname(__file__))
        terminator = path.index(PACKAGE_NAME)
        test = path[:terminator]
        return os.path.join(os.path.dirname(test), PACKAGE_NAME, file.strip())
