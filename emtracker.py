""" Class definition for Anser EMT system"""

from utils.settings import get_settings, get_calibration
from utils.utils import get_relative_filepath
from model.model import MagneticModel
from solver.solver import Solver
from acquisition.daq import DAQ
from filter.filter import Filter
from pyIGTLink.pyIGTLink import *
from pyIGTLink.tests import *
from model.constants import pi
from rx.subjects import Subject
from rx.concurrency import NewThreadScheduler
import platform

class EMTracker:
    """
    Class definition for Anser EMT system
    """
    def __init__(self, config):

        # Load the system calibration values from the calibration file.
        #self.cal_dict = get_calibration(get_relative_filepath('calibration.yaml'))
        #self.cal = np.array(self.cal_dict[1])

        # Define system magnetic model and solver with specific loaded configuration
        self.model = MagneticModel(config['model'])
        self.solver = Solver(None, self.model, config['solver'])

        self.channels = config['system']['channels']
        # Create a dictionary to store previous sensor positions
        self.prevPositions = dict()
        self.flipflags = config['system']['flip_list']

        # Define DAQ and Filter objects with their associated configuration
        self.daq = DAQ(config)
        self.filter = Filter(config)

        # Declare storage for sample data and field strengths
        self.data = np.matrix([])
        self.magnitudes = np.matrix([])

        # Create local OpenIGTLink server
        self.igtconn = None
        if config['system']['igt'] is True:
            self.igtconn = PyIGTLink(port=config['system']['igt_port'], localServer=config['system']['igt_local'])

        self.t = threading.Thread(target=self.run)
        self.t.daemon = True
        self.print_option = config['system']['print']
        self.sampleNotifications = Subject()
        self.positionNotifications = Subject()
        self.delay = config['system']['update_delay']
        self.sensors = []
        self.device_cal = config['system']['device_cal']
        self.alive = True
        self.subscriptions = []

    def start_acquisition(self):
        """Start the DAQ acquisition background process"""
        self.daq.daqStart()

    def stop_acquisition(self):
        """Stop the DAQ acquisition background process"""
        self.daq.daqStop()

    def sample_update(self):
        """Retrieve new samples from the buffer. Sample data for each channel is obtained and stored simultaneously.
        Due to driver limitations, it is important that this function be called as often as possible on Linux and Mac
        operation systems"""
        self.data = self.daq.getData()
        self.sampleNotifications.on_next(self.data)

    def update_sensor_positions(self, samples=None):
        positions = []
        for sensor in self.sensors:
            position, positionmat = self.get_position(sensor, sensor.name)
            if self.print_option is True:
                self.print_position(position)
            positions.append(position)
        self.positionNotifications.on_next(positions)

    def get_position(self, sensor, igtname=''):
        """Wrapper to include igt connection"""

        # Set the solver to use the corresponding sensor calibration
        self.solver.calibration = np.array(sensor.calibration[sensor.channel])

        if sensor.channel in self.prevPositions.keys():
            self.solver.conditions = self.prevPositions[sensor.channel]
        else:
            # Default initial conditionf for the solver
            self.solver.conditions = [0, 0, 0.2, 0, 0]

        # Resolve the position of the sensor indicated by sensorNo
        # Convert the resolved position to a 4x4 homogeneous transformation matrix
        position = self._resolve_position(sensor.channel)
        positionmat = self.vec_2_mat_5dof(position)

        # Latest resolved position is saved as the initial condition for the next solver iteration
        self.prevPositions[sensor.channel] = position

        # Send the resolved position over the system's OpenIGTLink connection
        # Optional sensor orientation correction (Theta + Pi) is applied before transmission
        if self.igtconn is not None:
            igtposition = position.copy()
            if self.flipflags is None or sensor.channel not in self.flipflags:
                igtposition[3] = igtposition[3] + pi
            igtmat = self.vec_2_mat_5dof(igtposition)
            self._igt_send_transform(igtmat, igtname)

        # Return the sensor position in both vector and 4x4 homogeneous transformation matrix.
        return position, positionmat

    # Resolve the position of the sensor specified by sensorNo. Should not be called directly. Use get_position instead
    def _resolve_position(self, sensorNo):

        magnitudes = self.filter.demodulateSignalRef(self.data, self.channels.index(sensorNo) + 1)

        f = np.array(magnitudes)
        result = self.solver.solveLeastSquares(magnitudes)

        # Wrap around angles to preserve constraints
        wrapresult = self._angle_wrap(result)

        self.solver.initialCond = wrapresult.x

        return np.array(wrapresult.x)

    # Send a transformation matrix mat using the system's OpenIGTLink connection
    def _igt_send_transform(self, mat, device_name=''):
        matmsg = TransformMessage(mat, device_name=device_name)
        self.igtconn.add_message_to_send_queue(matmsg)

    @staticmethod
    def print_position(position):
        print('%0.4f %0.4f %0.4f %0.4f %0.4f'
              % (position[0] * 1000, position[1] * 1000, position[2] * 1000, position[3], position[4]))

    @staticmethod
    def _angle_wrap(result):
        if result.x[4] > 2*pi:
            result.x[4] = result.x[4] - 2 * pi
        elif result.x[4] < -2*pi:
            result.x[4] = result.x[4] + 2 * pi
        return result

    @staticmethod
    def vec_2_mat_5dof(array):

        mat = np.matrix([[np.cos(array[4])*np.cos(array[3]), -np.sin(array[4]), np.cos(array[4])*np.sin(array[3]), array[0]*1000],
                                    [np.sin(array[4])*np.cos(array[3]), np.cos(array[4]), np.sin(array[4])*np.sin(array[3]), array[1]*1000],
                                    [-np.sin(array[3]), 0, np.cos(array[3]), array[2]*1000],
                                    [0, 0, 0, 1]])
        return mat

    @staticmethod
    def vec_2_mat_6dof(self, array=np.array(np.zeros([1,6]))):

        pass

    def create_igt_server(self, port, localhost):
        if self.igtconn is None:
            self.igtconn = PyIGTLink(port, localhost)
            return True
        return False

    def get_network_message(self):
        if self.igtconn is not None:
            if len(self.igtconn.message_in_queue) > 0:
                return self.igtconn.message_in_queue.popleft()

    def reset_server(self):
        if self.igtconn is not None:
            self.igtconn.close_server()
            self.igtconn = None
            return True
        return False

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def start(self):
        self.t.start()

    def run(self):
        if platform.system() == 'Darwin':
            update_pos_thread = NewThreadScheduler()
            self.subscriptions.append(self.sampleNotifications.sample(10, scheduler=update_pos_thread)
                                      .subscribe(on_next=self.update_sensor_positions))
            while self.alive:
                self.sample_update()
                time.sleep(self.delay)
        else:
            while self.alive:
                self.sample_update()
                self.update_sensor_positions()
                time.sleep(self.delay)

    def stop(self):
        self.alive = False
        list(map(lambda sub: sub.dispose(), self.subscriptions))

