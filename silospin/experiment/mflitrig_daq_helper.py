##Function takes in args:
def mflitrig_daq_helper(daq, ntrigger, time, samplerate, sigport):
    sample_data = daq_module.triggered_data_acquisition_time_domain(acquisition_time, n_traces = ntrigger, sample_rate=samplerate, sig_port  = sigport , plot_on = True)
    return sample_data
