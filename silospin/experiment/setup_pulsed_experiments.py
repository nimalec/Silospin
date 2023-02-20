from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.homedac_box import DacDriverSerial
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import channel_mapper, make_gate_parameters
import pickle
import datetime

def initialize_drivers(awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0: 'dev6541', 1: 'dev5761'}):
    global awg_driver_1
    global awg_driver_2
    global mfli_driver_1
    global mfli_driver_2

    channel_mapping, awg_mapping = channel_mapper({"hdawg1": {"rf":  [1,2,3,4], "dc": []}, "hdawg2":  {"rf": [1], "dc": [2,3,4]}}, trig_channels = {"hdawg1": 1, "hdawg2": 1})
    dev_name_1 = 'hdawg1'
    dev_name_2 = 'hdawg2'
    awg_driver_1 = HdawgDriver(awgs[0], dev_name_1, channel_mapping, awg_mapping)
    awg_driver_2 = HdawgDriver(awgs[1], dev_name_2, channel_mapping, awg_mapping)
    mfli_driver_1 = MfliDriver(lockins[1])
#    mfli_driver_2 = MfliDriver(lockins[1])
