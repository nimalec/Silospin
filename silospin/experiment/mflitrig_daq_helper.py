##Function takes in args:
def mflitrig_daq_helper(daqmod, ntrigger, time, samplerate, sigport):
    sample_data = daqmod.triggered_data_acquisition_time_domain(time, n_traces = ntrigger, sample_rate=samplerate, sig_port  = sigport , plot_on = True)
    return sample_data
