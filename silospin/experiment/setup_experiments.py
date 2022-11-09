from silospin.quantum_compiler.quantum_compiler import GateSetTomographyQuantumCompiler
from silospin.experiment.setup_experiment_helpers import initialize_drivers
from silospin.quantum_compiler.quantum_compiler_helpers import make_gate_parameters

class GSTExperiment:
    def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, drivers_initialized=False, descriptor="gst_experiment"):
        if drivers_initialized:
            self._instrument_drivers = {'awgs': {0: initialize_drivers.awg_driver_1}, "mflis": {0: initialize_drivers.mfli_driver_1, 1: initialize_drivers.mfli_driver_2}, 'dac': {0: initialize_drivers.dac_box_1}}
        else:
            initialize_drivers()
            self._instrument_drivers = {'awgs': {0: initialize_drivers.awg_driver_1}, "mflis": {0: initialize_drivers.mfli_driver_1, 1: initialize_drivers.mfli_driver_2}, 'dac': {0: initialize_drivers.dac_box_1}}
        self._gst_file = gst_file
        #experiment_parameters =  get_parameters_file(parameters_file_path)
        #self._gate_parameters = experiment_parameters['qubits']
        #self._gate_parameters =
        tau_pi = {1: 100, 2: 60, 3: 80}
        tau_pi_2 = {1: 50, 2: 30, 3: 40}
        i_amp = {1: 1, 2: 1, 3: 1}
        q_amp  = {1: 1, 2: 1, 3: 1}
        mod_freq = {1: 60e6, 2: 60e6, 3: 60e6}
        plunger_lengths = {7: 5, 8: 5}
        plunger_amp =  {7:  1, 8: 1}
        gate_param = make_gate_parameters(tau_pi, tau_pi_2, i_amp, q_amp, mod_freq, plunger_lengths, plunger_amp)
        self._gst_program = GateSetTomographyProgramPlunger_V4(self._gst_file, self._gate_parameters, self._instrument_drivers['awgs'][0], n_inner, n_outer)

    def run_program(self):
        self._gst_program.run_program()
