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
    df = df[0:100]

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        seq_line = {"0": [], "1": [], "2": [] , "3":[]} ##refer as seq_line[idx].append(new_gate)
        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            for item in element:
                if len(item)>2:
                    seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                    #sequence_line[int(item[0])-1] = item[2:len(item)]
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[2:len(item)]))
                    else:
                        qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                        length_set.append(qubit_length)
                else:
                    pass
            max_gt_len = max(length_set)
            diff_set = qubit_set.difference(idx_set)
            for item in diff_set:
                #sequence_line[item-1] = "t"+str(max_gt_len)
                seq_line[str(item-1)].append("t"+str(max_gt_len) )

        #sequence_table[idx] = sequence_line
        sequence_table[idx] = seq_line
    return sequence_table

def quantum_protocol_parser_csv_v2(file_path, qubit_lengths, qubit_cores, plunger_channels):
    qubit_sequence_table = {} ## qubit_sequence_table[line][qubit_core] w/ qubit_core = {0,1,2,3}
    plunger_sequence_table = {}  ## plunger_sequence_table[line][plunger_channel] w/ qubit_core = {0,1,2,3,4,5,6,7}
    q_seq_line = {} ##qubit sequence line
    p_seq_line = {}  ##qubit sequence line
    ##Possible non-Z/non-plunger gates
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    ## Read through CSV file ==> convert to data frame
    df = pd.read_csv(file_path, header = None, skiprows=1)

    ##Loop through qubit cores
    for q_idx in qubit_cores:
        #q_seq_line[q_idx-1] = []
        q_seq_line[q_idx] = []
    ##Loop through plunger channels
    # for p_idx in plunger_channels:
    #     p_seq_line[p_idx] = []

    for idx in range(len(df)):
        ##Single line obtained from Pandas data frame
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        ##Each gate in line
        for elem in line:
            element = re.split('\(| \)', elem)
            p_idx_set = set()
            q_idx_set = set()
            length_set = []

            for item in element:
                if len(item)>2:
                    if item[2] == "p":
                        p_seq_line[int(item[0])].append(item[2:len(item)])
                        p_idx_set.add(int(item[0]))
                        #pulse_length = plunger_lengths[item[2:len(item)]]
                        #length_set.append(pulse_length)
                    else:
                        q_seq_line[int(item[0])-1].append(item[2:len(item)])
                        #q_seq_line[int(item[0])].append(item[2:len(item)])
                        if item[2] == "t":
                            length_set.append(int(item[2:len(item)]))
                            q_idx_set.add(int(item[0]))
                        elif item[2] == "z":
                            pass
                        else:
                            qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                            length_set.append(qubit_length)
                            q_idx_set.add(int(item[0])-1)
                else:
                    pass

            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                q_diff_set = qubit_cores.difference(q_idx_set)
                p_diff_set = plunger_channels.difference(p_idx_set)
                for item in q_diff_set:
                    q_seq_line[item].append("t"+str(max_gt_len))
                    #q_seq_line[item].append("t"+str(max_gt_len))
                # for item in p_diff_set:
                #     p_seq_line[item].append("t"+str(max_gt_len))
        # qubit_line = {}
        # for q in q_seq_line:
        #     qubit_line[q] = q_seq_line[q][0:len(q_seq_line[q])/2]
        # qubit_sequence_table[idx] = qubit_line
        qubit_sequence_table[idx] = q_seq_line
        print(qubit_sequence_table[idx])

        #plunger_sequence_table[idx] = p_seq_line
    return qubit_sequence_table, plunger_sequence_table

def quantum_protocol_parser_Zarb(file_path, qubit_lengths, qubit_set = {1,2,3,4}):
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
            for item in element:
                if len(item)>2:
                    seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[3:len(item)]))
                    elif item[2] == "z":
                        length_set.append(32)
                        pass
                    else:
                        qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                        length_set.append(qubit_length)
                else:
                    pass
            max_gt_len = max(length_set)
            diff_set = qubit_set.difference(idx_set)
            for item in diff_set:
                seq_line[str(item-1)].append("t"+str(max_gt_len) )
        sequence_table[idx] = seq_line
    return sequence_table


def quantum_protocol_parser_Zarb_v2(file_path, qubit_lengths, qubit_set = {1,2,3,4}):
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
            for item in element:
                if len(item)>2:
                    seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[3:len(item)]))
                    elif item[2] == "z":
                        channel_set = {"0", "1", "2", "3"}
                        z_idx = {str(int(item[0])-1)}
                        diff_set_z = channel_set.difference(z_idx)
                        for itm in diff_set_z:
                            seq_line[itm].append("z0z")
                    else:
                        qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                        length_set.append(qubit_length)
                else:
                    pass
            if len(length_set) == 0:
                pass
            else:
                max_gt_len = max(length_set)
                diff_set = qubit_set.difference(idx_set)
                for item in diff_set:
                    seq_line[str(item-1)].append("t"+str(max_gt_len))
        sequence_table[idx] = seq_line
    return sequence_table

def quantum_protocol_parser_str(file_path, qubit_lengths, qubit_set = {1,2,3,4}):
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)
    df = df[0:100]

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        seq_line = {"0": [], "1": [], "2": [] , "3":[]} ##refer as seq_line[idx].append(new_gate)
        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            for item in element:
                if len(item)>2:
                    seq_line[str(int(item[0])-1)].append(item[2:len(item)])
                    #sequence_line[int(item[0])-1] = item[2:len(item)]
                    idx_set.add(int(item[0]))
                    if item[2] == "t":
                        length_set.append(int(item[2:len(item)]))
                    else:
                        qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                        length_set.append(qubit_length)
                else:
                    pass
            max_gt_len = max(length_set)
            diff_set = qubit_set.difference(idx_set)
            for item in diff_set:
                #sequence_line[item-1] = "t"+str(max_gt_len)
                seq_line[str(item-1)].append("t"+str(max_gt_len) )

        #sequence_table[idx] = sequence_line
        sequence_table[idx] = seq_line
    return sequence_table


def gst_parser(file_path, qubit_lengths, qubit_set = {0,1,2,3}):
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)

    for idx in range(len(df)):
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        seq_line = {0: [], 1: [], 2: [] , 3: []}

        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            for item in element:
                if len(item)>2:
                    seq_line[int(item[0])].append(item[2:len(item)])
                    qubit_length = qubit_lengths[int(item[0])][gates[item[2:len(item)]]]
                    length_set.append(qubit_length)
                else:
                    pass
            max_gt_len = max(length_set)
            diff_set = qubit_set.difference(idx_set)
            for item in diff_set:
                seq_line[item].append("t"+str(max_gt_len) )
        sequence_table[idx] = seq_line
    return sequence_table
