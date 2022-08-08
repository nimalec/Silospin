from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli2 import MfliDriver

def init(awg_id="dev8446", mfli_id="dev5759"):
    global awg_driver
    global mfli_driver
    global qubit_parameters
    awg_driver = HdawgDriver(awg_id)
    mfli_driver = MfliDriver(mfli_id)
    qubit_parameters =  {
        0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        2: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 120e-9,  "tau_pi_2" :  60e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        3: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 160e-9,  "tau_pi_2" :  80e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
    
