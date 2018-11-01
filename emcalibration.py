from emtracker import EMTracker
from calibration.calibration import Calibration
import platform as platform
import numpy as np
import utils.utils as utils
import copy


class EMCalibration:
    def __init__(self, sensor, config):
        super(EMCalibration, self).__init__()
        self.anser = None
        self.cal = None
        self.scalers = None
        self.point_count = 0
        self.curr_point = 1
        self.sensor = sensor
        self.config = config
        self.setup()

    def setup(self):
        try:
            self.config['system']['channels'] = [self.sensor.channel]
            self.anser = EMTracker(self.config)
            if platform.system() == 'Windows':
                self.anser.daq.setContSamps(True)
            else:
                self.anser.daq.setContSamps(False)

            self.cal = Calibration(self.anser.device_cal, self.anser.model)
            self.cal.fieldData = np.zeros([self.cal.numCoils, self.cal.numPoints])
            self.point_count = self.cal.numPoints
            self.anser.start_acquisition()
        except Exception as e:
            print(str(e))

    def next(self):
        if self.curr_point != self.point_count + 1:
            self.anser.sample_update()
            samples = copy.deepcopy(self.anser.data)
            #TODO: Automatic Frequency Detection and Configuration
            '''
             desired_frequencies = self.anser.filter.transFreqs
             while not utils.are_frequencies_active(desired_frequencies, samples):
                utils.write_frequencies_to_teensy_from_list(self.anser.filter.transFreqs)
                time.sleep(.5)
                self.anser.sample_update()
                samples = copy.deepcopy(self.anser.data)

            self.anser.sample_update()
            samples = copy.deepcopy(self.anser.data)
            '''
            self.cal.fieldData[:, self.curr_point - 1] = np.column_stack(self.anser.filter.demodulateSignalRef(samples, 1))  # Data always in Col 1
            self.curr_point += 1
        return self.curr_point

    def calibrate(self):
        if self.curr_point == self.point_count + 1:
            result = self.cal.run_calibration()
            self.scalers = result
            print(str(self.scalers))
        print('Done\n')

        try:
            self.sensor.calibration[self.sensor.channel] = [float(i) for i in self.scalers]
            sensor_settings = utils.import_sensor_settings(self.sensor.name)
            sensor_settings['calibration'] = self.sensor.calibration
            utils.export_settings(sensor_settings, utils.find_sensor(self.sensor.name))
            print('Calibration Saved.\n')
        except Exception as e:
            print('Error Calibrating')
            return False
        return True

    def reset(self):
        self.anser.stop_acquisition()
        self.curr_point = 0
        self.anser = None
        self.scalers = None