""" Class definition for Anser EMT system"""

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
import math


class EMTracker:
    """
    Class definition for Anser EMT system
    """
    def __init__(self, sensors, config):

        # Define system magnetic model and solver with specific loaded configuration
        self.model = MagneticModel(config['model'])
        self.solver = Solver(None, self.model, config['solver'])

        # Derive what channels should be active
        self.active_channels = []
        self.sensors = sensors
        for sensor in self.sensors:
            self.active_channels.extend(sensor.channel)
            self.active_channels = sorted(self.active_channels)
        config['system']['channels'] = self.active_channels

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
            position, positionmat = self.get_position(sensor, sensor.name) if sensor.dof == 5 \
                else self.get_position_6dof(sensor,sensor.name)
            if self.print_option is True:
                self.print_position(position)
            positions.append(position)
        self.positionNotifications.on_next(positions)

    def reset_solver(self):
        for channel in self.prevPositions.keys():
            self.prevPositions[channel] = [0, 0, 0.2, 0, 0]

    def get_position(self, sensor, igtname=''):
        """Wrapper to include igt connection"""
        channel = sensor.channel[0]
        # Set the solver to use the corresponding sensor calibration
        self.solver.calibration = np.array(sensor.calibration[channel])

        if channel in self.prevPositions.keys():
            self.solver.conditions = self.prevPositions[channel]
        else:
            # Default initial conditionf for the solver
            self.solver.conditions = [0, 0, 0.2, 0, 0]

        # Resolve the position of the sensor indicated by sensorNo
        # Convert the resolved position to a 4x4 homogeneous transformation matrix
        position = self._resolve_position(channel)
        positionmat = self.vec_2_mat_5dof(position)

        # Latest resolved position is saved as the initial condition for the next solver iteration
        self.prevPositions[channel] = position

        # Send the resolved position over the system's OpenIGTLink connection
        # Optional sensor orientation correction (Theta + Pi) is applied before transmission
        if self.igtconn is not None:
            igtposition = position.copy()
            if self.flipflags is None or channel not in self.flipflags:
                igtposition[3] = igtposition[3] + pi
            igtmat = self.vec_2_mat_5dof(igtposition)
            self._igt_send_transform(igtmat, igtname)

        # Return the sensor position in both vector and 4x4 homogeneous transformation matrix.
        return position, positionmat

    def get_position_6dof(self, sensor, igtname=''):
        positions = []

        for channel in sensor.channel:
            # Set the solver to use the corresponding sensor calibration
            self.solver.calibration = np.array(sensor.calibration[channel])
            if channel in self.prevPositions.keys():
                self.solver.conditions = self.prevPositions[channel]
            else:
                # Default initial conditionf for the solver
                self.solver.conditions = [0, 0, 0.2, 0, 0]

            # Resolve the position of the sensor indicated by sensorNo
            # Convert the resolved position to a 4x4 homogeneous transformation matrix
            position = self._resolve_position(channel)

            # Latest resolved position is saved as the initial condition for the next solver iteration
            self.prevPositions[channel] = position.copy()

            if self.flipflags is None or channel not in self.flipflags:
                position[3] = position[3] + pi
            positions.append(position)

        # TODO: fix 6dof calculation
        positionmat = self.combine_5dof_sensors(positions[0], positions[1])
        #print('midposition {}'.format(mid_position))

        # Send the resolved position over the system's OpenIGTLink connection
        # Optional sensor orientation correction (Theta + Pi) is applied before transmission
        if self.igtconn is not None:
            igtmat = positionmat
            self._igt_send_transform(igtmat, igtname)

        # Return the sensor position in both vector and 4x4 homogeneous transformation matrix.
        return positions[0], positionmat


    def combine_5dof_sensors(self, sensor1, sensor2):
        # Create upwards vector
        upwards_vector = np.array([0, 0, 1])
        upwards_vector = np.reshape(upwards_vector, (3, 1))
        # Create rotation matrix RTheta x RPhi for both Sensors
        r_matrix1 = self.vec_2_mat_5dof(sensor1)[:-1, :-1]
        r_matrix2 = self.vec_2_mat_5dof(sensor2)[:-1, :-1]

        # Step 1: Apply rotation matrix to upwards vector (matrix multiplication).
        v1 = r_matrix1 * upwards_vector
        v2 = r_matrix2 * upwards_vector

        v1 = np.squeeze(np.asarray(v1)) # Reshape Upwards vector
        v2 = np.squeeze(np.asarray(v2))

        # Step 2: Create a vector perpendicular to v1 and v3. (Cross product between vectors v1 and v2)
        v3 = np.cross(v1, v2)

        v3 = v3 * (self.safe_div(1, np.linalg.norm(v3))) # Adjust magnitude of v3 i.e V3 == 1

        # Step 3: Get vector between v1 and v2/
        vt = (v1 + v2) / (np.linalg.norm(v1 + v2))

        # Step 4: Get perpendicular axis
        vp = np.cross(vt, v3)

        # Get the mid point
        mid_point = ((sensor1 + sensor2) / 2)[:3]
        mid_point = np.multiply(np.array(mid_point), 1000)

        # Step 5: Populate rotation matrix ([v3][vp][vt][Position])
        #positions = np.multiply(np.array(sensor1)[:3], 1000)
        #mid_point = np.multiply(np.array(mid_point), 1000)
        mat = np.column_stack((v3, vp, vt, mid_point))
        mat = np.append(mat, np.array([[0, 0, 0, 1]]), axis=0)  # Apply padding to end of matrix

        return mat

    def safe_div(self, x, y):
        if y == 0:
            return 0
        return x / y

    # Resolve the position of the sensor specified by sensorNo. Should not be called directly. Use get_position instead
    def _resolve_position(self, sensorNo):

        magnitudes = self.filter.demodulateSignalRef(self.data, self.active_channels.index(sensorNo) + 1)

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
        theta = array[3]
        phi = array[4]
        psi = array[5]
        mat = np.matrix(
            [[np.cos(phi)*np.cos(theta), -np.cos(psi)*np.sin(theta) + np.sin(psi)*np.sin(phi)*np.cos(theta), np.sin(psi)*np.sin(theta) + np.cos(psi)*np.sin(phi)*np.cos(theta), array[0]*1000],
             [np.cos(phi)*np.sin(theta), np.cos(psi)*np.cos(theta) + np.sin(psi)*np.sin(phi)*np.sin(theta), -np.sin(psi)*np.cos(theta) + np.cos(psi)*np.sin(phi)*np.sin(theta), array[1]*1000],
             [-np.sin(theta), np.sin(psi)*np.cos(phi), np.cos(psi)*np.cos(phi), array[2]*1000],
              [0,0,0,1]])
        return mat

    # Calculates rotation matrix to euler angles.
    def rotationMatrixToEulerAngles(self, r):
        sy = math.sqrt(r[0, 0] * r[0, 0] + r[1, 0] * r[1, 0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(r[2, 1], r[2, 2])
            y = math.atan2(-r[2, 0], sy)
            z = math.atan2(r[1, 0], r[0, 0])
        else:
            x = math.atan2(-r[1, 2], r[1, 1])
            y = math.atan2(-r[2, 0], sy)
            z = 0

        return np.array([x, y, z])

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

