from math import ceil
from silospin.math.math_helpers import compute_accumulated_phase, rectangular

def channel_mapper(rf_cores, plunger_channels = {"p12": 7, "p21": 8}):
    ## Currently set up for only 1 HDAWG with 4 cores
    rf_cores = set(rf_cores)
    channel_mapping = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}
    core_mapping = {1: [1,2], 2: [3,4], 3: [5,6], 4: [7,8]}
    plunger_labels = dict([(value, key) for key, value in plunger_channels.items()])

    plunger_cores = set()
    for idx in plunger_channels:
        plunger_cores.add(channel_mapping[plunger_channels[idx]])

    n_cores = 4
    for idx in range(1,n_cores+1):
        if idx in rf_cores:
            awg_config[idx] = {"ch": {"index": core_mapping[idx], "label": ["i"+str(core_mapping[idx][0]), "q"+str(core_mapping[idx][1])], "gateindex": [idx, idx]} , "rf": 1}
        # elif idx in plunger_cores:
        #     awg_config[idx] = {"ch": {"index": core_mapping[idx], "label": [plunger_labels[], plunger_labels[], "gateindex": [idx, idx]} , "rf": 0}
        else:
            pass


    # n_cores = 4
    # awg_config = {}
    # for idx in range(n_cores):
    #     if idx in rf_cores:
    #
    # awg_config[idx] = {"ch": {"index": [1,2] , "label": ["i1", "q1"], "gateindex": [1, 1]} , "rf": 1}

def make_gateset_sequencer(n_seq):
    command_code = ""
    for n in n_seq:
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n"
        command_code = command_code + line
    program = "setTrigger(1);\nsetTrigger(0);\n" + command_code + "waitWave();\n"
    return program

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

def generate_waveforms(qubit_gate_lengths, max_idx, amp=1):
    waveforms = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None }, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
    npoints_s_pi  =  qubit_gate_lengths[max_idx]["pi"]
    npoints_s_pi_2 = qubit_gate_lengths[max_idx]["pi_2"]
    for idx in qubit_gate_lengths:
        waveforms[idx]["pi"] = rectangular(qubit_gate_lengths[idx]["pi"], amp, min_points = npoints_s_pi)
        waveforms[idx]["pi_2"] = rectangular(qubit_gate_lengths[idx]["pi_2"], amp, min_points = npoints_s_pi_2)
    return waveforms

def make_ramsey_sequencer(n_start, n_stop, dn, n_rect, n_av):
    sequence = "cvar i;\nconst n_start="+str(n_start)+";\nconst n_stop="+str(n_stop)+ ";\nconst dn="+str(dn)+";\nconst n_samp="+str(n_rect)+";\nwave pulse=rect(n_samp,1);\n\nfor (i = n_start; i < n_stop; i = i + dn){\n   repeat("+str(n_av)+"){\n     setTrigger(1);setTrigger(0);\n     playWave(pulse);\n     waitWave();\n     playZero(i);\n     waitWave();\n     playWave(pulse);\n     waitWave();\n   }\n}"
    return sequence

def make_rabi_sequencer(n_start, n_stop, dn, n_wait, n_av):
    sequence = "cvar i;\nconst n_start="+str(n_start)+";\nconst n_stop="+str(n_stop)+ ";\nconst dn="+str(dn)+";\nconst n_wait="+str(n_wait)+";\n  \nfor (i = n_start; i < n_stop; i = i + dn){\n   repeat("+str(n_av)+"){\n     setTrigger(1);setTrigger(0);\n     playWave(rect(i,1));\n     waitWave();\n     playZero(n_wait);\n     waitWave();\n   }\n}"
    return sequence
