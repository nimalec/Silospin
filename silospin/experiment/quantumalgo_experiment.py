from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters

from silospin.experiment import setup_quantumalgo_instruments
from silospin.experiment.setup_quantumalgo_instruments import *
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters

from silospin.drivers.trig_box import TrigBoxDriverSerialServer
from silospin.drivers.mfli_triggered import MfliDaqModule

import subprocess
import numpy as np
import matplotlib.pyplot as plt

class QuantumAlgoExperiment:
    ##Only utilizes Trigbox, MFLIs. Sweeper modules will utilize this...
    ##n_outer  ==> will correspond to externally swept parameter (e.g. f, voltage, etc. )
    ##n_inner  ==> will correspond to inner averaging
    ##realtime_plot ==> plot output on lockins (arb number) in realtime
    ##Should allow for arbitrary numberso f dacs

    def __init__(self, sequence_file, n_inner=1, n_outer=1, added_padding=0, realtime_plot = True, acquisition_time = 3.733e-3, lockin_sample_rate = 107e3, sig_port = 'Aux_in_1', trigger_settings = {'client': 'tcp://127.0.0.1:4244', 'tlength': 30, 'holdoff': 4000}, parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0:'dev5761', 1: 'dev5759'}, rf_dc_core_grouping = {'hdawg1': {'rf': [1,2,3,4],'dc':[]}, 'hdawg2': {'rf': [1], 'dc': [2,3,4]}}, trig_channels={'hdawg1': 1,'hdawg2': 1}):
        ##Initialize instruments
        self._instrument_drivers = {'awgs': {}, 'mflis': {}}
        self._sig_port = sig_port
        #initialize_drivers(awgs, lockins, rf_dc_core_grouping, trig_channels)
        initialize_drivers()
        for awg in awgs:
            idx_1 = str(awg)
            idx_2 = str(awg+1)
            line_temp = f'self._instrument_drivers["awgs"][{idx_1}]=setup_quantumalgo_instruments.awg_driver_{idx_2}\n'
            exec(line_temp)
        for mfli in lockins:
            idx_1 = str(mfli)
            idx_2 = str(mfli+1)
            line_temp = f'self._instrument_drivers["mflis"][{idx_1}]=setup_quantumalgo_instruments.mfli_driver_{idx_2}\n'
            exec(line_temp)
        awg_drivers = {}
        for awg in awgs:
            awg_drivers[f'hdawg{str(awg+1)}'] = self._instrument_drivers['awgs'][awg]

        ##Quantum program compilation
        self._sequence_file = sequence_file
        self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)['parameters']
        self._gst_program = GateSetTomographyQuantumCompiler(self._sequence_file, awg_drivers, self._gate_parameters, n_inner=n_inner, n_outer=n_outer,added_padding=added_padding)
        self._gst_program.compile_program()


        self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
        self._trig_box = TrigBoxDriverSerialServer(client=trigger_settings['client'])
        self._trig_box.set_holdoff(trigger_settings['holdoff'])
        self._trig_box.set_tlength(trigger_settings['tlength'])

        ##Now loop over all lockins
        columns = int(np.ceil(acquisition_time*lockin_sample_rate))
        self._time_axis = np.linspace(0, acquisition_time,  columns)
        v_measured = np.zeros(columns)

        self._daq_modules = {}
        self._sample_data = {}
        self._sig_source = {}
        plot_0_str = ''
        plot_1_str = ''
        for mfli in self._instrument_drivers['mflis']:
            self._daq_modules[mfli] = MfliDaqModule(self._instrument_drivers['mflis'][mfli])
            self._daq_modules[mfli].set_triggered_data_acquisition_time_domain(duration=acquisition_time, sig_port = sig_port, sample_rate=lockin_sample_rate, plot_on=realtime_plot)
            self._sig_source[mfli] = {'Demod_R': f'/{self._daq_modules[mfli]._dev_id}/demods/0/sample.R', 'Aux_in_1': f'/{self._daq_modules[mfli]._dev_id}/demods/0/sample.AuxIn0'}
            self._sample_data[mfli] = []
            plot_0_str += f'fig{mfli}=plt.figure()\nax{mfli} = fig{mfli}.add_subplot(111)\nax{mfli}.set_xlabel("Duration [s]")\nax{mfli}.set_ylabel("Demodulated Voltage [V]")\nline{mfli}, = ax{mfli}.plot(self._time_axis, v_measured, lw=1)\n'
        exec(plot_0_str)


    def run_program(self):
        sig_port = self._sig_port
        for i in range(self._n_trigger):
            for daq in self._daq_modules:
                self._daq_modules[daq]._daq_module.set("count", 1)
                self._daq_modules[daq]._daq_module.execute()
            self._trig_box.send_trigger()
            for daq in self._daq_modules:
                while not self._daq_modules[daq]._daq_module.finished():
                    data_read = self._daq_modules[daq]._daq_module.read(True)
                    if self._sig_source[daq][sig_port].lower() in data_read.keys():
                        #min_val = np.amin(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]))/5
                        #max_val = np.amax(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]))/5
                        #plot_1_str += f'line{daq}.set_data(self._time_axis, data_read[self._sig_source[daq][sig_port].lower()][0]["value"][0])\nax{daq}.set_ylim({min_val},{max_val})\nfig{daq}.canvas.draw()\nfig{daq}.canvas.flush_events()'
                        #exec(plot_1_str)
                        for sig in data_read[self._sig_source[sig_port].lower()]:
                            self._sample_data[daq].append(sig)
                data_read = self._daq_modules[daq]._daq_module.read(True)

                if self._sig_source[daq][sig_port].lower() in data_read.keys():
                    for sig in data_read[self._sig_source[daq][sig_port].lower()]:
                        self._sample_data[daq].append(sig)
                else:
                    pass
                self._daq_modules[daq]._daq_module.finish()
                self._daq_modules[daq]._daq_module.unsubscribe('*')
