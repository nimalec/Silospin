from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.experiment.setup_experiment_helpers import *
from silospin.experiment import setup_experiment_helpers
from silospin.quantum_compiler.quantum_compiler_helpers import make_gate_parameters
import pickle

class GSTExperiment:
    def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, descriptor="gst_experiment", parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle'):
        initialize_drivers()
        self._instrument_drivers = {'awgs': {0: setup_experiment_helpers.awg_driver_1, 1: setup_experiment_helpers.awg_driver_2}, "mflis": {0: setup_experiment_helpers.mfli_driver_1, 1: setup_experiment_helpers.mfli_driver_2}}
        self._gst_file = gst_file
        self._gate_parameters = unpickle_qubit_parameters(parameter_file_path)["parameters"]
        self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, self._instrument_drivers['awgs'][0], self._gate_parameters, n_inner, n_outer, added_padding=added_padding)
        pickle_waveforms(self._gst_program._waveforms,waveforms_file_path)
        pickle_instrument_parameters(self, setup_experiment_helpers.awg_driver_1.get_all_awg_parameters(), setup_experiment_helpers.awg_driver_2.get_all_awg_parameters(), instruments_file_path)

    def run_program(self):
        self._gst_program.run_program()
