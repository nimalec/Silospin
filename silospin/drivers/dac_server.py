import zerorpc
from silospin.drivers.homedac_box import DacDriverSerial

class DacServer(object):
    device_id='COM3'
    dac_driver = DacDriverSerial(dev_id = device_id, verbose=0, init=False,  baud_rate=250000)

    def close(self):
        self.dac_driver._dac.close()

    def open_connection(self):
        self.dac_driver._dac.open()

    def set_channel(self, channel):
        self.dac_driver.set_channel(channel)

    def set_voltage(self, voltage):
        self.dac_driver.set_voltage(voltage)

    def set_channel_voltage(self, channel, value):
        self.dac_driver.set_channel(channel)
        self.dac_driver.set_voltage(value)

    def set_init(self):
        self.dac_driver.set_init()

    def set_verbose(self):
        self.dac_driver.set_init()

​server = zerorpc.Server(DacServer())
s.bind("tcp://0.0.0.0:4243")
s.run()
