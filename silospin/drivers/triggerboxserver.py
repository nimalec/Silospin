import zerorpc
from silospin.drivers.trig_box import TrigBoxSerial

class TriggerBoxServer(object):
    device_id='COM17'
    triggerbox_driver = TrigBoxSerial(dev_id = device_id,  baud_rate=250000)

    def close(self):
        self.triggerbox_driver._trigbox.close()

    def open_connection(self):
        self.triggerbox_driver._trigbox.open()

    def send_trigger(self):
        self.triggerbox_driver.send_trigger()

    def send_burst(self):
        self.triggerbox_driver.send_burst()

    def set_holdoff(self, holdoff):
        self.triggerbox_driver.set_holdoff(holdoff)

    def set_tlength(self, tlength):
        self.triggerbox_driver.set_tlength(tlength)

    def set_nburst(self, nburst):
        self.triggerbox_driver.set_nburst(nburst)

server = zerorpc.Server(TriggerBoxServer())
server.bind("tcp://0.0.0.0:4244")
server.run()
