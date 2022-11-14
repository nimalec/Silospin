import zerorpc
from silospin.drivers.homedac_box import DacDriverSerial

class DacServer(object):
    device_id='COM3'
    dac_driver = DacDriverSerial(dev_id = device_id, verbose=0, init=False,  baud_rate=250000)

    def close(self):
        self.dac_driver._dac.close()

    def open_connection(self):
        self.dac_driver._dac.open()

    def channel_set(self, channel):
        self.dac_driver.set_channel(channel)

    def voltage_set(self, voltage):
        self.dac_driver.set_voltage(voltage)

    def channel_voltage_set(self, channel, value):
        self.dac_driver.set_channel(channel)
        self.dac_driver.set_voltage(value)

​server = zerorpc.Server(DacServer())
s.bind("tcp://0.0.0.0:4243")
s.run()
