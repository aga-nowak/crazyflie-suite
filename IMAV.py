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
        """ Initialize and run the example with the specified link_uri """
        self._cf = crazyflie
        # dictionary to hold data from callbacks
        self._data = {}
        self._logconfig = logconf


    def _log_cb(self, timestamp, data, logconf):
        for key, value in data.items():
            self._data[key] = value
        self.time = timestamp/1000

    def fly(self):

    
        self._cf.log.add_config(self._logconfig)
        self._logconfig.data_received_cb.add_callback(self._log_cb)
        self._logconfig.start()

        try:
            wait = 5
            time_passed = 0.0
            while time_passed < wait:
                cf.commander.send_position_setpoint(0.0, 0.0, 1.0, 0.0,)
                time.sleep(0.05)
                time_passed += 0.05
            t0=self.time
            printtime = 0.0
            yawrateold = 0
            zdold = 1
            while True:
                z = self._data['stateEstimate.z']
                errorx = self._data['jevois.errorx']
                errory = self._data['jevois.errory']
                # print(self.time-t0)
                if (self.time-t0) > printtime:
                    print(errorx,errory)
                    printtime += 1
                yawrate = 0.8*yawrateold + 0.2*0.05*errory
                zdistance = 0.8*zdold + 0.2*(0.05*errorx + z)
                cf.commander.send_zdistance_setpoint(0.0, -5.0, yawrate, zdistance)
                yawrateold = yawrate
                zdold = zdistance
        except KeyboardInterrupt:
            print('landing')
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

    cflib.crtp.init_drivers()

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
    cf=Crazyflie(rw_cache="./cache")
    cf.open_link(uri)
    timeout = 10
    end = 0
    while not cf.is_connected() and end<1:
        print("Waiting for Crazyflie connection...")
        time.sleep(2)
        timeout -= 1
        if timeout<=0:
            end = 1
    print("endwhile")
    if end < 1:
        print("connected")
        flight = gateIMAV(cf,lg_stab)
        flight.fly()
        



