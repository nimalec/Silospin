from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters

from silospin.experiment import setup_quantumalgo_instruments
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

    def __init__(self, sequence_file, n_inner=1, n_outer=1, added_padding=0, realtime_plot = True, acquisition_time = 3.733e-3, lockin_sample_rate = 107e3, sig_port = 'Aux_in_1', trigger_settings = {'client': 'tcp://127.0.0.1:4244', 'tlength': 30, 'holdoff': 4000}, parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0:'dev5761', 1: 'dev5759'}, rf_dc_core_grouping = {'hdawg1': {'rf': [1,2,3,4],'dc':[]}, 'hdawg2': {'rf': [1], 'dc': [2,3,4]}}, trig_channels={'hdawg1': 1,'hdawg2': 1}, mflidaq_file = 'C:\\Users\\Sigillito Lab\\Desktop\\codebases\\Silospin\\silospin\\experiment\\mflitrig_daq_helper.py'):
        ##Initialize instruments
        self._mflidaq_file = mflidaq_file
        self._instrument_drivers = {'awgs': {}, 'mflis': {}}
        self._sig_port = sig_port
        self._lockins = lockins
        self._measurement_settings = {'sample_rate': lockin_sample_rate, 'acquisition_time': acquisition_time}
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
        for mfli in self._instrument_drivers['mflis']:
            self._daq_modules[mfli] = MfliDaqModule(self._instrument_drivers['mflis'][mfli])
            self._sig_source[mfli]  = {'Demod_R': f'/{lockins[mfli]}/demods/0/sample.R' , 'Aux_in_1': f'/{lockins[mfli]}/demods/0/sample.AuxIn0'}
        #    self._daq_modules[mfli].set_triggered_data_acquisition_time_domain_v3(self._measurement_settings['acquisition_time'], sample_rate=self._measurement_settings['sample_rate'], sig_port = sig_port)
            self._sample_data[mfli] = []
            #plot_0_str += f'fig{mfli}=plt.figure()\nax{mfli} = fig{mfli}.add_subplot(111)\nax{mfli}.set_xlabel("Duration [s]")\nax{mfli}.set_ylabel("Demodulated Voltage [V]")\nline{mfli}, = ax{mfli}.plot(self._time_axis, v_measured, lw=1)\n'
    #    exec(plot_0_str)
    #    sample_data = self._daq_modules[0].triggered_data_acquisition_time_domain(self._measurement_settings['acquisition_time'], n_traces = self._n_trigger,  sample_rate=self._measurement_settings['sample_rate'], sig_port  = self._sig_port)

#    def run_program(self):
        # def mflitrig_daq_helper(daqmod, ntrigger, time, samplerate, sigport):
        #     sample_data = daqmod.triggered_data_acquisition_time_domain(time, n_traces = ntrigger, sample_rate=samplerate, sig_port  = sigport , plot_on = True)
        #     return sample_data

        # processes = []
        # for daq in self._daq_modules:
        #     daq_mod = self._daq_modules[daq]
        #     process = Process(target=mflitrig_daq_helper, args=(daq_mod, self._n_trigger, self._measurement_settings['acquisition_time'], self._measurement_settings['sample_rate'], self._sig_port))
        #     process.start()
        #     processes.append(process)
        #
        # for i in range(self._n_trigger):
        #      self._trig_box.send_trigger()
        #
        # for p in processes:
        #     p.join()

    #    triggered_data_acquisition_time_domain(self._measurement_settings['acquisition_time'], n_traces = self._n_trigger,  sample_rate=self._measurement_settings['sample_rate']), sig_port  = self._sig_port)
    #    for mfli in self._lockins:
        #     result = subprocess.run(["python", self._mflidaq_file, self._lockins[mfli], str(self._n_trigger),  str(self._measurement_settings['acquisition_time']), str(self._measurement_settings['sample_rate']), str(self._sig_port)], capture_output=True, text=True)
        #
        # for i in range(self._n_trigger):
        #      self._trig_box.send_trigger()

    ##Initiate lockins here
    ##Loop over to pass in lockins to function and generate plots
    ## Run over trigger events



    def run_program(self):
    #     ## Run background code here ..
        sig_port = self._sig_port
    #     columns = int(np.ceil(self._measurement_settings['acquisition_time']*self._measurement_settings['sample_rate']))
    #     self._time_axis = np.linspace(0, self._measurement_settings['acquisition_time'],  columns)
    #     v_measured = np.zeros(columns)
        for daq in self._daq_modules:
            self._daq_modules[daq]._daq_module.execute()
    #     # plot_0_str = ''
    #     # for mfli in self._instrument_drivers['mflis']:
    #     #     plot_0_str += f'fig{mfli}=plt.figure()\nax{mfli} = fig{mfli}.add_subplot(111)\nax{mfli}.set_xlabel("Duration [s]")\nax{mfli}.set_ylabel("Demodulated Voltage [V]")\nline{mfli}, = ax{mfli}.plot(self._time_axis, v_measured, lw=1)\n'
    #     # exec(plot_0_str)
        #for i in range(self._n_trigger):
        #    t_0 = time.time()
        #     for daq in self._daq_modules:
        #         self._daq_modules[daq].enable_triggered_data_acquisition_time_domain(sig_port)
        #         t_0 = time.time()
        #         self._daq_modules[daq]._daq_module.execute()
        #         t_1 = time.time()
        #         print(t_1 -t_0)
        #    self._trig_box.send_trigger()
            #plot_1_str = ''

    #        for daq in self._daq_modules:
                #self._daq_modules[daq].enable_triggered_data_acquisition_time_domain(sig_port)
                #self._trig_box.send_trigger()
            #    for i in range(self._n_trigger):
        itr = 0
        while not self._daq_modules[daq]._daq_module.finished():
            print(itr)
            self._trig_box.send_trigger()
            #self._trig_box.send_trigger()
            t_0 = time.time()
            data_read = self._daq_modules[daq]._daq_module.read(True)
            if self._sig_source[daq][sig_port].lower() in data_read.keys():
                # min_val = np.amin(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]))/5
                # max_val = np.amax(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[self._sig_source[daq][sig_port].lower()][0]['value'][0]))/5
                # plot_1_str += f'line{daq}.set_data(self._time_axis, data_read[self._sig_source[daq][sig_port].lower()][0]["value"][0])\nax{daq}.set_ylim({min_val},{max_val})\nfig{daq}.canvas.draw()\nfig{daq}.canvas.flush_events()'
                # exec(plot_1_str)
                for sig in data_read[self._sig_source[daq][sig_port].lower()]:
                    self._sample_data[daq].append(sig)
            t_1 = time.time()

            if t_1 - t_0 < self._measurement_settings['acquisition_time'] + 500e-6:
                print(t_1-t_0)
                wait(self._measurement_settings['acquisition_time'] + 500e-6)
            else:
                continue
            itr += 1

        self._daq_modules[daq]._daq_module.finish()
        self._daq_modules[daq]._daq_module.unsubscribe('*')
    #
    #         # t_1 = time.time()
    #         # print(t_1-t_0)
