def read_data_update_plot(data, timestamp0, daq_module, signal_paths):
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
                # if plot:
                #     axis.plot(t, value)
                num_samples = len(signal_burst["value"][0, :])
                dt = (signal_burst["timestamp"][0, -1]- signal_burst["timestamp"][0, 0]) / clockbase
                data[signal_path].append(signal_burst)
        else:
                pass

        # Update the plot.
        # if plot:
        #     axis.set_title(f"Progress of data acquisition: {100 * progress:.2f}%.")
        #     plt.pause(0.01)
        #     fig.canvas.draw()
        return data, timestamp0
