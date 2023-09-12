import logging
import time

# for logging data:
# import the sys library
import sys
# import the os library
import os

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig

# for showing live data:
from IPython import display
from matplotlib import pyplot as plt

URI = uri_helper.uri_from_env(default='radio://0/80/2M/FDE7E7E701')
DEAFULT_HEIGHT = 1.0

SHOW_DATA_LIVE = True

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class gateIMAV:
     
    def __init__(self, crazyflie,logconf):
        self._cf = crazyflie
        self._data = {}
        self._logconfig = logconf

        # Get the files in the current directory:
        files = os.listdir('.')
        # Find how many data files there are currently:
        data_files = [f for f in files if f.startswith('data')]
        n_data_files = len(data_files)

        # open a file for writing the data:
        self._pylogfile = open(f'data_{n_data_files+1}.txt', 'w')


    def _log_cb(self, timestamp, data, logconf):
        for key, value in data.items():
            self._data[key] = value
        self.time = timestamp/1000

    def log_data(self):
        # get the time in ms from the time package:
        sys_time = time.time()

        # write the data to the file:
        self._pylogfile.write(f'{sys_time}, {self.time}, {self._data["stateEstimate.x"]}, {self._data["stateEstimate.y"]}, {self._data["stateEstimate.z"]}, {self._data["jevois.errorx"]}, {self._data["jevois.errory"]}, {self._data["jevois.width"]}, {self._data["jevois.height"]}\n')

    def takeoff(self):
        time_passed = 0.0
        while time_passed < 5:
            # we now send the taking off position (x,y,z,yaw)
            # self._cf.commander.send_position_setpoint(0.0, 0.0, DEAFULT_HEIGHT, 0.0)
            self._cf.commander.send_zdistance_setpoint(0.0, 0.0, 0.0, DEAFULT_HEIGHT)
            self.log_data()
            time.sleep(0.05)
            time_passed += 0.05


    def fly_through_gate(self, time_limit):
        print('Window detection')

        yaw_rate = 0.0
        z_distance = DEAFULT_HEIGHT

        width = self._data['jevois.width']
        height = self._data['jevois.height']

        if(SHOW_DATA_LIVE):
            times = []
            error_ys = []
            error_xs = []
            widths = []
            heights = []

        time_passed = 0.0
        while time_passed < time_limit and max(width, height) < 180:
            # get z and jevois errors
            z = self._data['stateEstimate.z']
            error_x = self._data['jevois.errorx']
            error_y = self._data['jevois.errory']
            width = self._data['jevois.width']
            height = self._data['jevois.height']

            if(SHOW_DATA_LIVE):
                # add the data to the lists for live plotting
                times.append(self.time)
                error_ys.append(error_y)
                error_xs.append(error_x)
                widths.append(width)
                heights.append(height)

            # log the data for post-analysis
            self.log_data()

            # Computing yawrate and zdistance for the commander (filtered)
            alpha_yaw = 0.8
            # error_y_gain = 0.5
            error_y_gain = 3
            alpha_z = 0.8
            error_x_gain = 0.001

            yaw_rate = alpha_yaw * yaw_rate - (1 - alpha_yaw) * error_y_gain * error_y + 8
            z_distance = alpha_z * z_distance + (1 - alpha_z) * (error_x_gain * error_x + z)

            if z_distance > 1.5:
                z_distance = 1.5

            # print(f'error_y = {error_y}, error_y_gain = {error_y_gain}, alpha_yaw*yaw_rate={alpha_yaw*yaw_rate}, error_y_gain*error_y={error_y_gain*error_y}, yaw_rate={yaw_rate}')
            print(f'errorx = {error_x}, errory = {error_y}, width = {width}, height = {height}')

            # Commanding roll, pitch, yaw rate and z position
            self._cf.commander.send_zdistance_setpoint(0.0, -5.0, yaw_rate, z_distance)
            # self._cf.commander.send_setpoint(30.0, 0.0, 0.0, 40000)
            # self._cf.commander.send_position_setpoint(0.0, 30.0, DEAFULT_HEIGHT, 0.0)

            if(SHOW_DATA_LIVE):
                if(self.figure_handle == []):
                    self.figure_handle = plt.figure('Live data')
                    self.ax = self.figure_handle.add_subplot(111)
                    plt.ion()
                    #self.figure_handle.show()
                    self.figure_handle.canvas.draw()
                else:
                    plt.figure('Live data')
                
                self.ax.clear()
                self.ax.plot(times, error_xs, label='error_x')
                self.ax.plot(times, error_ys, label='error_y')
                self.ax.plot(times, widths, label='width')
                self.ax.plot(times, heights, label='height')
                self.ax.legend()
                #        self.figure_handle.canvas.draw()
                #        self.figure_handle.show()
                display.clear_output(wait=True)
                display.display(plt.gcf())

            time.sleep(0.05)
            time_passed += 0.05

        print('Window passed')


    def fly_forward(self, time_limit):
        z = self._data['stateEstimate.z']
        time_passed = 0.0
        while time_passed < time_limit:
            # Commanding roll, pitch, yaw rate and z position
            self._cf.commander.send_zdistance_setpoint(0.0, -10, 0.0, z)
            # log the data:
            self.log_data()

            time.sleep(0.05)
            time_passed += 0.05

    
    def landing(self):
        time_passed = 0.0
        while time_passed < 10 and self._data['stateEstimate.z'] > 0.1:
            x = self._data['stateEstimate.x']
            y = self._data['stateEstimate.y']
            # self._cf.commander.send_position_setpoint(x, y, 0.0, 0.0)
            self._cf.commander.send_zdistance_setpoint(0.0, 0.0, 0.0, 0.0)
            self.log_data()
            time.sleep(0.05)
            time_passed += 0.05

        print('Landed')
        self._pylogfile.close()
        self._logconfig.stop()


    def fly(self):
        # First we define the logging configuration as the input
        self._cf.log.add_config(self._logconfig)
        # Then we add a callback to log the data into the class variables every time
        self._logconfig.data_received_cb.add_callback(self._log_cb)
        # Then we start the logging
        self._logconfig.start()

        try:
            self.takeoff()
            self.fly_through_gate(time_limit=60)
            self.fly_forward(time_limit=5)
            print('Landing')
            self.landing()

        except KeyboardInterrupt:
            print('\nEmergency landing')
            self.landing()


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    # logging configuration (x,y,z and errors)
    lg_stab = LogConfig(name='', period_in_ms=10)
    lg_stab.add_variable('stateEstimate.x', 'float')
    lg_stab.add_variable('stateEstimate.y', 'float')
    lg_stab.add_variable('stateEstimate.z', 'float')
    # lg_stab.add_variable('stateEstimate.pitch', 'float')
    # lg_stab.add_variable('stateEstimate.roll', 'float')
    # lg_stab.add_variable('stateEstimate.yaw', 'float')
    lg_stab.add_variable('jevois.errorx', 'int16_t')
    lg_stab.add_variable('jevois.errory', 'int16_t')
    lg_stab.add_variable('jevois.width', 'int16_t')
    lg_stab.add_variable('jevois.height', 'int16_t')
    # lg_stab.add_variable('motion.deltaX', 'float')
    # lg_stab.add_variable('motion.deltaY', 'float')
    
    cf=Crazyflie(rw_cache="./cache")
    # Open link for connection
    cf.open_link(URI)
    
    timeout = 10
    while not cf.is_connected() and timeout > 0:
        print("Waiting for Crazyflie connection...")
        time.sleep(2)
        timeout -= 1
    
    if cf.is_connected():
        print("Connected")
        flight = gateIMAV(cf,lg_stab)
        flight.fly()
        