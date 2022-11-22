"""Homebuilt digital-to-analog converter (DAC) server.

Run this on the command line as:

>> python dacserver.py

Version from November 2022.
"""

import zerorpc
from silospin.drivers.homedac_box import DacDriverSerial

class DacServer(object):
    device_id='COM3'
    dac_driver = DacDriverSerial(dev_id = device_id, verbose=0, init=False,  baud_rate=250000)

    def close(self):
        self.dac_driver._dac.close()

    def open_connection(self):
        self.dac_driver._dac.open()

    def set_voltage(self, voltage):
        self.dac_driver.set_voltage(voltage)

    def set_channel(self, channel):
        self.dac_driver.set_channel(channel)

server = zerorpc.Server(DacServer())
server.bind("tcp://0.0.0.0:4243")
server.run()
