import numpy as np

def read_data_update_plot(data, timestamp0, daq_module, clockbase,signal_paths):
    data_read = daq_module.read(True)
    returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
    progress = daq_module.progress()[0]
    for signal_path in signal_paths:
        if signal_path.lower() in returned_signal_paths:
            for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                if np.any(np.isnan(timestamp0)):
                    timestamp0 = signal_burst["timestamp"][0, 0]
                t = (signal_burst["timestamp"][0, :] - timestamp0) / clockbase
                value = signal_burst["value"][0, :]
                num_samples = len(signal_burst["value"][0, :])
                dt = (signal_burst["timestamp"][0, -1]- signal_burst["timestamp"][0, 0]) / clockbase
                data[signal_path].append(signal_burst)
        else:
                pass

        return data, timestamp0
