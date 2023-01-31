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
    all_gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS"}
    ohmic_gates = {"Source1", "Drain1", "Source2", "Drain2", "Source3"}
    sensors02 = {"L2", "M2", "R2"}
    topgates = {"B1", "P1", "P2", "B3", "P3", "B4", "P4", "B5"}
    rightddgates = {"B3", "P3", "P4", "B5"}
    sensors1 = {"L1", "M1", "R1"}
    sensors2 = {"L2", "M2", "R2"}
    virtual_gates = {"VP1", "VP2", "VP3", "VP4"}


    if parameter == "channel":
        dac_client.set_channel(value)

    elif parameter == "voltage":
        dac_client.set_voltage(value)

    elif parameter == "channel_voltage":
        ##Takes in a tuple of chanel with voltage
        dac_client.set_channel(value[0])
        dac_client.set_voltage(value[1])

    elif parameter == "channel_voltage_set":
        for i in range(len(value)):
            dac_client.set_channel(value[i][0])
            dac_client.set_voltage(value[i][1])

    elif parameter == "gates_voltages_set":
        for i in range(len(value)):
            if value[i][0] in all_gates:
                dac_client.set_channel(channel_mapping["gates"][value[i][0]])
                dac_client.set_voltage(value[i][1])

            elif value[i][0] in ohmic_gates:
                dac_client.set_channel(channel_mapping["gates"][value[i][0]])
                dac_client.set_voltage(value[i][1])
            else:
                pass

    elif parameter in all_gates:
        print(parameter,value)
        dac_client.set_channel(channel_mapping["gates"][parameter])
        dac_client.set_voltage(value)

    elif parameter in ohmic_gates:
        dac_client.set_channel(channel_mapping["ohmics"][parameter])
        dac_client.set_voltage(value)

    elif parameter == "allgates":
        for gt in all_gates:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter == "ohmics":
        for gt in ohmic_gates:
            dac_client.set_channel(channel_mapping["ohmics"][gt])
            dac_client.set_voltage(value)

    elif parameter == "topgates":
        for gt in topgates:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter == "sensors02":
        for gt in sensors02:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter == "sensors1":
        for gt in sensors1:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter == "sensors2":
        for gt in sensors2:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter == "rightddgates":
        for gt in rightddgates:
            dac_client.set_channel(channel_mapping["gates"][gt])
            dac_client.set_voltage(value)

    elif parameter in virtual_gates:
         virtual_gate_param = unpickle_qubit_parameters(virtual_gate_param_file_path)
         idx = int(parameter[2])-1
         physical_gates = virtual_to_physical(idx, virtual_gate_param)
         dac_client.set_channel(channel_mapping["gates"]["P1"])
         dac_client.set_voltage(physical_gates[0])
         dac_client.set_channel(channel_mapping["gates"]["P2"])
         dac_client.set_voltage(physical_gates[1])
         dac_client.set_channel(channel_mapping["gates"]["P3"])
         dac_client.set_voltage(physical_gates[2])
         dac_client.set_channel(channel_mapping["gates"]["P4"])
         dac_client.set_voltage(physical_gates[3])
    else:
        pass
