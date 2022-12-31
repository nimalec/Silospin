import pandas as pd
import re
import copy
from math import ceil

from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import obtain_waveform_arbitrary_gate_waveform

def gst_file_parser_v2(file_path, qubit_lengths):
    '''
    Outputs a dictionary representation of a quantum algorithm saved in a CSV file.
    Quantum algorithm should follow standard GST convention.


    Parameters:
                    file_path (str): file path of the CSV quantum algorithm file.
                    qubit_lengths (dict): dictionary containing gate legnths for each qubit. output from 'make_gate_lengths' function.
                    channel_mapping (dict): channel mapping dictionary. output from 'channel_mapper' function.

    Returns:
       gate_parameters (dict): sequence_table representing the interpreted gate sequences for each AWG core and channel.
    '''
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        rf_idxs = set()
        plunger_idxs = set()
        rf_line = {}
        plunger_line = {}
        for rf_idx in qubit_lengths['rf'].keys():
            rf_line[rf_idx] = []
            rf_idxs.add(rf_idx)

        for p_idx in qubit_lengths['plunger'].keys():
            plunger_line[p_idx] = []
            plunger_idxs.add(p_idx)

        rfline = rf_line
        plungerline = plunger_line

        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            temp_set = []

            for item in element:
                if len(item)>2:
                    if item[len(item)-1] in {'x', 'y', 'm', 'p', 'z'}:
                        temp_set.append(item)
                    else:
                        pass
                else:
                    pass

            z_set = []
            notz_set = []
            for gt in temp_set:
                if gt[len(gt)-1] == 'z':
                    z_set.append(gt)
                else:
                    notz_set.append(gt)

            element1 = z_set
            element2 = notz_set

            ##loop over set of z gate
            z_idx = set({})
            for item in element1:
                if item[1] == ')':
                    gt_idx = int(item[0])
                    rfline[gt_idx].append(item[2:len(item)])
                else:
                    gt_idx = int(item[0:2])
                    rfline[gt_idx].append(item[2:len(item)])
                z_idx.add(gt_idx)
                diff_set_z = rf_idxs.difference(z_idx)
                for itm in diff_set_z:
                    rfline[itm].append("z0z")
                for itm in plungerline:
                    plungerline[itm].append("z0z")

            for item in element2:
                if item[2] == 'p':
                    gt_idx = int(item[0])
                    plungerline[gt_idx].append('p')
                    idx_set.add(gt_idx)
                    qubit_length = qubit_lengths["plunger"][gt_idx]['p']
                    length_set.append(qubit_length)

                elif len(item) > 3 and item[3] == 'p':
                    gt_idx = int(item[0:2])
                    plungerline[gt_idx].append('p')
                    idx_set.add(gt_idx)
                    qubit_length = qubit_lengths['plunger'][gt_idx]['p']
                    length_set.append(qubit_length)

                else:
                    if item[1] == ')':
                        rfline[int(item[0])].append(item[2:len(item)])
                        if item[2] == "t":
                            length_set.append(int(item[3:len(item)]))
                        else:
                            idx_set.add(int(item[0]))
                            qubit_length = qubit_lengths["rf"][int(item[0])][gates[item[2:len(item)]]]
                            length_set.append(qubit_length)
                    else:
                        rfline[int(item[0:2])].append(item[3:len(item)])
                        if item[3] == "t":
                            length_set.append(int(item[3:len(item)]))
                        else:
                            idx_set.add(int(item[0:2]))
                            qubit_length = qubit_lengths["rf"][int(item[0:2])][gates[item[2:len(item)]]]
                            length_set.append(qubit_length)

            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set_rf = rf_idxs.difference(idx_set)
                diff_set_plunger = plunger_idxs.difference(idx_set)
                for item in diff_set_rf:
                    rfline[item].append("t"+str(max_gt_len))
                for item in diff_set_plunger:
                    plungerline[item].append("t"+str(max_gt_len))
        sequence_table[idx+1] = {"rf": rfline, "plunger": plungerline}
    return sequence_table

def gst_file_parser_v3(file_path, qubit_lengths, channel_mapping, awg_core_split, sample_rate = 2.4e9, arbgate_picklefile_location = 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_arb_gates.pickle'):
    '''
    Outputs a dictionary representation of a quantum algorithm saved in a CSV file.
    Quantum algorithm should follow standard GST convention.


    Parameters:
                    file_path (str): file path of the CSV quantum algorithm file.
                    qubit_lengths (dict): dictionary containing gate legnths for each qubit. output from 'make_gate_lengths' function.
                    channel_mapping (dict): channel mapping dictionary. output from 'channel_mapper' function.

    Returns:
       gate_parameters (dict): sequence_table representing the interpreted gate sequences for each AWG core and channel.
    '''
    sequence_table = {}
    arbitrary_waveforms = {}
    arbitrary_z = {}

    for awg_idx in channel_mapping:
        arbitrary_waveforms[awg_idx] = {}
        arbitrary_z[awg_idx] = {}
        for core_idx in channel_mapping[awg_idx]:
            arbitrary_waveforms[awg_idx][core_idx] =  []
            arbitrary_z[awg_idx][core_idx] =  set({})

    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1) ## csv -> DF
    arb_gate_dict = unpickle_qubit_parameters(arbgate_picklefile_location) ## arb gate dict
    arbitrary_gates = []

    for idx in range(len(df)): ## loop over all lines in file
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1] #splits each line used semicolins
        rf_idxs = set()
        plunger_idxs = set()
        rf_line = {}
        plunger_line = {}
        arb_gates_line = {}
        ## Obtain RF idxs based on RF keys
        for rf_idx in qubit_lengths['rf'].keys():
            rf_line[rf_idx] = []
            rf_idxs.add(rf_idx)
        ## Obtain DC idxs based on RF keys
        for p_idx in qubit_lengths['plunger'].keys():
            plunger_line[p_idx] = []
            plunger_idxs.add(p_idx)

        rfline = rf_line
        plungerline = plunger_line

        for elem in line:
            ##Loop over each line
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            temp_set = []

            ##Loop over each element of each line
            for item in element:
                ##Loop over each element of each line ==> check to see if regular or RF gate
                if len(item)>2:
                    if item[len(item)-1] in {'x', 'y', 'm', 'p', 'z', 't'}:
                        temp_set.append(item)
                    elif item.find('*') != -1:
                        idx_gt = item.find('*') + 1
                        if item[idx_gt] in arb_gate_dict.keys():
                            temp_set.append(item)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

    ##Separate into Z and non-Z gates
            z_set = []
            notz_set = []
            for gt in temp_set:
                if gt[len(gt)-1] == 'z':
                   ## Modified to add z gate to each  ...
                    z_set.append(gt)
                else:
                    notz_set.append(gt)

            z_idx = set({})
            for item in z_set:
                gt_idx = int(item[item.find('(')+1:item.find(')')])

                z_gt_idx_awg = awg_core_split[gt_idx][0]
                z_gt_idx_core = awg_core_split[gt_idx][1]
                arbitrary_z[z_gt_idx_awg][z_gt_idx_core].add(item[item.find(')')+1:len(item)])

                rfline[gt_idx].append(item[item.find(')')+1:len(item)])
                z_idx.add(gt_idx)
                diff_set_z = rf_idxs.difference(z_idx)
            if len(z_set) == 0 :
                pass
            else:
                for itm in diff_set_z:
                    rfline[itm].append("z0z")
                for itm in plungerline:
                    plungerline[itm].append("z0z")

            ## Loop over all non-Z gates
            for item in notz_set:
                gt_idx = int(item[item.find('(')+1:item.find(')')]) ## obtain idx for this line

                ##Checks if  gate is plunger
                if item[item.find(')')+1]== 'p':
                    plungerline[gt_idx].append('p')
                    idx_set.add(gt_idx)
                    qubit_length = qubit_lengths["plunger"][gt_idx]['p']
                    length_set.append(qubit_length)

              ##Checks if  gate is arb
                elif item.find('*') != -1:
                    gt_label_idx = item.find('*') + 1
                    gt_label = item[gt_label_idx]
                    gt_parameters = arb_gate_dict[gt_label]['parameters']
                    idx_set.add(gt_idx)
                    comma_idxs = [i for i, letter in enumerate(item) if letter == '&']
                    param_values = []
                    ## Arb RF gate
                    if gt_idx in rf_idxs:
                        arbitrary_gates.append((gt_idx, item[item.find(')')+1:len(item)]))
                        rfline[gt_idx].append(item[item.find(')')+1:len(item)])
                        idx_set.add(gt_idx)
                        tau_val = float(item[gt_label_idx+2:comma_idxs[0]])
                        phase_val = float(item[comma_idxs[0]+1:comma_idxs[1]])
                        if len(gt_parameters) == 0:
                            pass
                        elif len(gt_parameters) == 1:
                            param_values.append((gt_parameters[0], float(item[comma_idxs[1]+1:item.find(']')])))
                        else:
                            for idx in range(len(param_values)-1):
                                param_values.append((gt_parameters[idx], float(item[comma_idxs[idx+1]+1:comma_idxs[idx+2]])))
                            param_values.append(gt_parameters[len(param_values)], float(item[comma_idxs[idx+1]+1:item.find(']')]))

                    ## Arb DC gate
                    elif gt_idx in plunger_idxs:
                         arbitrary_gates.append((gt_idx, item[item.find(')')+1:len(item)]))
                         plungerline[gt_idx].append(item[item.find(')')+1:len(item)])
                         idx_set.add(gt_idx)
                         tau_val = float(item[gt_label_idx+2:comma_idxs[0]])
                         if len(gt_parameters) == 0:
                             pass
                         elif len(gt_parameters) == 1:
                             param_values.append((gt_parameters[0], float(item[comma_idxs[0]+1:item.find(']')])))
                         else:
                             for idx in range(len(param_values)-1):
                                 param_values.append((gt_parameters[idx], float(item[comma_idxs[idx]+1:comma_idxs[idx+1]])))
                             param_values.append(gt_parameters[len(param_values)], float(item[comma_idxs[idx]+1:item.find(']')]))
                    else:
                        pass

                    waveform = obtain_waveform_arbitrary_gate_waveform(gt_label, tau_val, param_values, arbgate_picklefile_location)
                    gt_idx_awg = awg_core_split[gt_idx][0]
                    gt_idx_core = awg_core_split[gt_idx][1]
                    arbitrary_waveforms[gt_idx_awg][gt_idx_core].append((item[item.find(')')+1:len(item)], waveform))
                    length_set.append(ceil(1e9*len(waveform)/sample_rate))

                elif item[item.find(')')+1] in {'x', 'y', 'm'}:
                    rf_idx = int(item[item.find('(')+1:item.find(')')])
                    rf_gt = item[item.find(')')+1:len(item)]
                    idx_set.add(rf_idx)
                    rfline[rf_idx].append(rf_gt)
                    qubit_length = qubit_lengths["rf"][rf_idx][gates[rf_gt]]
                    length_set.append(qubit_length)

                elif item[item.find(')')+1] == 't':
                    rf_idx = int(item[item.find('(')+1:item.find(')')])
                    rfline[rf_idx].append(rf_gt)
                    length_set.append(int(item[3:len(item)]))
                else:
                    pass

            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set_rf = rf_idxs.difference(idx_set)
                diff_set_plunger = plunger_idxs.difference(idx_set)
                for item in diff_set_rf:
                    rfline[item].append("t"+str(max_gt_len))
                for item in diff_set_plunger:
                    plungerline[item].append("t"+str(max_gt_len))
        sequence_table[idx+1] = {"rf": rfline, "plunger": plungerline}

    arbZs = {}
    ## Dictionary. Indicates Z gate string, rotation angle, and command table index
    for core_idx in arbitrary_z:
        arbZs[core_idx] = {}
        for awg_idx in arbitrary_z[core_idx]:
            arbZs[core_idx][awg_idx] = {}
            ## Command table index for this z rotation
            itr = 56
            for arbZ in arbitrary_z[core_idx][awg_idx]:
                ## gives tuple: (ct_idx, angle)
                arbZs[core_idx][awg_idx][arbZ] = (itr, arbZ[arbZ.find('z'):len(arbZ)-1])
                itr += 1

    return sequence_table, arbitrary_gates, arbitrary_waveforms, arbZs
