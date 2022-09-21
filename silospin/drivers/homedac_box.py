import pyvisa
from pyvisa.constants import StopBits, Parity
import numpy as np
import time

class DacDriver:
    def __init__(self, dev_id = "ASRL3::INSTR", verbose=0, init=True, termination_char = '\r\n', baud_rate=250000):
        ##Resolve flush issue for DAC
        rm = pyvisa.ResourceManager()
        baud_rate = 250000
        self._dev_id = dev_id
        self._dac = rm.open_resource(self._dev_id, baud_rate=baud_rate, read_termination=termination_char, write_termination=termination_char, timeout=100000)
        self._dac.write("VERBOSE\s"+str(verbose))
        if init == True:
            self._dac.write("INIT")
        else:
            pass
        time.sleep(1)
        self._dac.query("*IDN?")

    def clear_buffer(self):
        self._dac.write("*CLS")

    def set_verbose(self, verbose):
        self._dac.write("*CLS")
        self._dac.write("VERBOSE\s"+str(verbose))

    def set_channel(self, channel):
        self._dac.write("*CLS")
        self._dac.write("CH\s"+str(channel))

    def set_channel_and_voltage(self, channel, voltage):
        self._dac.write("*CLS")
        self._dac.write("CH\s"+str(channel))
        self._dac.write("VOLT\s"+"{:.9f}".format(voltage))

    def set_voltage(self, voltage):
        self._dac.write("*CLS")
        self._dac.write("VOLT\s"+"{:.9f}".format(voltage))

    # def Sweep1D(self, channel, start_v, end_v, npoints):
    #     #self._dac.query("CH "+str(channel))
    #     self._dac.write("CH "+str(channel))
    #     v_array = np.linspace(start_v,end_v,npoints)
    #     for v in v_array:
    #         #self._dac.query("VOLT "+str(v))
    #         self._dac.write("VOLT "+str(v))
    #         voltage_str = self._dac.query("VOLT?")
    #         self._channel_configuration[channel] = float(voltage_str[0:3])
    #     return v_array
    #
    #
    # def Sweep2D(self, channel_1, channel_2, start_v_1, end_v_1, start_v_2, end_v_2, n_points_1, n_points_2):
    #     vx = np.linspace(start_v_1, end_v_1, n_points_1)
    #     vy = np.linspace(start_v_2, end_v_2, n_points_2)
    #     V_x, V_y = np.meshgrid(vx, vy)
    #     (dim0, dim1) = np.shape(V_x)
    #     for i in range(dim0):
    #         for j in range(dim1):
    #             self.set_voltage(channel_1, V_x[i][j])
    #             self.set_voltage(channel_2, V_y[i][j])
    #     return (V_x, V_y)
