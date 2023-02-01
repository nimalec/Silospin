"""Homebuilt digital-to-analog converter (DAC) server.

Run this on the command line as:

>> python dacserver.py

Version from November 2022.
"""

import zerorpc
from silospin.drivers.homedac_box import DacDriverSerial

class DacServer(object):
    device_id_1='COM14'
    device_id_2='COM13'
    dac_driver_1 = DacDriverSerial(dev_id = device_id_1, verbose=0, init=False,  baud_rate=250000)
    dac_driver_2 = DacDriverSerial(dev_id = device_id_2, verbose=0, init=False,  baud_rate=250000)

    def close_1(self):
        self.dac_driver_1._dac.close()

    def open_connection_1(self):
        self.dac_driver_1._dac.open()

    def set_voltage_1(self, voltage):
        self.dac_driver_1.set_voltage(voltage)

    def set_channel_1(self, channel):
        self.dac_driver_1.set_channel(channel)

    def close_2(self):
        self.dac_driver_2._dac.close()

    def open_connection_2(self):
        self.dac_driver_2._dac.open()

    def set_voltage_2(self, voltage):
        self.dac_driver_2.set_voltage(voltage)

    def set_channel_2(self, channel):
        self.dac_driver_2.set_channel(channel)

server = zerorpc.Server(DacServer())
server.bind("tcp://0.0.0.0:4243")
server.run()
