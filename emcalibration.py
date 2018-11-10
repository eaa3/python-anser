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
        self.scalers = None
        self.point_count = 0
        self.curr_point = 1
        self.sensor = sensor
        self.calibrators = []
        self.num_calibrators = 1 if int(self.sensor.dof) == 5 else 2
        self.config = config
        self.setup()

    def setup(self):
        try:
            self.anser = EMTracker([self.sensor], self.config)
            if platform.system() == 'Windows':
                self.anser.daq.setContSamps(True)
            else:
                self.anser.daq.setContSamps(False)

            # Need two calibrators for 6Dof, one for each channel.
            for i in range(self.num_calibrators):
                self.calibrators.append(Calibration(self.anser.device_cal, self.anser.model))
                self.calibrators[i].fieldData = np.zeros([self.calibrators[i].numCoils, self.calibrators[i].numPoints])
                self.point_count = self.calibrators[i].numPoints

            self.anser.start_acquisition()
        except Exception as e:
            raise

    def next(self):
        if self.curr_point != self.point_count + 1:
            self.anser.sample_update()
            samples = copy.deepcopy(self.anser.data)
            for index, calibrator in enumerate(self.calibrators):
                calibrator.fieldData[:, self.curr_point - 1] = np.column_stack(self.anser.filter.demodulateSignalRef(samples, index + 1))
                # TODO: Automatic Frequency Detection and Configuration
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
            self.curr_point += 1
        return self.curr_point

    def calibrate(self):
        if self.curr_point == self.point_count + 1:
            for index, calibrator in enumerate(self.calibrators):
                if self.sensor.dof == 5:
                    self.scalers = calibrator.run_calibration()
                else: # 6DOF
                    theta = self.config['calibration']['6DOF_theta']
                    phi = self.config['calibration']['6DOF_phi']

                    if index == 0:
                        print('\n Sensor 1: ')
                        print('theta: {} phi: {} \n'.format(theta[1], phi[1]))
                        #self.scalers = calibrator.run_calibration_6DOF(theta[1], phi[1])
                        self.scalers = calibrator.run_calibration()

                    else:
                        print('\n Sensor 2: ')
                        print('theta: {} phi: {} \n'.format(theta[2], phi[2]))
                        #self.scalers = calibrator.run_calibration_6DOF(theta[2], phi[2])
                        self.scalers = calibrator.run_calibration()
                self.sensor.calibration[self.sensor.channel[index]] = [float(i) for i in self.scalers]


            try:
                sensor_settings = utils.import_sensor_settings(self.sensor.name)
                sensor_settings['calibration'] = self.sensor.calibration
                utils.export_settings(sensor_settings, utils.find_sensor(self.sensor.name))
                print('Calibration Saved.\n')
                return True
            except Exception as e:
                print('Error Calibrating')
        return False

    def reset(self):
        self.anser.stop_acquisition()
        self.curr_point = 0
        self.anser = None
        self.scalers = None