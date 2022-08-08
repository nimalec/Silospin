from silospin.experiment import setup_experiment
from silospin.quantum_compiler.multi_qubit import MultiQubitGST_v5

def GST(gst_file):
    setup_experiment.init()
    awg = setup_experiment.awg_driver
    gst = MultiQubitGST_v5(gst_file, awg)
