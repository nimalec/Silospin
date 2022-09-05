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
        if channel < 10:
            self._dac.query("CH 0"+str(channel))
        else:
            self._dac.query("CH "+str(channel))
        self._dac.query("VOLT "+str(voltage))
        voltage_str = self._dac.query("VOLT?")
        self._channel_configuration[channel] = float(voltage_str[0:3])
        
    #def get_voltage(self, channel, voltage):
    #def get_voltage(self, channel, voltage):
