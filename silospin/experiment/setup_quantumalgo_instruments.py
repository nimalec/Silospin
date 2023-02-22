from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper, make_gate_parameters


# def initialize_drivers(awgs, lockins, rf_dc_core_grouping, trig_channels):
#     global_var_str = ''
#     for awg in awgs:
#         global_var_str += f'global awg_driver_{str(awg+1)}\n'
#     for mfli in lockins:
#         global_var_str += f'global mfli_driver_{str(mfli+1)}\n'
#     exec(global_var_str)
#
#     channel_mapping, awg_mapping = channel_mapper(rf_dc_core_grouping, trig_channels=trig_channels)
#     drivers_str = ''
#     quote = '"'
#
#     itr = 0
#     for awg in rf_dc_core_grouping:
#         drivers_str += f'awg_driver_{itr+1}=HdawgDriver(awgs[{itr}], {quote}{awg}{quote} , channel_mapping, awg_mapping)\n'
#         itr += 1
#
#     for mfli in lockins:
#         drivers_str += f'mfli_driver_{mfli+1}=MfliDriver(lockins[{mfli}])\n'
#
#     print(drivers_str)
#     exec(drivers_str)

def initialize_drivers(awgs={0: 'dev8446', 1: 'dev8485'}, lockins={0: 'dev5759', 1: 'dev5761'}):
    global awg_driver_1
    global awg_driver_2
    global mfli_driver_1
    global mfli_driver_2

    channel_mapping, awg_mapping = channel_mapper({"hdawg1": {"rf":  [1,2,3,4], "dc": []}, "hdawg2":  {"rf": [1], "dc": [2,3,4]}}, trig_channels = {"hdawg1": 1, "hdawg2": 1})
    dev_name_1 = 'hdawg1'
    dev_name_2 = 'hdawg2'
    awg_driver_1 = HdawgDriver(awgs[0], dev_name_1, channel_mapping, awg_mapping)
    awg_driver_2 = HdawgDriver(awgs[1], dev_name_2, channel_mapping, awg_mapping)
    mfli_driver_1 = MfliDriver(lockins[0])
    mfli_driver_2 = MfliDriver(lockins[1])
