from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters

from silospin.experiment import setup_pulsed_experiments
from silospin.experiment.setup_quantumalgo_instruments import *
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters

from silospin.drivers.trig_box import TrigBoxDriverSerialServer
from silospin.drivers.mfli_triggered import MfliDaqModule

# class QuantumAlgoExperiment:
#     ##Only utilizes Trigbox, MFLIs. Sweeper modules will utilize this...
#     ##n_outer  ==> will correspond to externally swept parameter (e.g. f, voltage, etc. )
#     ##n_inner  ==> will correspond to inner averaging
#     ##realtime_plot ==> plot output on lockins (arb number) in realtime
#     ##Should allow for arbitrary numberso f dacs
#
#
#     def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, realtime_plot = True, acquisition_time = 3.733e-5, lockin_sample_rate = 107e3, parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle', trigger_client="tcp://127.0.0.1:4243"):
#         ##Take in argument trigger settings
#         initialize_drivers()
#         self._instrument_drivers = {'awgs': {0: setup_pulsed_experiments.awg_driver_1, 1: setup_pulsed_experiments.awg_driver_2}, "mflis": {0: setup_pulsed_experiments.mfli_driver_1}}
#         ##GST  experiment file
#         self._gst_file = gst_file
#         self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)["parameters"]
#
#         awgs = {'hdawg1': self._instrument_drivers['awgs'][0], 'hdawg2': self._instrument_drivers['awgs'][1]}
#         self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, awgs, self._gate_parameters, added_padding=added_padding, n_outer = n_outer, n_inner=n_inner)
#         self._gst_program.compile_program()
#
#         self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
#         self._trig_box = TrigBoxDriverSerialServer()
#
#         daq_module =  MfliDaqModule(self._instrument_drivers['mflis'][0])
#         sample_data, time_axis = daq_module.triggered_data_acquisition_time_domain(duration=trace_duration, n_traces = self._n_trigger, sig_port  = 'Aux_in_1', sample_rate=lockin_sample_rate, plot_on=realtime_plot)
#         self._sample_data = sample_data
#
#     def run_program(self):
#         for i in range(self._n_trigger):
#             self._trig_box.send_trigger()


class QuantumAlgoExperiment:
    ##Only utilizes Trigbox, MFLIs. Sweeper modules will utilize this...
    ##n_outer  ==> will correspond to externally swept parameter (e.g. f, voltage, etc. )
    ##n_inner  ==> will correspond to inner averaging
    ##realtime_plot ==> plot output on lockins (arb number) in realtime
    ##Should allow for arbitrary numberso f dacs

    def __init__(self, sequence_file, n_inner=1, n_outer=1, added_padding=0, realtime_plot = True, acquisition_time = 3.733e-3, lockin_sample_rate = 107e3, sig_port = 'Aux_in_1', trigger_settings = {'client': 'tcp://127.0.0.1:4244', 'tlength': 30, 'holdoff': 4000}, parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0:'dev5761', 1: 'dev5759'}, rf_dc_core_grouping = {'hdawg1': {'rf': [1,2,3,4],'dc':[]}, 'hdawg2': {'rf': [1], 'dc': [2,3,4]}}, trig_channels={'hdawg1': 1,'hdawg2': 1}):
        ##Initialize instruments
        self._instrument_drivers = {'awgs': {}, 'mflis': {}}
        initialize_drivers(awgs, lockins, rf_dc_core_grouping, trig_channels)
        for awg in awgs:
            idx_1 = str(awg)
            idx_2 = str(awg+1)
            line_temp = f'self._instrument_drivers["awgs"][{idx_1}]=setup_quantumalgo_instruments.awg_driver_{idx_2}\n'
            exec(line_temp)
        for mfli in lockins:
            idx_1 = str(mfli)
            idx_2 = str(mfli+1)
            line_temp = f'self._instrument_drivers["mflis"][{idx_1}]=setup_quantumalgo_instruments.awg_driver_{idx_2}\n'
            exec(line_temp)
        awg_drivers = {}
        for awg in awgs:  
            awg_drivers[f'hdawg{str(awg+1)}'] = self._instrument_drivers['awgs'][awg]

        ##Quantum program compilation
        self._sequence_file = sequence_file
        self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)['parameters']
        self._gst_program = GateSetTomographyQuantumCompiler(self._sequence_file, awg_drivers, self._gate_parameters, n_inner=n_inner, n_outer=n_outer,added_padding=added_padding)
        self._gst_program.compile_program()

        ##Trigger box settings ==> add pulse length and holdoff length
        ##Need to moify entire module ==>
        self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
        self._trig_box = TrigBoxDriverSerialServer(client=trigger_settings['client'])
        self._trig_box.set_holdoff(trigger_settings['holdoff'])
        self._trig_box.set_tlength(trigger_settings['tlength'])

        ##Now loop over all lockins
        ## Issue here ==> all lockins waiting for a trigger event here...
        daq_module =  MfliDaqModule(self._instrument_drivers['mflis'][0])
        sample_data, time_axis = daq_module.triggered_data_acquisition_time_domain(duration=trace_duration, n_traces = self._n_trigger, sig_port = sig_port, sample_rate=lockin_sample_rate, plot_on=realtime_plot)
        self._sample_data = sample_data

    def run_program(self):
        for i in range(self._n_trigger):
            self._trig_box.send_trigger()
