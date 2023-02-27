import time
import numpy as np
import matplotlib.pyplot as plt

def daq_measurement_settings(n_traces, daq_module, daq, dev_id, measurement_settings, sig_port):
    duration = measurement_settings['acquisition_time']
    sample_rate = measurement_settings['sample_rate']
    sig_source = {'Demod_R': f'/{dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{dev_id}/demods/0/sample.AuxIn0'}
    daq_module.set("device", dev_id)
    daq.setInt(f'/{dev_id}/demods/0/enable', 1)
    daq.setInt(f'/{dev_id}/demods/0/trigger', 0)
    daq.setDouble(f'/{dev_id}/demods/0/rate', sample_rate)
    time.sleep(0.2)
    daq_module.set('type', 6)
    daq_module.set('triggernode', f'/{dev_id}/demods/0/sample.TrigIn2')
    daq_module.set('clearhistory', 1)
    daq_module.set('clearhistory', 1)
    daq_module.set('bandwidth', 0)
    daq_module.set('edge', 1)
    columns = np.ceil(duration*sample_rate)
    daq_module.set('grid/mode', 4)
    daq_module.set("count", n_traces)
    daq_module.set("grid/cols", columns)
    daq_module.set('grid/rows', 1)
    daq_module.set("holdoff/time", 0)
    daq_module.set("holdoff/count", 0)
    daq_module.subscribe(sig_source[sig_port])
    time.sleep(0.8)
    columns = daq_module.getInt('grid/cols')
    daq_module.set('endless', 0)
    daq_module.subscribe(sig_source[sig_port])
    daq_module.execute()
    daq_module.finish()
    daq_module.unsubscribe('*')
    daq_module.subscribe(sig_source[sig_port])

def plot_voltage_traces(sample_data):
    voltages = []
    for i in range(len(sample_data)):
        voltages.append(np.array(sample_data[i]['value']).reshape(400))
    voltages = np.array(voltages)
    #c = plt.imshow(voltages,  vmin = np.min(voltages), vmax = np.max(voltages))
    #print(np.shape(voltages))
    plt.imshow(voltages)
    #plt.colorbar(c)
    #plt.show()
