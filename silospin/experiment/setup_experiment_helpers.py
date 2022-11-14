from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.homedac_box import DacDriverSerial
import pickle
import datetime

def initialize_drivers(awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0: 'dev5759', 1: 'dev5761'}):
    global awg_driver_1
    global awg_driver_2
    global mfli_driver_1
    global mfli_driver_2
    global mfli_driver_3
    awg_driver_1 = HdawgDriver(awgs[0])
    awg_driver_2 = HdawgDriver(awgs[1])
    mfli_driver_1 = MfliDriver(lockins[0])
    mfli_driver_2 = MfliDriver(lockins[1])

def pickle_qubit_parameters(parameters_dict, parameters_file_path):
    qubit_parameters = {"timestamp": str(datetime.datetime.now()), "parameters": parameters_dict}
    with open(parameters_file_path, 'wb') as handle:
        pickle.dump(qubit_parameters, handle, protocol = pickle.HIGHEST_PROTOCOL)

def unpickle_qubit_parameters(parameters_file_path):
    with open(parameters_file_path, 'rb') as handle:
        qubit_parameters = pickle.load(handle)
    return qubit_parameters

def pickle_waveforms(waveforms_dict, waveforms_file_path):
    waveforms_parameters = {"timestamp": str(datetime.datetime.now()), "waveforms": waveforms_dict}
    with open(waveforms_file_path, 'wb') as handle:
        pickle.dump(waveforms_parameters, handle, protocol = pickle.HIGHEST_PROTOCOL)

def pickle_instrument_parameters(awg1_params, awg2_params, mfli1_params, mfli2_params, instruments_file_path):
    instrument_parameters = {"timestamp": str(datetime.datetime.now()), "awg1": awg1_params, "awg2": awg2_params, "mfli1": mfli1_params, "mfli2": mfli2_params}
    with open(instruments_file_path, 'wb') as handle:
        pickle.dump(instrument_parameters, handle, protocol = pickle.HIGHEST_PROTOCOL)

def pickle_dac_parameters(channel_mapping, instruments_file_path, dev_id = "COM3"):
    instrument_parameters = {"timestamp": str(datetime.datetime.now()), "id": dev_id, "channel_mapping": channel_mapping}
    with open(instruments_file_path, 'wb') as handle:
        pickle.dump(instrument_parameters, handle, protocol = pickle.HIGHEST_PROTOCOL)
