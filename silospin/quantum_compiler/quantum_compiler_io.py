import pandas as pd
import re
import copy

def gst_file_parser(file_path, qubit_lengths, channel_mapping):
    '''
    Outputs the mapping between AWG cores/channels and gate labels. \n
    Outer keys of dictionary correspond to core number running from 1-4 (e.g. chanel_mapping = {1 : {}, ... , 4: {}). These keys have values in the form of dictonaries with the following keys and values. \n
    - "ch", dictionary of the core's output channels, output gate labels, and gate indices in the GST convention (dict) \n
    - "rf", 1 if core is for RF pulses and 0 if for DC pulses (int) \n
    The dictionaries corresponding to the key "ch" have the following keys and values,
    - "index", list of 2 channels corresponding the specified core (grouping given by- 1: [1,2], 2: [3,4], 3: [5,6], 4: [7,8]). \n
    - "label", list of 2 labels corresponding to each channel (e.g. ["i1", "q1"] as IQ pair for RF or  ["p12", "p21"] as 2 plunger channels for DC). \n
    - "gateindex", list of 2 gate indices corresponding to GST indices. (e.g. gate (1)x(1) maps to gateindex [1,1] for core 1 or (7)p(7)(8)p(8) maps to indices [7,8] of core 4.)\n
    Note: currently configured for 1 HDAWG unit with 4 AWG cores.   \n

    Parameters:
                    tau_pi (dict): list of core indices dedicated to RF control (default set to [1,2,3]).
                    tau_pi_2 (dict): list of core indices dedicated to RF control (default set to [1,2,3]).
                    i_amp (dict):
                    q_amp (dict):
                    mod_freq (dict):
                    plunger_lengths (dict):
                    plunger_amp (dict):

    Returns:
       gate_parameters (dict):
    '''
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        rf_idxs = set()
        rf_set = set()
        plunger_idxs = set()
        plunger_set = set()
        rf_line = {}
        plunger_line = {}
        for ii in channel_mapping:
            if channel_mapping[ii]['rf'] == 1:
                rf_idx = str(channel_mapping[ii]['ch']['gateindex'][0]-1)
                rf_idxs.add(channel_mapping[ii]['ch']['gateindex'][0])
                rf_set.add(rf_idx)
                rf_line[rf_idx] = []
            elif channel_mapping[ii]['rf'] == 0:
                plunger_idx_1 = str(channel_mapping[ii]['ch']['gateindex'][0]-1)
                plunger_idx_2 = str(channel_mapping[ii]['ch']['gateindex'][1]-1)
                plunger_idxs.add(plunger_idx_1)
                plunger_idxs.add(plunger_idx_2)
                plunger_set.add("p"+str(plunger_idx_1))
                plunger_set.add("p"+str(plunger_idx_2))
                plunger_line[plunger_idx_1] = []
                plunger_line[plunger_idx_2] = []

            else:
                pass

        rfline = rf_line
        plungerline = plunger_line

        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            temp_set = []

            for item in element:
                if len(item)>2:
                    temp_set.append(item)
                else:
                    pass
            z_set = []
            notz_set = []
            for gt in temp_set:
                if gt[2] == "z":
                    z_set.append(gt)
                else:
                    notz_set.append(gt)

            element1 = z_set
            element2 = notz_set

            ##loop over set of z gate
            for item in element1:
                rfline[str(int(item[0])-1)].append(item[2:len(item)])
                z_idx = {str(int(item[0])-1)}
                diff_set_z = rf_set.difference(z_idx)
                for itm in diff_set_z:
                    rfline[itm].append("z0z")
                for itm in plungerline:
                    plungerline[itm].append("z0z")
            for item in element2:
                if item[2] == "p":
                    plungerline[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add("p"+str(int(item[0])-1))
                    qubit_length = qubit_lengths["plunger"][int(item[0])]['p']
                    length_set.append(qubit_length)

                else:
                    rfline[str(int(item[0])-1)].append(item[2:len(item)])
                    if item[2] == "t":
                        length_set.append(int(item[3:len(item)]))
                    else:
                        idx_set.add(int(item[0]))
                        qubit_length = qubit_lengths["rf"][int(item[0])][gates[item[2:len(item)]]]
                        length_set.append(qubit_length)
            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set_rf = rf_idxs.difference(idx_set)
                diff_set_plunger = plunger_set.difference(idx_set)
                for item in diff_set_rf:
                    rfline[str(item-1)].append("t"+str(max_gt_len))
                for item in diff_set_plunger:
                    plungerline[item[1:len(item)]].append("t"+str(max_gt_len))
        sequence_table[idx] = {"rf": rfline, "plunger": plungerline}
    return sequence_table
