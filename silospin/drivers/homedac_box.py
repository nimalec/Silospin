import pyvisa
import numpy as np

class DacDriver:
    def __init__(self, dev_id = "ASRL3::INSTR"):
        rm = pyvisa.ResourceManager()
        self._dev_id = dev_id
        self._dac = rm.open_resource(self._dev_id)
        self._id_name = self._dac.query("*IDN?")
        n_channels = 25
        self._channel_configuration = {}
        for i in range(1,n_channels):
            if i < 10:
                self._dac.query("CH 0"+str(i))
            else:
                self._dac.query("CH "+str(i))

            voltage = self._dac.query("VOLT?")
            self._channel_configuration[i] = float(voltage[0:3])

    def set_voltage(self, channel, voltage):
        ##channel index should be between 1 and 24
        if channel < 10:
            self._dac.query("CH 0"+str(channel))
        else:
            self._dac.query("CH "+str(channel))
        self._dac.query("VOLT "+str(voltage))
        voltage_str = self._dac.query("VOLT?")
        self._channel_configuration[channel] = float(voltage_str[0:3])

    def get_voltage(self, channel):
        if channel < 10:
            self._dac.query("CH 0"+str(channel))
        else:
            self._dac.query("CH "+str(channel))
        voltage_str = self._dac.query("VOLT?")
        self._channel_configuration[channel] = float(voltage_str[0:3])
        return self._channel_configuration[channel]

    def Sweep1D(self, channel, start_v, end_v, npoints):
        if channel < 10:
            self._dac.query("CH 0"+str(channel))
        else:
            self._dac.query("CH "+str(channel))

        v_array = np.linspace(start_v,end_v,npoints)
        for v in v_array:
            self._dac.query("VOLT "+str(v))
            voltage_str = self._dac.query("VOLT?")
            self._channel_configuration[channel] = float(voltage_str[0:3])
        return v_array


    def Sweep2D(self, channel_1, channel_2, start_v_1, end_v_1, start_v_2, end_v_2, n_points_1, n_points_2):
        dVx = (end_v_1-start_v_1)/n_points_1
        dVy = (end_v_2-start_v_2)/n_points_2
        V_x, V_y = np.mgrid[start_v_1:end_v_1:dVx,start_v_2:end_v_2:dVy]
        (dim0, dim1) = np.shape(V_x)
        for i in range(dim0):
            for j in range(dim1):
                self.set_voltage(channel_1, V_x[i][j])
                self.set_voltage(channel_2, V_y[i][j])
        return (V_x, V_y)
