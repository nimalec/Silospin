import pyvisa
from pyvisa.constants import StopBits, Parity
import numpy as np
import time
import serial
import zerorpc

class TrigBoxDriverSerial:
    def __init__(self, dev_id = 'COM17', baud_rate=250000):
        self._dev_id = dev_id
        self._baud_rate = baud_rate
        self._trig_box = serial.Serial(self._dev_id)
        time.sleep(1)
        cmd_1 = '*IDN?\n'
        self._trig_box.write(cmd_1.encode('utf-8'))
        time.sleep(1)
        outputstring_1 = ''
        outputstring_1 = self._trig_box.readline().decode('utf-8').strip()
        print(outputstring_1)

    def reconnect_device(self):
        self._trig_box.close()
        self._trig_box = serial.Serial(self._dev_id, baudrate=self._baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)

    def send_trigger(self):
        cmd = 'TRGA\n'
        self._trig_box.write(cmd.encode('utf-8'))

    def send_burst(self):
        cmd = 'BSTA\n'
        self._trig_box.write(cmd.encode('utf-8'))

    def set_holdoff(self, holdoff):
        ##holdoff in us
        cmd = f'HOLDOFF {int(holdoff)}\n'
        self._trig_box.write(cmd.encode('utf-8'))

    def set_tlength(self, tlength):
        ##trigger length in us
        cmd = f'TLENGTH {int(tlength)}\n'
        self._trig_box.write(cmd.encode('utf-8'))

    def set_nburst(self, nburst):
        ##nunber of bursts
        cmd = f'NBURST {int(nburst)}\n'
        self._trig_box.write(cmd.encode('utf-8'))


class TrigBoxDriverSerialServer:
    def __init__(self, client="tcp://127.0.0.1:4244"):
        self._client_address = client
        self._client = zerorpc.Client()
        self._client.connect(self._client_address)

    def close(self):
        self._client.close()

    def open_connection(self):
        self._client.open_connection()

    def send_trigger(self):
        self._client.send_trigger()

    def send_burst(self):
        self._client.send_burst()

    def set_holdoff(self, holdoff):
        self._client.set_holdoff(holdoff)

    def set_tlength(self, tlength):
        self._client.set_tlength(tlength)

    def set_nburst(self, nburst):
        self._client.set_nburst(tlength)
