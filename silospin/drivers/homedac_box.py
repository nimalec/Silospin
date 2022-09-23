import pyvisa
from pyvisa.constants import StopBits, Parity
import numpy as np
import time
import serial

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
        self._dac.write("VERBOSE\s"+str(verbose))

    def set_channel(self, channel):
        self._dac.write("CH\s"+str(channel))

    def set_channel_and_voltage(self, channel, voltage):
        self._dac.write("CH\s"+str(channel))
        self._dac.write("VOLT\s"+"{:.6f}".format(voltage))

    def set_voltage(self, voltage):
        self._dac.write("VOLT\s"+"{:.6f}".format(voltage))

class DacDriverSerial:
    def __init__(self, dev_id = 'COM3', verbose=0, init=True, termination_char = '\n', baud_rate=250000):
        self._dev_id = dev_id
        self._dac = serial.Serial(self._dev_id, baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)
        time.sleep(1)
        cmd_1 = '*IDN?\n'
        self._dac.write(cmd_1.encode('utf-8'))
        time.sleep(1)
        outputstring_1 = ''
        outputstring_1 = self._dac.readline().decode('utf-8').strip()
        print(outputstring_1)
        cmd_2 = 'VERBOSE\s'+str(int(verbose))+'\n'
        self._dac.write(cmd_2.encode('utf-8'))
        time.sleep(1)
        cmd_3 = 'INIT\n'

        if init == True:
            self._dac.write(cmd_3.encode('utf-8'))
            time.sleep(1)
        else:
            pass

    def set_voltage(self, voltage):
        self._dac.write(str('VOLT\'+''{:.6f}'.format(voltage)+'\n'))

    # def set_channel(self, channel):
    #     self._dac.write(str("CH\s"+str(int(channel))).encode('utf_8')+'\r\n')
