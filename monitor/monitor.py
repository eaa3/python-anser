import serial
import serial.tools.list_ports
import time
import numpy as np
import utils.utils as utils
from rx.subjects import Subject
from rx.concurrency import NewThreadScheduler
import sys as sys

OK_CODE_TEENSY = 0
OK_CODE = 1
ERROR_CODE_DAQ = 11
ERROR_CODE_POWER = 12
ERROR_CODE_TEENSY = 13
ERROR_CODE_BOARD = 14
ERROR_CODE_COILS = 20

OK_CODE_MESSAGE = 'OK'
ERROR_MESSAGE_DAQ = '(USB-B) DAQ is not connected'
ERROR_MESSAGE_POWER = 'Power is OFF'
ERROR_MESSAGE_TEENSY = '(USB-B) MCU is not connected'
ERROR_MESSAGE_BOARD = 'Field Generator is not connected to Base Station'
ERROR_MESSAGE_COILS = 'Coil Failure'

POWER_THRESHOLD = -60
BOARD_THRESHOLD = -20

OFF = 0
FAULT = 1
ON = 2


class SystemStatusNotification:
    '''
    Bundles EMT coil and system activity into a single notification.
    '''
    def __init__(self, status=OFF, coils=[OFF] * 8, code=0, message=''):
        self.code = code
        self.message = message
        self.status = status
        self.coils = coils


class Monitor:
    '''
    Monitors the EMT system by performing tests every 1.5 seconds.
    Deduces whether system is on/off, field generator and MCU are connected and which coils are active.
    This is primarily done by performing a fast fourier transform on the samples acquired from the data acquisition device.
    '''
    def __init__(self, anser):
        super(Monitor, self).__init__()
        self.anser = anser
        self.system_connected = False
        self.daq_connected = False
        self.power_on = False
        self.board_connected = False
        self.teensy_connected = False
        self.systemNotifications = Subject()
        self.systemStatus = Subject()
        self.scheduler = NewThreadScheduler()

    def run_system_test(self, samples):
        system_status, coil_status, code, message = self.system_test(samples)
        self.systemNotifications.on_next(SystemStatusNotification(system_status, coil_status, code, message))

    def system_test(self, samples):
        system_status = OFF
        coil_status = [OFF]*8
        if self.is_daq_connected() is False:
            return system_status, coil_status, ERROR_CODE_DAQ, ERROR_MESSAGE_DAQ
        magnitudes = utils.convert_samples_to_fft_dbs(samples, 0)
        if self.is_power_on(magnitudes) is False:
            system_status = FAULT
            return system_status, coil_status, ERROR_CODE_POWER, ERROR_MESSAGE_POWER

        if self.is_board_connected(magnitudes) is False:
            system_status = FAULT
            return system_status, coil_status, ERROR_CODE_BOARD, ERROR_MESSAGE_BOARD

        coil_status = self.get_coil_status(magnitudes)
        if FAULT in coil_status:
            system_status = FAULT
            return system_status, coil_status, ERROR_CODE_COILS, ERROR_MESSAGE_COILS

        #TODO: Future Development: Frequency Changer
        #if self.is_teensy_connected() is False:
        #    return system_status, coil_status, ERROR_CODE_TEENSY, ERROR_MESSAGE_TEENSY

        system_status = ON
        return system_status, coil_status, OK_CODE, OK_CODE_MESSAGE

    def is_daq_connected(self):
        if self.anser is None:
            return False
        return True

    def is_power_on(self, magnitudes):
        if np.max(magnitudes) >= POWER_THRESHOLD:
            return True
        return False

    def is_board_connected(self, magnitudes):
        if np.max(magnitudes) >= BOARD_THRESHOLD:
            return True
        return False
    @staticmethod
    def is_teensy_connected():
        ports = list(serial.tools.list_ports.comports())
        response = 1
        command = 'ALIVE'
        try:
            for p in ports:
                port = serial.Serial(p.device)
                port.write(command.encode())
                time.sleep(.5)
                if port.in_waiting:
                    response = port.read()
                    response = int.from_bytes(response, byteorder=sys.byteorder)
                if response == OK_CODE_TEENSY:
                    return True
        except Exception as e:
            print(str(e))
        return False

    def get_coil_status(self, magnitudes):
        coil_status = [ON]*8
        fs = self.anser.filter.sampleFreq
        block_size = self.anser.filter.numSamples
        flattened_sorted = sorted(magnitudes)
        top_8_frequencies = []
        for i in range(1, 9):
            top_8_frequencies.append(flattened_sorted[i * -1])

        for index, frequency in enumerate(self.anser.filter.transFreqs):
            if magnitudes[int(round(frequency / (fs / block_size)))] not in top_8_frequencies:
                coil_status[index] = FAULT
        return coil_status
