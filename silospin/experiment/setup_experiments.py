from silospin.quantum_compiler.quantum_compiler_v2 import GateSetTomographyQuantumCompiler
from silospin.experiment.setup_pulsed_experiments import *
from silospin.experiment import setup_pulsed_experiments
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import channel_mapper, make_gate_parameters
from silospin.drivers.homedac_box import TrigBoxDriverSerialServer
import pickle
from silospin.drivers.mfli_triggered import MfliDaqModule

class QuantumAlgoExperiment:
    def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, descriptor="gst_experiment", parameter_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_qubit_gate_parameters.pickle', waveforms_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_waveforms.pickle', instruments_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_instruments.pickle', trigger_client="tcp://127.0.0.1:4243"):

        ##Modify, should now include lockins
        initialize_drivers()
        self._instrument_drivers = {'awgs': {0: setup_pulsed_experiments.awg_driver_1, 1: setup_pulsed_experiments.awg_driver_2}, "mflis": {0: setup_pulsed_experiments.mfli_driver_1}}
        ##GST  experiment file
        self._gst_file = gst_file
        self._gate_parameters =  unpickle_qubit_parameters(parameter_file_path)["parameters"]

        awgs = {'hdawg1': self._instrument_drivers['awgs'][0], 'hdawg2': self._instrument_drivers['awgs'][1]}
        self._gst_program = GateSetTomographyQuantumCompiler(self._gst_file, awgs, self._gate_parameters, added_padding=added_padding, n_outer = n_outer, n_inner=n_inner)
        self._gst_program.compile_program()

        self._n_trigger = n_inner*n_outer*len(self._gst_program._gate_sequences)
        self._trig_box = TrigBoxDriverSerialServer()

        daq_module =  MfliDaqModule(self._instrument_drivers['mflis'][0])
        # sample_data, time_axis = daq_module.triggered_data_acquisition_time_domain(duration=3.733e-5, n_traces = self._n_trigger, sig_port  = 'Aux_in_1', sample_rate=107e3)

    def run_program(self):
        for i in range(self._n_trigger):
            self._trig_box.send_trigger()
