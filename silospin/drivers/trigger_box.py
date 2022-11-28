import time
import serial
import zerorpc

class TriggerBoxSerial:
    ##Note: timing error with N still persists. Alternative is to catch a write timeout error and restart the Driver connection  (~every 600 connections)
    def __init__(self, dev_id = 'COM5', baud_rate=250000):
        self._dev_id = dev_id
        self._baud_rate = baud_rate
        self._trigbox = serial.Serial(self._dev_id, baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)
        time.sleep(1)
        cmd_1 = '*IDN?\n'
        self._trigbox.write(cmd_1.encode('utf-8'))
        time.sleep(1)
        outputstring_1 = ''
        outputstring_1 = self._trigbox.readline().decode('utf-8').strip()
        print(outputstring_1)

    def reconnect_device(self):
        self._trigbox.close()
        self._trigbox = serial.Serial(self._dev_id, baudrate=self._baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)

    def trigger(self):
        ##Start trigger
        cmd = 'TRIG\n'
        self._trigbox.write(cmd.encode('utf-8'))

    def set_burst_length(self, burst_length):
        ##Numbe of bursts
        cmd = 'BURST '+ str(int(burst_length))+'\n'
        self._trigbox.write(cmd.encode('utf-8'))

    def set_pulse_length(self, pulse_length):
        ##Pulse length in microseconds
        cmd = 'PLENGTH '+ str(int(pulse_length))+'\n'
        self._trigbox.write(cmd.encode('utf-8'))

    def set_holdoff(self, holdoff):
        ##Holdoff in microseconds between pulses
        cmd = 'HOLDOFF '+ str(int(holdoff))+'\n'
        self._trigbox.write(cmd.encode('utf-8'))

class TriggerBoxServer:
    ##May need to change client...
    def __init__(self, client="tcp://127.0.0.1:4243"):
        self._client_address = client
        self._client = zerorpc.Client()
        self._client.connect(self._client_address)

    def close(self):
        self._client.close()

    def open_connection(self):
        self._client.open_connection()

    def trigger(self):
        self._client.trigger()

    def set_burst_length(self, burst_length):
        self._client.set_burst_length(burst_length)

    def set_pulse_length(self, pulse_length):
        self._client.set_pulse_length(pulse_length)

    def set_holdoff(self, holdoff):
        self._client.set_holdoff(holdoff)
