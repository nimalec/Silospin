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
