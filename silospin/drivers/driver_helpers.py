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

def read_data(data, daq_module, signal_paths):
    data_read = daq_module.read(True)
    returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
    progress = daq_module.progress()[0]
    for signal_path in signal_paths:
        if signal_path.lower() in returned_signal_paths:
            for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                value = signal_burst["value"][0, :]
                num_samples = len(signal_burst["value"][0, :])
                data[signal_path].append(signal_burst)
        else:
                pass
    return data

# def read_data_update_plot(data, daq_module, signal_paths):
#     data_read = daq_module.read(True)
#     returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
#     for signal_path in signal_paths:
#         if signal_path.lower() in returned_signal_paths:
#             for index, signal_burst in enumerate(data_read[signal_path.lower()]):
#                 data[signal_path].append(signal_burst)
#         else:
#                 pass
#         return data

def get_scope_records(device, daq, scopeModule, num_records=1):
    """
    Obtain scope records from the device using an instance of the Scope Module.
    """

    # Tell the module to be ready to acquire data; reset the module's progress to 0.0.
    scopeModule.execute()
    # Enable the scope: Now the scope is ready to record data upon receiving triggers.
    daq.setInt("/%s/scopes/0/enable" % device, 1)
    daq.sync()

    start = time.time()
    timeout = 30  # [s]
    records = 0
    progress = 0
    # Wait until the Scope Module has received and processed the desired number of records.
    while (records < num_records) or (progress < 1.0):
        time.sleep(0.5)
        records = scopeModule.getInt("records")
        progress = scopeModule.progress()[0]
        print(
            f"Scope module has acquired {records} records (requested {num_records}). "
            f"Progress of current segment {100.0 * progress}%.",
            end="\r",
        )

        if (time.time() - start) > timeout:
            # Break out of the loop if for some reason we're no longer receiving scope data from the
            # device.
            print(
                f"\nScope Module did not return {num_records} records after {timeout} s - \
                    forcing stop."
            )
            break
    print("")
    daq.setInt("/%s/scopes/0/enable" % device, 0)

    data = scopeModule.read(True)
    scopeModule.finish()
    return data

def check_scope_record_flags(scope_records):
    num_records = len(scope_records)
    for index, record in enumerate(scope_records):
        if record[0]["flags"] & 1:
            print(
                f"Warning: Scope record {index}/{num_records} flag indicates dataloss."
            )
        if record[0]["flags"] & 2:
            print(
                f"Warning: Scope record {index}/{num_records} indicates missed trigger."
            )
        if record[0]["flags"] & 4:
            print(
                f"Warning: Scope record {index}/{num_records} indicates transfer failure \
                    (corrupt data)."
            )
        totalsamples = record[0]["totalsamples"]
        for wave in record[0]["wave"]:
            # Check that the wave in each scope channel contains the expected number of samples.
            assert (
                len(wave) == totalsamples
            ), f"Scope record {index}/{num_records} size does not match totalsamples."
