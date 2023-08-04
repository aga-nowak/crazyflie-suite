import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def simple_log(scf, logconf):

    with SyncLogger(scf, lg_stab) as logger:

        for log_entry in logger:

            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]

            print('[%d][%s]: %s' % (timestamp, logconf_name, data))

            break

def simple_connect():

    print("yeah")
    time.sleep(3)
    print("disconnecting")

if __name__ == '__main__':

    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='motor', period_in_ms=10)
    lg_stab.add_variable('motor.m1', 'float')
    lg_stab.add_variable('motor.m2', 'float')
    lg_stab.add_variable('motor.m3', 'float')
    lg_stab.add_variable('motor.m4', 'float')

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        simple_log(scf, lg_stab)



