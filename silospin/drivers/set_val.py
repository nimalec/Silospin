"""Homebuilt digital-to-analog converter (DAC) server.

Run this on the command line as:

>> python dacserver.py

Version from November 2022.
"""

import serial
from zerorpc import Client
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters, pickle_dac_parameters
from silospin.analysis.virtualgates import virtual_to_physical

def make_dac_channel_mapping(channel_map=None, dac_param_file ='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac.pickle', dev_id='COM3'):
    if channel_map:
        dac_channel_mapping = channel_map
    else:
        dac_channel_mapping = {"gates":
         {"B1": 1, "B2": 2, "B3": 3, "B4": 4, "B5": 5, "P1": 6, "P2": 7,  "P3": 8, "P4": 9, "L1": 10, "L2": 11,  "M1": 12, "M2": 13,  "R1": 14, "R2": 15,  "BS1": 16, "BS2": 17, "TS": 18, "MS": 19} ,
        "ohmics": {"Source1": 20, "Drain1": 21, "Source2": 22, "Drain2": 23, "Source3": 24}}
    pickle_dac_parameters(channel_mapping=channel_map, instruments_file_path=dac_param_file,dev_id=dev_id)
    return dac_channel_mapping

def set_val(parameter, value, channel_mapping, dac_client, virtual_gate_param_file_path='C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_virtual_param.pickle'):
    ## parameter ==> string of parameter passed in
    ## value ==> corresponding voltage to set)
    ##channel_mapping ==> map from gate type to channel number
    ##dac_client ==> pre-connected client for dac

    ##Groupings for each gate
    all_gates = {'B1', 'B2', 'B3', 'B4', 'B5', 'P1', 'P2', 'P3', 'P4', 'SM', 'ST', 'L1', 'L3', 'A1', 'O1', 'O2', 'M1', 'M3', 'R1', 'R3', 'SL',  'AOM', 'AOR', 'OR'}
    rightgates = {'B3', 'P3', 'P4', 'B5'}
    ohmic_gates = {"Source1", "Drain1", "Source2", "Drain2", "Source3"}
    sensors02 = {'L2', 'M2', 'R2'}
    topgates = {'B1', 'B2', 'B3', 'B4', 'B5', 'P1', 'P2', 'P3', 'P4'}
    rightddgates = {"B3", "P3", "P4", "B5"}
    sensors1 = {"L1", "M1", "R1"}
    sensors2 = {"L2", "M2", "R2"}
    virtual_gates = {"VP1", "VP2", "VP3", "VP4"}

    all_gate_maps = {}
    voltage_divide = {}
    for dac in channel_mapping:
        gate_map = channel_mapping[dac]['channel_mapping']
        volage_dividers = channel_mapping[dac]['dividers']
        for gate in gate_map:
            all_gate_maps[gate] = gate_map[gate]
        for ch in volage_dividers:
            voltage_divide[ch] = volage_dividers[ch]


    dac_channel_map = {1: (1,1), 2: (1,2), 3: (1,3), 4: (1,4), 5: (1,5), 6: (1,6),
    7: (1,7), 8: (1,8), 9: (1,9), 10: (1,10), 11: (1,11), 12: (1,12), 13: (1,13), 14: (1,14),
    15: (1,15), 16: (1,16), 17: (1,17), 18: (1,18), 19: (1,19), 20: (1,20), 21: (1,21),
    22: (1,22), 23: (1,23), 24: (1,24), 25: (2,1), 26: (2,2), 27: (2,3), 28: (2,4), 29: (2,5), 30: (2,6),
    31: (2,7), 32: (2,8), 33: (2,9), 34: (2,10), 35: (2,11), 36: (2,12), 37: (2,13), 38: (2,14),
    39: (2,15), 40: (2,16), 41: (2,17), 42: (2,18), 43: (2,19), 44: (2,20), 45: (2,21),
    46: (2,22), 47: (2,23), 48: (2,24)}


    if parameter == "channel":
        dac_idx = dac_channel_map[value][0]
        ch_idx =  dac_channel_map[value][1]
        if dac_idx == 1:
            dac_client.set_channel_1(ch_idx)
        elif dac_idx == 2:
            dac_client.set_channel_2(ch_idx)
        else:
            pass

    # elif parameter == "channel_voltage":
    #     ## Comes as pair: (ch_idx, voltage)
    #     dac_idx = dac_channel_map[value[0]][0]
    #     ch_idx =  dac_channel_map[value[0]][1]
    #     ##Takes in a tuple of chanel with voltage
    #     if dac_idx == 1:
    #         dac_client.set_channel_1(ch_idx)
    #         dac_client.set_voltage_1(value[1])
    #     elif dac_idx == 2:
    #         dac_client.set_channel_2(ch_idx)
    #         dac_client.set_voltage_2(value[1])
    #     else:
    #         pass

    # elif parameter == "channel_voltage_set":
    #     ## set of channels and  voltages
    #     for i in range(len(value)):
    #         dac_idx = dac_channel_map[value[i][0]][0]
    #         ch_idx =  dac_channel_map[value[i][0]][1]
    #         if dac_idx == 1:
    #             dac_client.set_channel_1(ch_idx)
    #             dac_client.set_voltage_1(value[i][1])
    #         elif dac_idx == 2:
    #             dac_client.set_channel_2(ch_idx)
    #             dac_client.set_voltage_2(value[i][1])
    #         else:
    #             pass

    # elif parameter == "gates_voltages_set":
    #     ##Set of gates and voltages
    #     for i in range(len(value)):
    #         dac_idx = dac_channel_map[all_gate_maps[value[i][0]]][0]
    #         ch_idx =  dac_channel_map[all_gate_maps[value[i][0]]][1]
    #         if dac_idx == 1:
    #             dac_client.set_channel_1(ch_idx)
    #             dac_client.set_voltage_1(value[i][1])
    #         elif dac_idx == 2:
    #             dac_client.set_channel_2(ch_idx)
    #             dac_client.set_voltage_2(value[i][1])
    #         else:
    #             pass


    elif parameter in all_gates or parameter in ohmic_gates:
        dac_idx = dac_channel_map[all_gate_maps[parameter]][0]
        ch_idx = dac_channel_map[all_gate_maps[parameter]][1]
        print(ch_idx)

        if dac_idx == 1:
            dac_client.set_channel_1(ch_idx)
            dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[parameter]])
            #dac_client.set_voltage_1(value)
        elif dac_idx == 2:
            dac_client.set_channel_2(ch_idx)
            dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[parameter]])
            # dac_client.set_voltage_2(value)
        else:
            pass

    elif parameter == 'allgates':
        for gt in all_gates:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]

            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass

    elif parameter == 'ohmics':
        for gt in ohmics:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass


    elif parameter == 'topgates':
        for gt in topgates:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass

    elif parameter == 'ohmics':
        for gt in ohmic_gates:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass
    elif parameter == 'sensors02':
        for gt in sensors02:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass

    elif parameter == 'sensors1':
        for gt in sensors1:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value)/voltage_divide[all_gate_maps[gt]]
            else:
                pass

    elif parameter == 'sensors2':
        for gt in sensors2:
            dac_idx = dac_channel_map[all_gate_maps[gt]][0]
            ch_idx = dac_channel_map[all_gate_maps[gt]][1]
            if dac_idx == 1:
                dac_client.set_channel_1(ch_idx)
                dac_client.set_voltage_1(value/voltage_divide[all_gate_maps[gt]])
            elif dac_idx == 2:
                dac_client.set_channel_2(ch_idx)
                dac_client.set_voltage_2(value/voltage_divide[all_gate_maps[gt]])
            else:
                pass
    #
    # elif parameter in virtual_gates:
    #      virtual_gate_param = unpickle_qubit_parameters(virtual_gate_param_file_path)
    #      idx = int(parameter[2])-1
    #      physical_gates = virtual_to_physical(idx, virtual_gate_param)
    #      dac_client.set_channel(channel_mapping["gates"]["P1"])
    #      dac_client.set_voltage(physical_gates[0])
    #      dac_client.set_channel(channel_mapping["gates"]["P2"])
    #      dac_client.set_voltage(physical_gates[1])
    #      dac_client.set_channel(channel_mapping["gates"]["P3"])
    #      dac_client.set_voltage(physical_gates[2])
    #      dac_client.set_channel(channel_mapping["gates"]["P4"])
    #      dac_client.set_voltage(physical_gates[3])
    # else:
    #     pass
