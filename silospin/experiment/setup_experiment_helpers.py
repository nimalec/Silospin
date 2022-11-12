from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.homedac_box import DacDriverSerial
import pickle

def initialize_drivers(awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0: 'dev5759', 1: 'dev5761'}):
    global awg_driver_1
    global mfli_driver_1
    global mfli_driver_2
    global mfli_driver_3
    awg_driver_1 = HdawgDriver(awgs[0])
    awg_driver_2 = HdawgDriver(awgs[1])
    mfli_driver_1 = MfliDriver(lockins[0])
    mfli_driver_2 = MfliDriver(lockins[1])

def pickle_qubit_parameters(parameters_dict, parameters_file_path):
    with open(parameters_file_path, 'wb') as handle:
        pickle.dump(parameters_dict, handle, protocol = pickle.HIGHEST_PROTOCOL)

def unpickle_qubit_parameters(parameters_file_path):
    with open(parameters_file_path, 'rb') as handle:
        qubit_parameters = pickle.load(handle)
    return qubit_parameters
