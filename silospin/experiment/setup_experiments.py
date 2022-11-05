from silospin.quantum_compiler.qc_v3 import GateSetTomographyProgramPlunger_V4
from silospin.experiment.setup_experiment_helpers import initialize_drivers, get_parameters_file

class GSTExperiment:
    def __init__(self, gst_file, n_inner=1, n_outer=1, added_padding=0, drivers_initialized=False, descriptor="gst_experiment"):
        if drivers_initialized:
            self._instrument_drivers = {'awgs': {0: initialize_drivers.awg_driver_1}, "mflis": {0: initialize_drivers.mfli_driver_1, 1: initialize_drivers.mfli_driver_2}, 'dac': {0: initialize_drivers.dac_box_1}}
        else:
            initialize_drivers()
            self._instrument_drivers = {'awgs': {0: initialize_drivers.awg_driver_1}, "mflis": {0: initialize_drivers.mfli_driver_1, 1: initialize_drivers.mfli_driver_2}, 'dac': {0: initialize_drivers.dac_box_1}}
        self._gst_file = gst_file
        experiment_parameters =  get_parameters_file(parameters_file_path)
        self._gate_parameters = experiment_parameters['qubits']
        self._gst_program = GateSetTomographyProgramPlunger_V4(self._gst_file, self._gate_parameters, self._instrument_drivers['awgs'][0], n_inner, n_outer)

    def run_program(self):
        self._gst_program.run_program()
