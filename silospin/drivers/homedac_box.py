import pyvisa
from pyvisa.constants import StopBits, Parity
import numpy as np
import time
import serial
import zerorpc

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
    ##Note: timing error with N still persists. Alternative is to catch a write timeout error and restart the Driver connection  (~every 600 connections)
    def __init__(self, dev_id = 'COM3', verbose=0, init=True, baud_rate=250000):
        self._dev_id = dev_id
        self._baud_rate = baud_rate
        self._dac = serial.Serial(self._dev_id, baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)
        time.sleep(1)
        cmd_1 = '*IDN?\n'
        self._dac.write(cmd_1.encode('utf-8'))
        time.sleep(1)
        outputstring_1 = ''
        outputstring_1 = self._dac.readline().decode('utf-8').strip()
        print(outputstring_1)
        cmd_2 = 'VERBOSE '+str(int(verbose))+'\n'
        self._dac.write(cmd_2.encode('utf-8'))
        time.sleep(1)
        cmd_3 = 'INIT\n'

        if init == True:
            self._dac.write(cmd_3.encode('utf-8'))
            time.sleep(1)
        else:
            pass

    def reconnect_device(self):
        self._dac.close()
        self._dac = serial.Serial(self._dev_id, baudrate=self._baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)

    def set_voltage(self, voltage):
        cmd = 'VOLT '+ str('{:.6f}'.format(voltage))+'\n'
        self._dac.write(cmd.encode('utf-8'))

    def set_channel(self, channel):
        cmd = 'CH '+str(int(channel))+'\n'
        self._dac.write(cmd.encode('utf-8'))

    def set_init(self):
        self._dac.write('INIT\n'.encode('utf-8'))

    def set_idn(self):
        cmd = '*IDN?\n'
        self._dac.write(cmd.encode('utf-8'))

    def set_verbose(self, verbose):
        cmd = 'VEROBSE '+str(int(verbose))+'\n'
        self._dac.write(cmd.encode('utf-8'))

    def direct_write(self, cmd):
        cmd = str(cmd)+'\n'
        print(cmd)
        self._dac.write(cmd.encode('utf-8'))

class DacDriverSerialServer:
    def __init__(self, client="tcp://127.0.0.1:4243"):
        self._client_address = client
        self._client = zerorpc.Client()
        self._client.connect(self._client_address)

    def close(self):
        self._client.close()

    def open_connection(self):
        self._client.open_connection()

    def set_voltage(self, voltage):
        #self._client.connect(self._client_address)
        self._client.set_voltage(voltage)

    def set_channel(self, channel):
        #self._client.connect(self._client_address)
        self._client.set_channel(channel)
