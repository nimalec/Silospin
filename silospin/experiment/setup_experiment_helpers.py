import pickle
import datetime

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
