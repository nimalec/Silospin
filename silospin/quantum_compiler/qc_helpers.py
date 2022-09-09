from math import ceil
from silospin.math.math_helpers import compute_accumulated_phase, rectangular

def channel_mapper(rf_cores=[1,2,3], plunger_channels = {"p12": 7, "p21": 8}):
    ## Currently set up for only 1 HDAWG with 4 cores
    rf_cores = set(rf_cores) # awg cores used for rf bursts
    channel_mapping = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4} #channel maping (channel -> core)
    core_mapping = {1: [1,2], 2: [3,4], 3: [5,6], 4: [7,8]}#channel maping (core -> channel)
    plunger_labels = dict([(value, key) for key, value in plunger_channels.items()]) #plunger gates (channel -> plunger id)
    plunger_cores = set() #plunger cores being used
    awg_config = {}  #awg configuration to be returend
    ii=1
    for idx in plunger_channels:
        plunger_cores.add(channel_mapping[plunger_channels[idx]])
    n_cores = 4
    for idx in range(1,n_cores+1):
        if idx in rf_cores:
            awg_config[idx] = {"ch": {"index": core_mapping[idx], "label": ["i"+str(ii), "q"+str(ii)], "gateindex": [idx, idx]} , "rf": 1}
            ii +=1
        elif idx in plunger_cores:
            awg_config[idx] = {"ch": {"index": core_mapping[idx], "label": [plunger_labels[core_mapping[idx][0]],plunger_labels[core_mapping[idx][1]]], "gateindex": [core_mapping[idx][0], core_mapping[idx][1]]} , "rf": 0}
        else:
             pass
    return awg_config

def make_gate_parameters(tau_pi, tau_pi_2, i_amp, q_amp, mod_freq, plunger_length, plunger_amp):
    ## index denoted by gate index (use gst format)
    gate_parameters = {}
    #rf_params = {"i_amp": None, "q_amp": None, "tau_pi" : None,  "tau_pi_2" :  None,  "mod_freq": None}
    gate_parameters["rf"] = {}
    gate_parameters["p"] = {}

    for rf_idx in tau_pi:
        gate_parameters["rf"][rf_idx] = {"i_amp": None, "q_amp": None, "tau_pi" : None,  "tau_pi_2" :  None,  "mod_freq": None}
        gate_parameters["rf"][rf_idx]["i_amp"] = i_amp[rf_idx]
        gate_parameters["rf"][rf_idx]["q_amp"] = q_amp[rf_idx]
        gate_parameters["rf"][rf_idx]["tau_pi"] = tau_pi[rf_idx]
        gate_parameters["rf"][rf_idx]["tau_pi_2"] = tau_pi_2[rf_idx]
        gate_parameters["rf"][rf_idx]["mod_freq"] = mod_freq[rf_idx]
    for p_idx in plunger_length:
        gate_parameters["p"][p_idx] = {"tau": None, "p_amp": None}
        gate_parameters["p"][p_idx]["tau"] = plunger_length[p_idx]
        gate_parameters["p"][p_idx]["p_amp"] = plunger_amp[p_idx]
    return gate_parameters

def make_gateset_sequencer(n_seq):
    command_code = ""
    for n in n_seq:
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n"
        command_code = command_code + line
    program = "setTrigger(1);\nsetTrigger(0);\n" + command_code + "waitWave();\n"
    return program

def gate_npoints(gate_parameters, sample_rate):
    gate_npoints = {"rf": {}, "plunger": {}}
    for idx in gate_parameters["rf"]:
        n_pi = ceil(sample_rate*gate_parameters["rf"][idx]["tau_pi"]*1e-9)
        n_pi_2 = ceil(sample_rate*gate_parameters["rf"][idx]["tau_pi_2"]*1e-9)
        gate_npoints["rf"][idx] = {"pi": n_pi, "pi_2": n_pi_2}
    for idx in gate_parameters["p"]:
        n_p = ceil(sample_rate*gate_parameters["p"][idx]["tau"]*1e-9)
        gate_npoints["plunger"][idx] = {"p": n_p}
    return gate_npoints

def make_gateset_sequencer_ext_trigger(n_seq, n_av, trig_channel=True):
    command_code = ""
    for n in n_seq:
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n"
        command_code = command_code + line
    if trig_channel == True:
        trig_program = "repeat("+str(n_av)+"){"+"waitDigTrigger(1);\nsetDIO(1);wait(2);\nsetDIO(0);\n"+"\nwaitDIOTrigger();\nresetOscPhase();"
    else:
        trig_program = "repeat("+str(n_av)+"){"+"\nwaitDIOTrigger();\nresetOscPhase();\n"
    program = trig_program + command_code +"}\n"
    return program

def generate_reduced_command_table(n_pi_2, n_pi, arbZ=[]):
    ##Note: very simplified. Does not include Z, plungers, and edge cases for combo of pi and pi/2 pulses.
    ## ct_idx = 0-7 ==> initial gates
    ## ct_idx = 8-14 ==> pi_2 pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 15-22 ==> pi pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 23 - 25 ==> standard pulse delays
    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": -90, "wave_idx": 0}, "xxx": {"phi": -180, "wave_idx": 0}, "yyy": {"phi": 90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": -90, "wave_idx": 1}, "mxxm": {"phi": -180, "wave_idx": 1}, "myym": {"phi": 90, "wave_idx": 1}}
    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}]
    phases_0_I = [{"value": 0}, {"value": -90}, {"value": -180}, {"value": 90}]
    phases_0_Q = [{"value": -90}, {"value": -180}, {"value": -270}, {"value": 0}]
    phases_incr = [{"value": 0, "increment": True}, {"value": -90, "increment": True}, {"value": -180, "increment": True}, {"value": -270, "increment": True}, {"value": 90, "increment": True},  {"value": 180, "increment": True},{"value": 270, "increment": True}]
    ct_idx = 0
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct.append({"index": ct_idx+1, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    if len(arbZ) == 0:
        pass
    else:
        for item in arbZ:
            ct.append({"index": item[0], "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table


##Note: modify function to handle plunger indices
def generate_reduced_command_table_v2(n_pi_2, n_pi, arbZ=[]):
    ##Note: very simplified. Does not include Z, plungers, and edge cases for combo of pi and pi/2 pulses.
    ## ct_idx = 0-7 ==> initial gates
    ## ct_idx = 8-14 ==> pi_2 pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 15-22 ==> pi pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 23 - 25 ==> standard pulse delays
    ## ct_idx = 26 - 28 ==> plungers
    ## ct_idx = > 29 ==> plungers
    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": -90, "wave_idx": 0}, "xxx": {"phi": -180, "wave_idx": 0}, "yyy": {"phi": 90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": -90, "wave_idx": 1}, "mxxm": {"phi": -180, "wave_idx": 1}, "myym": {"phi": 90, "wave_idx": 1}}
    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}]
    phases_0_I = [{"value": 0}, {"value": -90}, {"value": -180}, {"value": 90}]
    phases_0_Q = [{"value": -90}, {"value": -180}, {"value": -270}, {"value": 0}]
    phases_incr = [{"value": 0, "increment": True}, {"value": -90, "increment": True}, {"value": -180, "increment": True}, {"value": -270, "increment": True}, {"value": 90, "increment": True},  {"value": 180, "increment": True},{"value": 270, "increment": True}]
    ct_idx = 0
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct.append({"index": ct_idx+1, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    if len(arbZ) == 0:
        pass
    else:
        for item in arbZ:
            ct.append({"index": item[0], "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def generate_reduced_command_table_v3(pulse_lengths, arbZ=[], plungers=[]):
    ##Generates a command table and loads onto AWG
    ##pulse lengths ==> tuple of standard pulse lengths (n_pi_2, n_pi) in number of points
    ##arbZ ==> list of tuples ofcarbitrary Z rotations
    ##0-3 ==> initial gates, wv_idx = 0  (f_pi_2^pi_2) [4 elements]
    ##4-7 ==> initial gates, wv_idx = 1 (f_pi^pi) [4 elements]
    ##8-11 ==> initial gates, wv_idx = 2  (f_pi_2^pi) [4 elements]
    ##12-18 ==> phase increment, wv_idx = 0  (f_pi_2^pi_2) [8 elements]
    ##19 - 25 ==> phase increment, wv_idx = 1 (f_pi^pi) [8 elements]
    ##26 - 32 ==> phase increment, wv_idx = 2 (f_pi_2^pi) [8 elements]
    ##33 - 34 ==> time delay, rf pulses [2 elements]
    ##35 - 35 + n_p ==> time delay, barrier pulses [n_p elements]
    ## 36+n_p - 36+n_p+n_z ==>  Z gates [n_z elements]
    ## 37 + n_z  +n_p - 37 + n_z + 2n_p ==> plunger gates [n_p elements]
    (n_pi_2, n_pi) = pulse_lengths
    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": -90, "wave_idx": 0}, "xxx": {"phi": -180, "wave_idx": 0}, "yyy": {"phi": 90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": -90, "wave_idx": 1}, "mxxm": {"phi": -180, "wave_idx": 1}, "myym": {"phi": 90, "wave_idx": 1}}
    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}, {"index": 2, "awgChannel0": ["sigout0","sigout1"]}]
    phases_0_I = [{"value": 0}, {"value": -90}, {"value": -180}, {"value": 90}]
    phases_0_Q = [{"value": -90}, {"value": -180}, {"value": -270}, {"value": 0}]
    phases_incr = [{"value": 0, "increment": True}, {"value": -90, "increment": True}, {"value": -180, "increment": True}, {"value": -270, "increment": True}, {"value": 90, "increment": True},  {"value": 180, "increment": True},{"value": 270, "increment": True}]

    ct_idx = 0
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_0_I)):
         ct.append({"index": ct_idx, "waveform": waves[2], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[2], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct.append({"index": ct_idx+1, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1

    if len(arbZ) == 0:
        pass
    else:
        for item in arbZ:
            ct.append({"index": item[0], "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})
        ct_idx = item[0]

    if len(plungers) == 0:
        pass
    else:
        for item in plungers:
            ct.append({"index": ct_idx+1, "waveform": {"playZero": True, "length": item[1]}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1
    ct_idx += 1
    if len(plungers) == 0:
        pass
    else:
        for item in plungers:
            ct.append({"index": ct_idx, "waveform": item[0], "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table


def make_waveform_placeholders(n_array):
    idx = 0
    sequence_code = ""
    command_code = ""
    for n in n_array:
        n_str = str(n)
        idx_str = str(idx)
        line = "assignWaveIndex(placeholder("+n_str+"),"+idx_str+");\n"
        sequence_code = sequence_code + line
        idx+=1
    return sequence_code

##modify for plungers
## add 2 additional placeholders for plugners
def make_waveform_placeholders_v2(n_array):
    idx = 0
    sequence_code = ""
    command_code = ""
    for n in n_array:
        n_str = str(n)
        idx_str = str(idx)
        line = "assignWaveIndex(placeholder("+n_str+"),"+idx_str+");\n"
        sequence_code = sequence_code + line
        idx+=1
    return sequence_code


def get_ct_idx(phi_a, gt):
    ct_idx_table = {
    "0": {"x": 8, "y": 8, "xxx": 8, "yyy": 8,  "xx": 15, "yy": 15, "mxxm": 15, "myym": 15},
    "90" : {"x": 9, "y": 9, "xxx": 9, "yyy": 9,  "xx": 16, "yy": 16, "mxxm": 16, "myym": 16},
    "180" : {"x": 10, "y": 10, "xxx": 10, "yyy": 10,  "xx": 17, "yy": 17, "mxxm": 17, "myym":17} ,
    "270": {"x": 11, "y": 11, "xxx": 11, "yyy": 11, "xx": 17, "yy": 17, "mxxm": 17, "myym": 17},
    "-90" : {"x": 12, "y": 12, "xxx": 12, "yyy": 12,  "xx": 18, "yy": 18, "mxxm": 18, "myym": 18},
    "-180" : {"x": 13, "y": 13, "xxx": 13, "yyy": 13,  "xx": 19, "yy": 19, "mxxm": 19, "myym": 19},
    "-270": {"x": 14, "y": 14,  "xxx": 14, "yyy": 14,  "xx": 20, "yy": 20, "mxxm": 20, "myym": 20}}
    return ct_idx_table[str(int(phi_a))][gt]

##modify for plungers
def get_ct_idx_v2(phi_a, gt):
    ct_idx_table = {
    "0": {"x": 8, "y": 8, "xxx": 8, "yyy": 8,  "xx": 15, "yy": 15, "mxxm": 15, "myym": 15},
    "90" : {"x": 9, "y": 9, "xxx": 9, "yyy": 9,  "xx": 16, "yy": 16, "mxxm": 16, "myym": 16},
    "180" : {"x": 10, "y": 10, "xxx": 10, "yyy": 10,  "xx": 17, "yy": 17, "mxxm": 17, "myym":17} ,
    "270": {"x": 11, "y": 11, "xxx": 11, "yyy": 11, "xx": 17, "yy": 17, "mxxm": 17, "myym": 17},
    "-90" : {"x": 12, "y": 12, "xxx": 12, "yyy": 12,  "xx": 18, "yy": 18, "mxxm": 18, "myym": 18},
    "-180" : {"x": 13, "y": 13, "xxx": 13, "yyy": 13,  "xx": 19, "yy": 19, "mxxm": 19, "myym": 19},
    "-270": {"x": 14, "y": 14,  "xxx": 14, "yyy": 14,  "xx": 20, "yy": 20, "mxxm": 20, "myym": 20}}
    return ct_idx_table[str(int(phi_a))][gt]


def make_command_table_idxs(gt_seqs, tau_pi_s, tau_pi_2_s, n_arbZ):
    arbZ = []
    ct_idxs = {}
    initial_gates = {"x": 0, "y": 1,  "xx": 4,  "yy": 5, "xxx": 2, "yyy": 3,  "mxxm": 5,  "myym": 7}
    arbZ_counter = 24 + n_arbZ
    phi_ls_gt = {"x":  0, "y": -90, "xx":  0, "yy": -90 , "xxx":  -180, "yyy": 90, "mxxm": -180, "myym": 90}
    for idx in gt_seqs:
        gate_sequence = gt_seqs[idx]
        ct_idx_list = []
        gt_0 = gt_seqs[idx][0]
        if gt_0[0] in {"x", "y", "m"}:
            phi_l = phi_ls_gt[gt_0]
        else:
            phi_l = 0
        ii = 0
        for gt in gate_sequence:
            if ii == 0:
                if gt in {"x", "y", "xxx", "yyy"}:
                    ct_idx_list.append(initial_gates[gt])
                elif gt in {"xx", "yy", "mxxm", "myym"}:
                    ct_idx_list.append(initial_gates[gt])
                elif gt[0] == "t":
                     if int(gt[1:len(gt)]) == tau_pi_2_s:
                         ct_idx_list.append(22)
                     elif int(gt[1:len(gt)]) == tau_pi_s:
                         ct_idx_list.append(23)
                     else:
                         pass
                elif gt[0] == "z":
                    ct_idx_list.append(arbZ_counter)
                    arbZ.append((arbZ_counter, -float(gt[1:len(gt)])))
                    arbZ_counter += 1
                else:
                    pass
            else:
                if gt[0] in {"x", "y", "m"}:
                    phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
                    ct_idx = get_ct_idx(phi_a, gt)
                    if gt in {"x", "y", "xxx", "yyy"}:
                        ct_idx_list.append(ct_idx)
                    else:
                        ct_idx_list.append(ct_idx)
                elif gt[0] == "t":
                    if int(gt[1:len(gt)]) == tau_pi_2_s:
                        ct_idx_list.append(22)
                    elif int(gt[1:len(gt)]) == tau_pi_s:
                        ct_idx_list.append(23)
                elif gt[0] == "z":
                    ct_idx_list.append(arbZ_counter)
                    arbZ.append((arbZ_counter, -float(gt[1:len(gt)-1])))
                    arbZ_counter += 1
                else:
                    pass
            ii += 1
        ct_idxs[idx] = ct_idx_list
    return ct_idxs, arbZ

#modify for plungers
def make_command_table_idxs_v2(gt_seqs, tau_pi_s, tau_pi_2_s, n_arbZ):
    arbZ = []
    ct_idxs = {}
    initial_gates = {"x": 0, "y": 1,  "xx": 4,  "yy": 5, "xxx": 2, "yyy": 3,  "mxxm": 5,  "myym": 7}
    arbZ_counter = 24 + n_arbZ
    phi_ls_gt = {"x":  0, "y": -90, "xx":  0, "yy": -90 , "xxx":  -180, "yyy": 90, "mxxm": -180, "myym": 90}
    for idx in gt_seqs:
        gate_sequence = gt_seqs[idx]
        ct_idx_list = []
        gt_0 = gt_seqs[idx][0]
        if gt_0[0] in {"x", "y", "m"}:
            phi_l = phi_ls_gt[gt_0]
        else:
            phi_l = 0
        ii = 0
        for gt in gate_sequence:
            if ii == 0:
                if gt in {"x", "y", "xxx", "yyy"}:
                    ct_idx_list.append(initial_gates[gt])
                elif gt in {"xx", "yy", "mxxm", "myym"}:
                    ct_idx_list.append(initial_gates[gt])
                elif gt[0] == "t":
                     if int(gt[1:len(gt)]) == tau_pi_2_s:
                         ct_idx_list.append(22)
                     elif int(gt[1:len(gt)]) == tau_pi_s:
                         ct_idx_list.append(23)
                     else:
                         pass
                elif gt[0] == "z":
                    ct_idx_list.append(arbZ_counter)
                    arbZ.append((arbZ_counter, -float(gt[1:len(gt)])))
                    arbZ_counter += 1
                else:
                    pass
            else:
                if gt[0] in {"x", "y", "m"}:
                    phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
                    ct_idx = get_ct_idx(phi_a, gt)
                    if gt in {"x", "y", "xxx", "yyy"}:
                        ct_idx_list.append(ct_idx)
                    else:
                        ct_idx_list.append(ct_idx)
                elif gt[0] == "t":
                    if int(gt[1:len(gt)]) == tau_pi_2_s:
                        ct_idx_list.append(22)
                    elif int(gt[1:len(gt)]) == tau_pi_s:
                        ct_idx_list.append(23)
                elif gt[0] == "z":
                    ct_idx_list.append(arbZ_counter)
                    arbZ.append((arbZ_counter, -float(gt[1:len(gt)-1])))
                    arbZ_counter += 1
                else:
                    pass
            ii += 1
        ct_idxs[idx] = ct_idx_list
    return ct_idxs, arbZ

def generate_waveforms(qubit_gate_lengths, max_idx, amp=1):
    waveforms = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None }, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
    npoints_s_pi  =  qubit_gate_lengths[max_idx]["pi"]
    npoints_s_pi_2 = qubit_gate_lengths[max_idx]["pi_2"]
    for idx in qubit_gate_lengths:
        waveforms[idx]["pi"] = rectangular(qubit_gate_lengths[idx]["pi"], amp, min_points = npoints_s_pi)
        waveforms[idx]["pi_2"] = rectangular(qubit_gate_lengths[idx]["pi_2"], amp, min_points = npoints_s_pi_2)
    return waveforms

#modify for plungers
def generate_waveforms_v2(qubit_gate_lengths, max_idx, amp=1):
    waveforms = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None }, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
    npoints_s_pi  =  qubit_gate_lengths[max_idx]["pi"]
    npoints_s_pi_2 = qubit_gate_lengths[max_idx]["pi_2"]
    for idx in qubit_gate_lengths:
        waveforms[idx]["pi"] = rectangular(qubit_gate_lengths[idx]["pi"], amp, min_points = npoints_s_pi)
        waveforms[idx]["pi_2"] = rectangular(qubit_gate_lengths[idx]["pi_2"], amp, min_points = npoints_s_pi_2)
    return waveforms

def generate_waveforms_v3(gate_npoints, channel_map):
    amp = 1
    waveforms = {}
    for idx in channel_map:
        if channel_map[idx]["rf"] == 1:
            waveforms[idx] = {"pi": None, "pi_2": None, "pi_2_pifr": None}
        elif channel_map[idx]["rf"] == 0:
            waveforms[idx] = {"pi": None, "pi_2": None, "p": None, "p_fr": None}
        else:
            pass

    rf_pi_npoints = {}
    for i in gate_npoints["rf"]:
        rf_pi_npoints[i] = gate_npoints["rf"][i]["pi"]
    plunger_npoints = {}
    for i in gate_npoints["plunger"]:
        plunger_npoints[i] = gate_npoints["plunger"][i]["p"]

    ch_map_rf = {}
    ch_map_p = {}
    for i in ch_map:
        if ch_map[i]["rf"] == 1:
            rf_ch = ch_map[i]["ch"]["gateindex"][0]
            rf_core = i
            ch_map_rf[rf_ch] = rf_core
        else:
            p_ch_1 = ch_map[i]["ch"]["gateindex"][0]
            p_ch_2 = ch_map[i]["ch"]["gateindex"][1]
            p_core = i
            ch_map_p[p_ch_1] = p_core
            ch_map_p[p_ch_2] = p_core

    max_rf_key = max(rf_pi_npoints, key=lambda k: rf_pi_npoints[k])
    npoints_pi_std = gate_npoints["rf"][max_rf_key]["pi"]
    npoints_pi_2_std = gate_npoints["rf"][max_rf_key]["pi_2"]

    max_p_key = max(plunger_npoints, key=lambda k: plunger_npoints[k])
    npoints_p_std = gate_npoints["plunger"][max_p_key]["p"]

    for i in gate_npoints["rf"]:
        idx = ch_map_rf[i]
        waveforms[idx]["pi"] = rectangular(gate_npoints["rf"][i]["pi"], amp, min_points = npoints_pi_std)
        waveforms[idx]["pi_2"] = rectangular(gate_npoints["rf"][i]["pi_2"], amp, min_points = npoints_pi_2_std)
        waveforms[idx]["pi_2_pifr"] = rectangular(gate_npoints["rf"][i]["pi_2"], amp, min_points = npoints_pi_std)

    for i in gate_npoints["plunger"]:
        idx = ch_map_p[i]
        waveforms[idx]["pi"] = rectangular(gate_npoints["plunger"][i]["p"], amp, min_points = npoints_pi_std)
        waveforms[idx]["pi_2"] = rectangular(gate_npoints["plunger"][i]["p"], amp, min_points = npoints_pi_2_std)
        waveforms[idx]["p"] = rectangular(gate_npoints["plunger"][i]["p"], amp, min_points = gate_npoints["plunger"][i]["p"])
        waveforms[idx]["p_fr"] = rectangular(gate_npoints["plunger"][i]["p"], amp, min_points = npoints_p_std)
    return waveforms

def make_ramsey_sequencer(n_start, n_stop, dn, n_rect, n_av):
    sequence = "cvar i;\nconst n_start="+str(n_start)+";\nconst n_stop="+str(n_stop)+ ";\nconst dn="+str(dn)+";\nconst n_samp="+str(n_rect)+";\nwave pulse=rect(n_samp,1);\n\nfor (i = n_start; i < n_stop; i = i + dn){\n   repeat("+str(n_av)+"){\n     setTrigger(1);setTrigger(0);\n     playWave(pulse);\n     waitWave();\n     playZero(i);\n     waitWave();\n     playWave(pulse);\n     waitWave();\n   }\n}"
    return sequence

def make_rabi_sequencer(n_start, n_stop, dn, n_wait, n_av):
    sequence = "cvar i;\nconst n_start="+str(n_start)+";\nconst n_stop="+str(n_stop)+ ";\nconst dn="+str(dn)+";\nconst n_wait="+str(n_wait)+";\n  \nfor (i = n_start; i < n_stop; i = i + dn){\n   repeat("+str(n_av)+"){\n     setTrigger(1);setTrigger(0);\n     playWave(rect(i,1));\n     waitWave();\n     playZero(n_wait);\n     waitWave();\n   }\n}"
    return sequence
