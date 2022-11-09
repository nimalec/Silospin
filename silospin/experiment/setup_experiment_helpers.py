from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli2 import MfliDriver
from silospin.drivers.homedac_box import DacDriverSerial
import pickle

def initialize_drivers(awgs={0: 'dev8446'}, lockins={0: 'dev5759', 1: 'dev5761'}, dacboxes={0: 'COM3'}):
    ##awgs ==> dictionary of AWG device IDs
    ##lockins ==> dictionary of LockIn device IDs
    ##microwaves ==> dictionary of microwave communication ports
    ## dacboxes ==> dictionary of microwave communication ports
    ##Designed for setup with 2 AWGs, 2 lockin amplifiers,
    ##Initialize AWGs
    global awg_driver_1
    global mfli_driver_1
    global mfli_driver_2
    global dac_box_1
    awg_driver_1 = HdawgDriver(awgs[0])
    #awg_driver_2 = HdawgDriver(awgs[1])
    mfli_driver_1 = MfliDriver(lockins[0])
    mfli_driver_2 = MfliDriver(lockins[1])
    dac_box_1 = DacDriverSerial(dev_id=dacboxes[0])

#def update_parameters_file(parameters_file_path, new_parameter_set):
    ##Structure of parameter dictionneirs
    ## 'descriptors': {'experiment_setup', 'time_stamp', 'date' , 'experiment_counter', 'initials' 'descriptors'}
    ## 'instruments': {'descriptors': {'last_update'}, 'awgs': {'awg1', 'awg2'}, 'mflis': {'mfli1', 'mfli2'},
    #'dacs': {'dac0'}}
    ## 'qubits' : {'descriptors': {}, 'parameters': parameter file here}
    #with open(‘filename.pickle’, ‘wb’) as handle:
#        pickle.dump(your_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

#def get_parameters_file(parameters_file_path)
