import pandas as pd
import re

def read_qubit_paramater_file(file_path):
    qubit_parameters = pd.read_csv(file_path)
    return qubit_parameters.to_dict

def write_qubit_parameter_file(qubit_parameters, file_path):
    param_df = pd.DataFrame.from_dict(qubit_parameters)
    param_df.to_csv(file_path)

def quantum_protocol_parser(file_path, qubit_lengths, qubit_set = {1,2,3,4}):
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)
    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        seq_line = {"0": [], "1": [], "2": [] , "3":[]}
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
                    pass
            element1 = z_set
            element2 = notz_set
            for item in element1:
                seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                channel_set = {"0", "1", "2", "3"}
                z_idx = {str(int(item[0])-1)}
                diff_set_z = channel_set.difference(z_idx)
                for itm in diff_set_z:
                    seq_line[itm].append("z0z")
            for item in element2:
                seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                idx_set.add(int(item[0]))
                if item[2] == "t":
                    length_set.append(int(item[3:len(item)]))
                else:
                    qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                    length_set.append(qubit_length)
            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set = qubit_set.difference(idx_set)
                for item in diff_set:
                    seq_line[str(item-1)].append("t"+str(max_gt_len))
        sequence_table[idx] = seq_line
    return sequence_table

def quantum_protocol_parser_v2(file_path, qubit_lengths, channel_mapping):
    ## Break into rf and plunger gate idxs
    rf_idxs = set()
    rf_set = set()
    plunger_idxs = set()
    rf_line = {}
    plunger_line = {}
    for idx in channel_mapping:
        if channel_mapping[idx]['rf'] == 1:
            rf_idx = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            rf_idxs.add(channel_mapping[idx]['ch']['gateindex'][0])
            rf_set.add(rf_idx)
            rf_line[rf_idx] = []
        elif chnls[idx]['rf'] == 0:
            plunger_idx_1 = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            plunger_idx_2 = str(channel_mapping[idx]['ch']['gateindex'][1]-1)
            plunger_idxs.add(plunger_idx_1)
            plunger_idxs.add(plunger_idx_2)
            plunger_line[plunger_idx_1] = []
            plunger_line[plunger_idx_2] = []
        else:
            pass

    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)
    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
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
                    pass
            element1 = z_set
            element2 = notz_set
            for item in element1:
                rfline[str(int(item[0])-1)].append(item[2:len(item)])
                z_idx = {str(int(item[0])-1)}
                diff_set_z = rf_set.difference(z_idx)
                for itm in diff_set_z:
                    rfline[itm].append("z0z")
            for item in element2:
                rfline[str(int(item[0])-1)].append(item[2:len(item)])
                idx_set.add(int(item[0]))
                if item[2] == "t":
                    length_set.append(int(item[3:len(item)]))
                else:
                    qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                    length_set.append(qubit_length)
            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set = rf_idxs.difference(idx_set)
                for item in diff_set:
                    rfline[str(item-1)].append("t"+str(max_gt_len))
        sequence_table[idx] = {"rf": rfline, "plunger": plungerline}
    return sequence_table



def quantum_protocol_parser_v3(file_path, qubit_lengths, channel_mapping):
    ## Break into rf and plunger gate idxs
    rf_idxs = set()
    rf_set = set()
    plunger_idxs = set()
    plunger_set = set()
    rf_line = {}
    plunger_line = {}
    for idx in channel_mapping:
        if channel_mapping[idx]['rf'] == 1:
            rf_idx = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            rf_idxs.add(channel_mapping[idx]['ch']['gateindex'][0])
            rf_set.add(rf_idx)
            rf_line[rf_idx] = []
        elif channel_mapping[idx]['rf'] == 0:
            plunger_idx_1 = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            plunger_idx_2 = str(channel_mapping[idx]['ch']['gateindex'][1]-1)
            plunger_idxs.add(plunger_idx_1)
            plunger_idxs.add(plunger_idx_2)
            plunger_set.add("p"+str(plunger_idx_1))
            plunger_set.add("p"+str(plunger_idx_2))
            plunger_line[plunger_idx_1] = []
            plunger_line[plunger_idx_2] = []

        else:
            pass
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)
    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
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
                    idx_set.add("p"+item[0])
                else:
                    rfline[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add(int(item[0]))

                if item[2] == "t":
                    length_set.append(int(item[3:len(item)]))
                elif item[2] == "p":
                    qubit_length = qubit_lengths["plunger"][int(item[0])]
                    length_set.append(qubit_length)
                else:
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

def quantum_protocol_parser_v4(file_path, qubit_lengths, channel_mapping):
    rf_idxs = set()
    rf_set = set()
    plunger_idxs = set()
    plunger_set = set()
    rf_line = {}
    plunger_line = {}
    for idx in channel_mapping:
        if channel_mapping[idx]['rf'] == 1:
            rf_idx = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            rf_idxs.add(channel_mapping[idx]['ch']['gateindex'][0])
            rf_set.add(rf_idx)
            rf_line[rf_idx] = []
        elif channel_mapping[idx]['rf'] == 0:
            plunger_idx_1 = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            plunger_idx_2 = str(channel_mapping[idx]['ch']['gateindex'][1]-1)
            plunger_idxs.add(plunger_idx_1)
            plunger_idxs.add(plunger_idx_2)
            plunger_set.add("p"+str(plunger_idx_1))
            plunger_set.add("p"+str(plunger_idx_2))
            plunger_line[plunger_idx_1] = []
            plunger_line[plunger_idx_2] = []

        else:
            pass

    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
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
                    qubit_length = qubit_lengths["plunger"][int(item[0])]
                    length_set.append(qubit_length)
                else:
                    rfline[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[3:len(item)]))
                    else:
                        qubit_length = qubit_lengths["rf"][int(item[0])-1][gates[item[2:len(item)]]]
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




def quantum_protocol_parser_v5(file_path, qubit_lengths, channel_mapping):
    ## qubit_length has form:
    ##gate_standard_lengths = {"pi_2": ceil(tau_pi_2_standard*1e-9), "pi": ceil(tau_pi_standard*1e-9), "p": p_dict}
    rf_idxs = set()
    rf_set = set()
    plunger_idxs = set()
    plunger_set = set()
    rf_line = {}
    plunger_line = {}
    for idx in channel_mapping:
        if channel_mapping[idx]['rf'] == 1:
            rf_idx = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            rf_idxs.add(channel_mapping[idx]['ch']['gateindex'][0])
            rf_set.add(rf_idx)
            rf_line[rf_idx] = []
        elif channel_mapping[idx]['rf'] == 0:
            plunger_idx_1 = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
            plunger_idx_2 = str(channel_mapping[idx]['ch']['gateindex'][1]-1)
            plunger_idxs.add(plunger_idx_1)
            plunger_idxs.add(plunger_idx_2)
            plunger_set.add("p"+str(plunger_idx_1))
            plunger_set.add("p"+str(plunger_idx_2))
            plunger_line[plunger_idx_1] = []
            plunger_line[plunger_idx_2] = []

        else:
            pass

    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
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
                    qubit_length = qubit_lengths["plunger"][int(item[0])]
                    length_set.append(qubit_length)
                else:
                    rfline[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[3:len(item)]))
                    else:
                        qubit_length = qubit_lengths["rf"][int(item[0])-1][gates[item[2:len(item)]]]
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
