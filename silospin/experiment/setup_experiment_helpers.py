from silospin.drivers.zi_hdawg_driver_v2 import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.homedac_box import DacDriverSerial
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import channel_mapper, make_gate_parameters
import pickle
import datetime

# def initialize_drivers(awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0: 'dev5759', 1: 'dev5761'}):
#     global awg_driver_1
#     global awg_driver_2
#     global mfli_driver_1
#     global mfli_driver_2
#
#     channel_mapping, awg_mapping = channel_mapper({"hdawg1": {"rf":  [1,2,3,4], "dc": []}, "hdawg2":  {"rf": [1], "dc": [2,3,4]}}, trig_channels = {"hdawg1": 1, "hdawg2": 1})
#     dev_name_1 = 'hdawg1'
#     dev_name_2 = 'hdawg2'
#     awg_driver_1 = HdawgDriver(awgs[0], dev_name_1, channel_mapping, awg_mapping)
#     awg_driver_2 = HdawgDriver(awgs[1], dev_name_2, channel_mapping, awg_mapping)
#     mfli_driver_1 = MfliDriver(lockins[0])
#     mfli_driver_2 = MfliDriver(lockins[1])

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

def pickle_charge_data(data, file_path):
    data_dict = {"timestamp": str(datetime.datetime.now()), "data": data}
    with open(file_path, 'wb') as handle:
        pickle.dump(data_dict, handle, protocol = pickle.HIGHEST_PROTOCOL)

def pickle_dac_parameters_v2(channel_mapping, voltage_divide, instruments_file_path, dev_id = "COM14", dac_name = "DAC1"):
    instrument_parameters = {"timestamp": str(datetime.datetime.now()), "dac_name": dac_name,  "id": dev_id, "channel_mapping": channel_mapping, "dividers": voltage_divide}
    with open(instruments_file_path, 'wb') as handle:
        pickle.dump(instrument_parameters, handle, protocol = pickle.HIGHEST_PROTOCOL)
