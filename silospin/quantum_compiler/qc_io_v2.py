import pandas as pd
import re
import copy


def quantum_protocol_parser_v4(file_path, qubit_lengths, channel_mapping):

    ##1. generate rf and plugner lines
    # rf_idxs = set()
    # rf_set = set()
    # plunger_idxs = set()
    # plunger_set = set()
    # rf_line = {}
    # plunger_line = {}
    # for idx in channel_mapping:
    #     if channel_mapping[idx]['rf'] == 1:
    #         rf_idx = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
    #         rf_idxs.add(channel_mapping[idx]['ch']['gateindex'][0])
    #         rf_set.add(rf_idx)
    #         rf_line[rf_idx] = []
    #     elif channel_mapping[idx]['rf'] == 0:
    #         plunger_idx_1 = str(channel_mapping[idx]['ch']['gateindex'][0]-1)
    #         plunger_idx_2 = str(channel_mapping[idx]['ch']['gateindex'][1]-1)
    #         plunger_idxs.add(plunger_idx_1)
    #         plunger_idxs.add(plunger_idx_2)
    #         plunger_set.add("p"+str(plunger_idx_1))
    #         plunger_set.add("p"+str(plunger_idx_2))
    #         plunger_line[plunger_idx_1] = []
    #         plunger_line[plunger_idx_2] = []

    #     else:
    #         pass

    ##2. setup for sequence table generagtion and define mapping from gates to pulse lengths
    sequence_table = {}
    gates = {"x": "pi_2", "y": "pi_2", "xxx": "pi_2", "yyy": "pi_2",  "xx": "pi", "yy":  "pi", "mxxm": "pi", "myym": "pi"}


    ##3. parse through csv file and generate data frame
    df = pd.read_csv(file_path, header = None, skiprows=1)

    #4. parse through data frame and generate a sequence table

    #outer loop lines in df
    for idx in range(len(df)):
        #split single line in data frame with semicolin
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

        #loop over every gate in the line
        for elem in line:
            element = re.split('\(| \)', elem)
            idx_set = set()
            length_set = []
            temp_set = []

            #if actual gate, append to line
            for item in element:
                if len(item)>2:
                    temp_set.append(item)
                else:
                    pass
            #create sets for z an non-z gates and append to each
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

                #create set of non-z gates within rf defined gates
                diff_set_z = rf_set.difference(z_idx)

                #add zero phase change for non-z gates
                for itm in diff_set_z:
                    rfline[itm].append("z0z")
                #od the same for plungers
                for itm in plungerline:
                    plungerline[itm].append("z0z")

            #loop over set of non-z gates
            for item in element2:

                #check if plungers are present
                if item[2] == "p":
                    #add plunger to line
                    plungerline[str(int(item[0])-1)].append(item[2:len(item)])

                    #add index with 'p' as an idenitfier for plunger gates
                    idx_set.add("p"+str(int(item[0])-1))

                    #obtain qubit lengths
                    #qubit_length = qubit_lengths["plunger"][int(item[0])]
                    qubit_length = qubit_lengths["plunger"][int(item[0])]['p']
                    length_set.append(qubit_length)

                #rf line
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
