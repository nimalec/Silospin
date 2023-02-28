from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters

from silospin.experiment import setup_quantumalgo_instruments
from silospin.experiment.measurement_settings import *
from silospin.experiment.setup_quantumalgo_instruments import *
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters
from silospin.experiment.mflitrig_daq_helper import mflitrig_daq_helper

from silospin.drivers.trig_box import TrigBoxDriverSerialServer
from silospin.drivers.mfli_triggered import MfliDaqModule

import numpy as np
import matplotlib.pyplot as plt
import time
from multiprocessing import Process

class QuantumAlgoExperiment:
    ##Only utilizes Trigbox, MFLIs. Sweeper modules will utilize this...
    ##n_outer  ==> will correspond to externally swept parameter (e.g. f, voltage, etc. )
    ##n_inner  ==> will correspond to inner averaging
    ##realtime_plot ==> plot output on lockins (arb number) in realtime
    ##Should allow for arbitrary numberso f dacs

    def __init__(self, sequence_file, n_inner=1, n_outer=1, added_padding=0, realtime_plot = True, acquisition_time = 3.733e-3, lockin_sample_rate = 107e3, sig_port = 'Aux_in_1', trigger_settings = {'client': 'tcp://127.0.0.1:4244', 'tlength': 70, 'holdoff': 4000}, parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0:'dev5761', 1: 'dev5759'}, rf_dc_core_grouping = {'hdawg1': {'rf': [1,2,3,4],'dc':[]}, 'hdawg2': {'rf': [1], 'dc': [2,3,4]}}, trig_channels={'hdawg1': 1,'hdawg2': 1}, mflidaq_file = 'C:\\Users\\Sigillito Lab\\Desktop\\codebases\\Silospin\\silospin\\experiment\\mflitrig_daq_helper.py'):
        ##Initialize instruments
        self._mflidaq_file = mflidaq_file
        self._instrument_drivers = {'awgs': {}, 'mflis': {}}
        self._sig_port = sig_port
        self._lockins = lockins
        self._measurement_settings = {'sample_rate': lockin_sample_rate, 'acquisition_time': acquisition_time}
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

        self._daq_modules = {}
        self._sample_data = {}
        self._sig_sources = {}

        for mfli in self._instrument_drivers['mflis']:
           self._daq_modules[mfli] = MfliDaqModule(self._instrument_drivers['mflis'][mfli])
           self._sig_sources[mfli]  = {'Demod_R': f'/{lockins[mfli]}/demods/0/sample.R' , 'Aux_in_1': f'/{lockins[mfli]}/demods/0/sample.AuxIn0'}
           self._sample_data[mfli] = []

#        self._daq_module = self._daq_modules[0]._daq_module
#        self._daq = self._daq_modules[0]._daq

    def run_program(self):
        for mfli in self._lockins:
            daq_measurement_settings(self._n_trigger, self._daq_modules[mfli]._daq_module, self._daq_modules[mfli]._daq, self._lockins[mfli], self._measurement_settings, self._sig_port)

        #dev_id = self._lockins[0]
        #sig_source = {'Demod_R': f'/{dev_id}/demods/0/sample.R','Aux_in_1': f'/{dev_id}/demods/0/sample.AuxIn0'}
        #sample_data = []
        #daq_measurement_settings(self._n_trigger, self._daq_module, self._daq, self._lockins[0], self._measurement_settings, self._sig_port)

        duration = self._daq_modules[0]._daq_module.getDouble("duration")
        columns = self._daq_modules[0]._daq_module.getInt('grid/cols')
        time_axis = np.linspace(0, duration,  columns)
        v_measured = np.zeros(columns)
        plot_0_str = ''
        for mfli in self._lockins:
            plot_0_str += f'fig{mfli}=plt.figure()\nax{mfli} = fig{mfli}.add_subplot(111)\nax{mfli}.set_xlabel("Duration [Seconds]")\nax{mfli}.set_ylabel("Demodulated Voltage [Voltage]")\nline{mfli}, = ax{mfli}.plot(time_axis, v_measured, lw=1)\n'
            self._daq_modules[mfli]._daq_module.execute()
        exec(plot_0_str)

        # fig = plt.figure()
        # ax1 = fig.add_subplot(111)
        # ax1.set_xlabel('Time [seconds]')
        # ax1.set_ylabel('Demodulated Voltage [Volts]')
        # line, = ax1.plot(time_axis, v_measured, lw=1)

    #    self._daq_module.execute()
        data_reads = {}
        #for i in range(self._n_trigger):
        while not self._daq_modules[0]._daq_module.finished():
    #    while not self._daq_module.finished():
             self._trig_box.send_trigger()
             for mfli in self._lockins:
                 data_reads[mfli] = self._daq_modules[mfli]._daq_module.read(True)
            #data_read = self._daq_module.read(True)
                 if self._sig_sources[mfli][self._sig_port].lower() in data_reads[mfli].keys():
            #    if sig_source[self._sig_port].lower() in data_read.keys():
                    #min_val = np.amin(data_read[sig_source[self._sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[sig_source[self._sig_port].lower()][0]['value'][0]))/5
                    #max_val =   np.amax(data_read[sig_source[self._sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[sig_source[self._sig_port].lower()][0]['value'][0]))/5
                     min_val = np.amin(data_reads[mfli][self._sig_sources[mfli][self._sig_port].lower()][0]['value'][0]) - abs(np.amin(data_reads[mfli][self._sig_sources[mfli][self._sig_port].lower()][0]['value'][0]))/5
                     max_val = np.amax(data_reads[mfli][self._sig_sources[mfli][self._sig_port].lower()][0]['value'][0]) + abs(np.amax(data_reads[mfli][self._sig_sources[mfli][self._sig_port].lower()][0]['value'][0]))/5

                    ##Replace this ....
                    # line.set_data(time_axis, data_read[sig_source[self._sig_port].lower()][0]['value'][0])
                    # ax1.set_ylim(min_val, max_val)
                    # fig.canvas.draw()
                    # fig.canvas.flush_events()

                     plot_1 = f'line{mfli}.set_data(time_axis, data_reads[{mfli}][self._sig_sources[{mfli}][self._sig_port].lower()][0]["value"][0])\nax{mfli}.set_ylim({min_val}, {max_val})\nfig{mfli}.canvas.draw()\nfig{mfli}.canvas.flush_events()'
                     exec(plot_1)
                    #for each in data_read[sig_source[self._sig_port].lower()]:
                     for each in data_reads[mfli][self._sig_sources[mfli][self._sig_port].lower()]:
                         self._sample_data[mfli].append(each)
             time.sleep(duration)

        for mfli in self._lockins:
            data_reads[mfli] = self._daq_modules[mfli]._daq_module.read(True)
            if self._sig_sources[mfli][self._sig_port].lower() in data_reads[mfli].keys():
                for each in data_read[self._sig_sources[mfli][self._sig_port].lower()]:
                    self._sample_data[mfli].append(each)
                    self._daq_modules[mfli]._daq_module.finish()
                    self._daq_modules[mfli]._daq_module('*')


        #data_read = self._daq_module.read(True)
        # if sig_source[self._sig_port].lower() in data_read.keys():
        #     for each in data_read[sig_source[self._sig_port].lower()]:
        #         sample_data.append(each)

        # self._daq_module.finish()
        # self._daq_module.unsubscribe('*')
        #self._sample_data = sample_data
        #plot_voltage_traces(self._sample_data, self._measurement_settings['acquisition_time'])
