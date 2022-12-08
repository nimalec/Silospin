import pandas as pd
import re
import copy

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
                if item[2] == "p":
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
                    print(item)
                    rfline[int(item[0])].append(item[2:len(item)])
                    if item[2] == "t":
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
