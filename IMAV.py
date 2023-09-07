import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper

from cflib.crazyflie.log import LogConfig

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class gateIMAV:
     
    def __init__(self, crazyflie,logconf):
        """ initialize the class variables """
        self._cf = crazyflie
        # dictionary to hold data from callbacks
        self._data = {}
        self._logconfig = logconf


    def _log_cb(self, timestamp, data, logconf):
        """ Logging function. Logs into class variables """
        for key, value in data.items():
            self._data[key] = value
        self.time = timestamp/1000

    def fly(self):
        """ Main function """

        # First we define the logging configuration as the input
        self._cf.log.add_config(self._logconfig)
        # Then we add a callback to log the data into the class variables every time
        self._logconfig.data_received_cb.add_callback(self._log_cb)
        # Then we start the logging
        self._logconfig.start()

        # Main function for the movement
        try:
            # we define a time to take off. This can be changed
            wait = 5
            # We initialize a counter for the time
            time_passed = 0.0
            while time_passed < wait:
                # we now send the taking off position (x,y,z,yaw)
                cf.commander.send_position_setpoint(0.0, 0.0, 1.0, 0.0)
                time.sleep(0.05)
                time_passed += 0.05
            # define first yawrate and z, and also initial time and the counter for when to print data on screen
            t0=self.time
            printtime = 0.0
            yawrateold = 0
            zdold = 1
            x = 0
            # Control with jevois (until certain x distance)
            print('window detection')
            while x < 4:
                # get x, z and jevois error
                x = self._data['stateEstimate.x']
                z = self._data['stateEstimate.z']
                errorx = self._data['jevois.errorx']
                errory = self._data['jevois.errory']
                # printing errors to debug
                if (self.time-t0) > printtime:
                    print(errorx,errory)
                    printtime += 1
                # Computing yawrate and zdistance for the commander (filtered)
                yawrate = 0.8*yawrateold + 0.2*0.05*errory
                zdistance = 0.8*zdold + 0.2*(0.05*errorx + z)
                # Commanding roll, pitch, yaw rate and z position
                cf.commander.send_zdistance_setpoint(0.0, -5.0, yawrate, zdistance)
                # Keeping the last values to filtering
                yawrateold = yawrate
                zdold = zdistance
            print('window passed')
            while x < 8:
                # Command position, final of the lane (x=8.5,y=0,z=1, yaw=0)
                cf.commander.send_position_setpoint(8.5, 0.0, 1.0, 0.0)
            print('landing')
            # Time for landing and time counter
            wait = 5
            time_passed = 0.0
            while time_passed < wait:
                # Reading x and y to land in the same position
                x = self._data['stateEstimate.x']
                y = self._data['stateEstimate.y']
                # Landing command (x,y,z=0,yaw=0)
                cf.commander.send_position_setpoint(x, y, 0.0, 0.0)
                time.sleep(0.05)
                time_passed += 0.05
            print('landed')
            # stopping the logging
            self._logconfig.stop()
        except KeyboardInterrupt:
            print('emergency landing')
            #same as normal landing
            wait = 10
            time_passed = 0.0
            while time_passed < wait:
                x = self._data['stateEstimate.x']
                y = self._data['stateEstimate.y']
                cf.commander.send_position_setpoint(x, y, 0.0, 0.0)
                time.sleep(0.05)
                time_passed += 0.05
            print('landed')
            self._logconfig.stop()





    def simple_connect():

        print("yeah")
        time.sleep(3)
        print("disconnecting")



if __name__ == '__main__':
    # init drivers (from the tutorial)
    cflib.crtp.init_drivers()

    # logging configuration (x,y,z and errors)
    lg_stab = LogConfig(name='', period_in_ms=10)
    lg_stab.add_variable('stateEstimate.x', 'float')
    lg_stab.add_variable('stateEstimate.y', 'float')
    lg_stab.add_variable('stateEstimate.z', 'float')
    # lg_stab.add_variable('stateEstimate.pitch', 'float')
    # lg_stab.add_variable('stateEstimate.roll', 'float')
    # lg_stab.add_variable('stateEstimate.yaw', 'float')
    lg_stab.add_variable('jevois.errorx', 'uint32_t')
    lg_stab.add_variable('jevois.errory', 'uint32_t')
    # lg_stab.add_variable('motion.deltaX', 'float')
    # lg_stab.add_variable('motion.deltaY', 'float')
    
    # Defining the crazyflie class
    cf=Crazyflie(rw_cache="./cache")
    # Open link for connection
    cf.open_link(uri)
    # Time counter and integer for connection
    timeout = 10
    end = 0
    # While for connection timeout
    while not cf.is_connected() and end<1:
        print("Waiting for Crazyflie connection...")
        time.sleep(2)
        timeout -= 1
        if timeout<=0:
            end = 1
    # Running the code only if connected
    if end < 1:
        print("connected")
        #defining the class and calling the function
        flight = gateIMAV(cf,lg_stab)
        flight.fly()
        



