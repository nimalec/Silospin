import pyvisa
from pyvisa.constants import StopBits, Parity
import numpy as np
import time
import zerorpc

class MicrowaveSource:
    def __init__(self, dev_id, termination_char = '\r\n', baud_rate=9600):
        ##Resolve flush issue for DAC
        rm = pyvisa.ResourceManager()
        baud_rate = 250000
        self._dev_id = dev_id
        self._dac = rm.open_resource(self._dev_id, baud_rate=baud_rate, read_termination=termination_char, write_termination=termination_char, timeout=100000)
        time.sleep(1)
        self._dac.query("*IDN?")

    def clear_buffer(self):
        self._dac.write("*CLS")

    def set_frequency(self, frequency):
        self._dac.write("FREQ\s"+str(frequency))

    def set_power(self, power):
        self._dac.write("LEVEL\s"+str(power))
