class Sensor:
    def __init__(self, sensor_settings):
        self.name = sensor_settings['name']
        self.description = sensor_settings['description']
        self.channel = sensor_settings['channel']
        self.calibration = sensor_settings['calibration']
        self.dof = sensor_settings['dof']
        self.ports = []