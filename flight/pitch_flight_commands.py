import time


def takeoff(cf, z_distance=1.0):
    print('Takeoff')

    time_passed = 0.0
    while time_passed < 5:
        if cf.args["optitrack"] == "state":
            cf._cf.extpos.send_extpos(
                cf.filtered_pos[0], cf.filtered_pos[1], cf.filtered_pos[2]
            )
        cf.commander.send_zdistance_setpoint(0.0, 0.0, 0.0, z_distance)  # (roll, pitch, yaw rate, z distance)
        time.sleep(0.05)
        time_passed += 0.05


def fly_forward(cf, pitch=-10.0, z_distance=1.0, time_limit=5):
    print('Fly forward')

    time_passed = 0.0
    while time_passed < time_limit:
        if cf.args["optitrack"] == "state":
            cf._cf.extpos.send_extpos(
                cf.filtered_pos[0], cf.filtered_pos[1], cf.filtered_pos[2]
            )
        cf._cf.commander.send_zdistance_setpoint(0.0, pitch, 0.0, z_distance)  # (roll, pitch, yaw rate, z distance)
        time.sleep(0.05)
        time_passed += 0.05


def landing(cf):
    print('Landing')

    if cf.args["optitrack"] == "state":
        while cf.filtered_pos[2] > 0.1:
            cf._cf.extpos.send_extpos(
                cf.filtered_pos[0], cf.filtered_pos[1], cf.filtered_pos[2]
            )
            cf._cf.commander.send_zdistance_setpoint(0.0, 0.0, 0.0, 0.0)
            time.sleep(0.05)
    else:
        time_passed = 0.0
        while time_passed < 5:
            cf._cf.commander.send_zdistance_setpoint(0.0, 0.0, 0.0, 0.0)
            time.sleep(0.05)
            time_passed += 0.05

    print('Landed')
