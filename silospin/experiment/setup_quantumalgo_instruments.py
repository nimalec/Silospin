from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters


def initialize_drivers(awgs, lockins, rf_dc_core_grouping, trig_channels):
    global_var_str = ''
    for awg in awgs:
        global_var_str += f'global awg_driver_{str(awg+1)}\n'
    for mfli in lockins:
        global_var_str += f'global mfli_driver_{str(mfli+1)}\n'
    print(global_var_str)
    exec(global_var_str)

    channel_mapping, awg_mapping = channel_mapper(rf_dc_core_grouping, trig_channels=trig_channels)
    drivers_str = ''
    quote = '"'

    for awg in awgs:
        drivers_str += f'awg_driver_{awg+1}=HdawgDriver(awgs[{awg}], awg, channel_mapping, awg_mapping)\n'

    for mfli in lockins:
        drivers_str += f'mfli_driver_{mfli+1}=MfliDriver(lockins[{mfli}])\n'

    print(drivers_str)
    exec(drivers_str)
