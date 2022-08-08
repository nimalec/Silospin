from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli2 import MfliDriver

def init(awg_id="dev8446"):
    global awg_driver
    awg_driver = HdawgDriver(awg_id)
