from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters


def initialize_drivers(awgs, lockins, rf_dc_core_grouping, trig_channels):
    global_var_str = ''
    for awg in awgs:
        global_var_str += f'global awg_driver_{str(awg+1)}\n'
    for mfli in lockins:
        global_var_str += f'global mfli_driver_{str(mfli+1)}\n'
    exec(global_var_str)

    channel_mapping, awg_mapping = channel_mapper(rf_dc_core_grouping, trig_channels=trig_channels)
    drivers_str = ''
    quote = '"'

    itr = 0
    for awg in rf_dc_core_grouping:
        drivers_str += f'awg_driver_{itr+1}=HdawgDriver(awgs[{itr}], {quote}{awg}{quote} , channel_mapping, awg_mapping)\n'
        itr += 1

    for mfli in lockins:
        drivers_str += f'mfli_driver_{mfli+1}=MfliDriver(lockins[{mfli}])\n'

    print(drivers_str)
    exec(drivers_str)
