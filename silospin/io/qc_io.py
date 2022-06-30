import pandas as pd
import re

def read_qubit_paramater_file(file_path):
    qubit_parameters = pd.read_csv(file_path)
    return qubit_parameters.to_dict

def write_qubit_parameter_file(qubit_parameters, file_path):
    param_df = pd.DataFrame.from_dict(qubit_parameters)
    param_df.to_csv(file_path)

def quantum_protocol_parser(file_path, qubit_lengths, qubit_set = {1,2,3,4}):
    ##  qubit_lengths = {1 : {"pi": 64, "pi_2": 32}, 2 : {"pi": 65, "pi_2": 34}}
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}
    df = pd.read_csv(file_path, header = None, skiprows=1)
    df = df[0:100]

    for idx in range(len(df)):
        ##splits current line into a sequence
        line = df.values[idx][0].split(";")[0:len(df.values[idx][0].split(";"))-1]
        seq_line = {"0": [], "1": [], "2": [] , "3":[]} ##refer as seq_line[idx].append(new_gate)
        #sequence_line = {}
        #seq_line = []
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
