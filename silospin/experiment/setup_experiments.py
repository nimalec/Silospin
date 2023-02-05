from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.experiment.setup_pulsed_experiments import *
from silospin.experiment import setup_pulsed_experiments
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters  
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import channel_mapper, make_gate_parameters
from silospin.drivers.trigger_box import TriggerBoxServer
import pickle

# class GSTExperiment:
#     def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, descriptor="gst_experiment", parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle'):
#         initialize_drivers()
#         #self._instrument_drivers = {'awgs': {0: setup_experiment_helpers.awg_driver_1, 1: setup_experiment_helpers.awg_driver_2}, "mflis": {0: setup_experiment_helpers.mfli_driver_1, 1: setup_experiment_helpers.mfli_driver_2}}
#         #self._instrument_drivers = {'awgs': {0: setup_experiment_helpers.awg_driver_1, 1: setup_experiment_helpers.awg_driver_2}, "mflis": {0: setup_experiment_helpers.mfli_driver_1, 1: setup_experiment_helpers.mfli_driver_2, 2: setup_experiment_helpers.mfli_driver_3}}
#         self._instrument_drivers = {'awgs': {0: setup_experiment_helpers.awg_driver_1, 1: setup_experiment_helpers.awg_driver_2}}
#         self._gst_file = gst_file
#         self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)["parameters"]
#         self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, self._instrument_drivers['awgs'][0], self._gate_parameters, n_inner, n_outer, added_padding=added_padding)
#         pickle_waveforms(self._gst_program._waveforms,waveforms_file_path)
#         pickle_instrument_parameters(setup_experiment_helpers.awg_driver_1.get_all_awg_parameters(), setup_experiment_helpers.awg_driver_2.get_all_awg_parameters(), setup_experiment_helpers.mfli_driver_1.get_all_mfli_settings(), setup_experiment_helpers.mfli_driver_2.get_all_mfli_settings(), instruments_file_path)
#
#     def run_program(self):
#         self._gst_program.run_program()
#
# class GSTTriggeredExperiment:
#     def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, descriptor="gst_experiment", parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle', trigger_client="tcp://127.0.0.1:4243", trigger_holdoff=20, trigger_pulselength=20):
#         initialize_drivers()
#         self._instrument_drivers = {'awgs': {0: setup_experiment_helpers.awg_driver_1, 1: setup_experiment_helpers.awg_driver_2}, "mflis": {0: setup_experiment_helpers.mfli_driver_1, 1: setup_experiment_helpers.mfli_driver_2, 2: setup_experiment_helpers.mfli_driver_3}}
#         self._gst_file = gst_file
#         self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)["parameters"]
#         self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, self._instrument_drivers['awgs'][0], self._gate_parameters, n_inner, n_outer, added_padding=added_padding)
#         self._gst_program.run_program()
#         self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
#         self._trig_box = TriggerBoxServer(trigger_client)
#         self._trig_box.set_burst_length(self._n_trigger)
#         self._trig_box.set_pulse_length(trigger_pulselength)
#         self._trig_box.set_holdoff(holdoff)
#         pickle_waveforms(self._gst_program._waveforms,waveforms_file_path)
#         pickle_instrument_parameters(setup_experiment_helpers.awg_driver_1.get_all_awg_parameters(), setup_experiment_helpers.awg_driver_2.get_all_awg_parameters(), setup_experiment_helpers.mfli_driver_1.get_all_mfli_settings(), setup_experiment_helpers.mfli_driver_2.get_all_mfli_settings(), instruments_file_path)
#
#     def run_program(self):
#         self._trig_box.trigger()

class QuantumAlgoExperiment:
    def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, descriptor="gst_experiment", parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle', trigger_client="tcp://127.0.0.1:4243"):

        ##Modify, should now include lockins
        initialize_drivers()
        self._instrument_drivers = {'awgs': {0: setup_pulsed_experiments.awg_driver_1, 1: setup_pulsed_experiments.awg_driver_2}, "mflis": {0: setup_pulsed_experiments.mfli_driver_1, 1: setup_pulsed_experiments.mfli_driver_2}}
        ##GST  experiment file
        self._gst_file = gst_file
        self._gate_parameters =  unpickle_qubit_parameters(parameter_file_path)["parameters"]

    #     #Gate parameters
    #     #Generate and compile program for quantum algo
    #     self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, self._instrument_drivers['awgs'][0], self._gate_parameters, n_inner, n_outer, added_padding=added_padding)
    #     self._gst_program.compile_program()
    #     ##Determine number of total trigger events
    #     self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
    #     ## Grab instance of client for DAC box
    #     self._trig_box = TriggerBoxServer(trigger_client)
    #     pickle_waveforms(self._gst_program._waveforms,waveforms_file_path)
    #     pickle_instrument_parameters(setup_experiment_helpers.awg_driver_1.get_all_awg_parameters(), setup_experiment_helpers.awg_driver_2.get_all_awg_parameters(), setup_experiment_helpers.mfli_driver_1.get_all_mfli_settings(), setup_experiment_helpers.mfli_driver_2.get_all_mfli_settings(), instruments_file_path)
    #
    # def run_program(self):
    #     for i in range(self._n_trigger):
    #         self._trig_box.trigger()
