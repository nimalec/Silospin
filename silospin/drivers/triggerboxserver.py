import zerorpc
from silospin.drivers.trigger_box import TriggerBoxSerial

class TriggerBoxServer(object):
    device_id='COM5'
    triggerbox_driver = TriggerBoxSerial(dev_id = device_id,  baud_rate=250000)

    def close(self):
        self.triggerbox_driver._trigbox.close()

    def open_connection(self):
        self.triggerbox_driver._trigbox.open()

    def trigger(self):
        self.triggerbox_driver.trigger()

    def set_burst_length(self, burst_length):
        self.triggerbox_driver.set_burst_length(burst_length)

    def set_pulse_length(self, pulse_length):
        self.triggerbox_driver.set_pulse_length(pulse_length)

    def set_holdoff(self, holdoff):
        self.triggerbox_driver.set_holdoff(holdoff)


server = zerorpc.Server(TriggerBoxServer())
server.bind("tcp://0.0.0.0:4243")
server.run()
