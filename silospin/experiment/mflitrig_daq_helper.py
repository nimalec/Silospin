##Function takes in args:
from silospin.drivers.mfli_triggered import MfliDriver, MfliDaqModule
import sys
inputs = sys.argv


def mflitrig_daq_helper(device_id=str(inputs[1]), n_traces=int(inputs[2]), acquisition_time=float(inputs[3]), sample_rate=float(inputs[4]), sig_port=str(inputs[5])):
    mfli_driver = MfliDriver(device_id)
    daq_module = MfliDaqModule(mfli_driver)
    sample_data = daq_module.triggered_data_acquisition_time_domain(acquisition_time, n_traces = n_traces, sample_rate=sample_rate, sig_port  = 'Aux_in_1' , plot_on = True)
    return sample_data

if __name__=="__main__":
    sample_data = mflitrig_daq_helper()
    print(sample_data)
