# read a data file and show it:
import sys
from matplotlib import pyplot as plt
import numpy as np
import csv


def simulate_yaw_rate(filename):
    yaw_rates = []

    with open(filename, 'r') as f:
        yaw_rate = 0.0

        while True:
            line = f.readline()

            if not line:
                break

            line = line.strip().split(', ')
            
            # (f'{sys_time}, {self.time}, {self._data["stateEstimate.x"]}, {self._data["stateEstimate.y"]}, {self._data["stateEstimate.z"]}, {self._data["jevois.errorx"]}, {self._data["jevois.errory"]}, {self._data["jevois.width"]}, {self._data["jevois.height"]}\n')

            alpha_yaw = 0.8
            error_y_gain = 0.25

            error_y = float(line[6])

            yaw_rate = alpha_yaw * yaw_rate - (1 - alpha_yaw) * error_y_gain * error_y + 8

            yaw_rates.append(yaw_rate)

    with open('yaw_sim.csv', 'w') as y:
        wr = csv.writer(y)
        for yaw_rate in yaw_rates:
            wr.writerow([yaw_rate])


def read_data(filename):

    with open(filename, 'r') as f:
        data = f.read()
    
    data = data.split('\n')
    data = [d.split(',') for d in data]
    
    npdata = np.zeros((len(data), len(data[0])))
    for i in range(len(data)):
        if(data[i] != ['']):
            for j in range(len(data[i])):
                npdata[i,j] = float(data[i][j])

    npdata = npdata[:-1,:]

    return npdata

if __name__ == '__main__':
    if len(sys.argv) < 2:
        n_file = 7
    else:
        n_file = int(sys.argv[1])
    data = read_data(f'data_{n_file}.txt')

    # self._pylogfile.write(f'{sys_time}, {self.time}, {self._data["stateEstimate.x"]}, {self._data["stateEstimate.y"]}, {self._data["stateEstimate.z"]}, {self._data["jevois.errorx"]}, {self._data["jevois.errory"]}, {self._data["jevois.width"]}, {self._data["jevois.height"]}\n')
    sys_time = data[:,0]
    time = data[:,1]
    x = data[:,2]
    y = data[:,3]
    z = data[:,4]
    error_x = data[:,5]
    error_y = data[:,6]
    width = data[:,7]
    height = data[:,8]

    if len(data[0]) <= 9:
        simulate_yaw_rate(f'data_{n_file}.txt')

    # live plot:
    # figure_handle = plt.figure('Live data')
    # plt.ion()
    # for i in range(len(time)):
    #     plt.clf()
    #     plt.plot(time[:i], error_x[:i], label='error_x')
    #     plt.plot(time[:i], error_y[:i], label='error_y')
    #     plt.legend()
    #     plt.pause(0.01)
    #     plt.draw()


    plt.figure()
    plt.plot(time, x, label='x')
    plt.plot(time, y, label='y')
    plt.plot(time, z, label='z')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(time, error_x, label='error_x')
    plt.plot(time, error_y, label='error_y')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(time, width, label='width')
    plt.plot(time, height, label='height')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(time, sys_time, label='sys_time')
    plt.legend()
    plt.show()

    
