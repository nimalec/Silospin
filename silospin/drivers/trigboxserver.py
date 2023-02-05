"""Homebuilt digital-to-analog converter (DAC) server.

Run this on the command line as:

>> python dacserver.py

Version from November 2022.
"""
import zerorpc
from silospin.drivers.homedac_box import TrigBoxDriverSerial

class TrigBoxServer(object):
    device_id_1='COM17'
    trigbox_driver_1 = TrigBoxDriverSerial(dev_id = device_id_1, verbose=0, init=False,  baud_rate=250000)

    def close_1(self):
        self.trigbox_driver_1._trig_box.close()

    def open_connection(self):
        self.trigbox_driver_1._trig_box.open()

    def send_trigger(self):
        self.trigbox_driver_1.send_trigger()

server = zerorpc.Server(TrigBoxServer())
server.bind("tcp://0.0.0.0:4244")
server.run()
