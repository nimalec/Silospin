from math import ceil
from silospin.math.math_helpers import compute_accumulated_phase

def make_command_table(gate_string, sample_rate, phi_z = 0, del_phi=0):
    ##Need to specify AWG and output channel.
    ## I ==> out = 0 , Q ==> out = 1.
    ## 1: AWG = 0 , out = 0
    ## 2: AWG = 0 , out = 1
    ## 3: AWG = 1 , out = 0
    ## 4 : AWG = 1 , out = 1
    ## 5 : AWG = 2 , out = 0
    ## 6 : AWG = 2 , out = 1
    ## 7 : AWG = 3 , out = 0
    ## 8 : AWG = 3 , out = 1

    dPhid_gt = {"x":  0, "y": 90, "xx":  0, "yy": 90 , "xxx":  180, "yyy": -90, "mxxm": 180, "myym": -90, "p": 0}

    ct_idx = 0
    wv_idx = 0

    ct = []
    Phi_l = 0

    for gt in gate_string:
        #break into 2 cases: playZero = False, playZero = True.
        if gt[0] == "t":
            t = gt[1:4]
            n_t = ceil(sample_rate*int(t)*(1e-9)/48)*48

            waveform = {"playZero": True, "length": n_t}
            #waveform = {"index": idx, "awgChannel0": ["sigout0","sigout1"]}
            phase0 = {"value": 0,  "increment": True}
            phase1 = {"value": 0,  "increment": True}


        else:
            #waveform = {"index": idx, "awgChannel0": ["sigout0","sigout1"]}
            waveform = {"index": wv_idx, "awgChannel0": ["sigout0","sigout1"]}
            dPhi_d = dPhid_gt[gt] + phi_z # WE SHOULD HANDLE PHI_Z SEPARATELY, I THINK AS WRITTEN THINGS WON'T WORK WHEN YOU ADD Z ROTATIONS IN. TO DO A Z WE JUST NEED TO CHECK IF THE GATE IS A Z AND IF SO WE JUST IMMEDIATELY APPLY AN INCREMENT BY THE APPROPRIATE VALUE. YOU SHOULDN'T NEED TO TRACK THE PHASE IN THAT CASE. I.E. Z GATE = A ROTATION OF THE REFERENCE FRAME.
            dPhi_a = dPhi_d - Phi_l
            Phi_l = Phi_l + dPhi_a # WHY NOT Phi_l = dPhi_d ? it may be a bit more transparent what you're doing/what the phi's mean
            #if idx == 0:
            if ct_idx == 0:
                phase0 = {"value": dPhi_a+del_phi, "increment": False}
                phase1 = {"value": dPhi_a+90+del_phi, "increment": False}
            else:
                phase0 = {"value": dPhi_a, "increment": True}
                phase1 = {"value": dPhi_a, "increment": True}
            wv_idx += 1

        ct_entry = {"index": ct_idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
        ct.append(ct_entry)
        ct_idx += 1

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct} # eventually (after the code is in a better state), we want to remove any online resources... the code should run with the computer not connected to the internet. I know this is taken directly from ZI and works, but we'll want to make things more robust.
    return command_table

def make_gateset_sequencer(n_array, n_seq, continuous=False, trigger=False):
    ##Input: n_array. List of lengths for each gate operation.
    idx = 0
    sequence_code = ""
    command_code = ""
    for n in n_array:
        n_str = str(n)
        idx_str = str(idx)
        line = "assignWaveIndex(placeholder("+n_str+"),"+idx_str+");\n"
        sequence_code = sequence_code + line
        idx+=1
    sequnce_code = sequence_code
    ##Replace n_array  for command table with ct indices instead
    #idx = 0
    for n in range(n_seq):
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n";
        command_code = command_code + line

    if continuous is True:
        if trigger is False:
            program = sequence_code + "while(true){\n" + command_code +"}\n"
        else:
            program = sequence_code + "while(true){\n  setTrigger(1);\n setTrigger(0);\n" + command_code +"}\n"

    else:
        if trigger is False:
            program = sequence_code + command_code
        else:
            program = sequence_code + "setTrigger(1);\n setTrigger(0);\n" + command_code

    return program

def make_gateset_sequencer_fast(n_array, n_seq, continuous=False, soft_trigger=False, hard_trigger=False):
    ##Input: n_array. List of lengths for each gate operation.
    idx = 0
    sequence_code = ""
    command_code = "executeTableEntry("+str(0)+");\n"
    for n in n_array:
        n_str = str(n)
        idx_str = str(idx)
        line = "assignWaveIndex(placeholder("+n_str+"),"+idx_str+");\n"
        sequence_code = sequence_code + line
        idx+=1
    sequnce_code = sequence_code

    ##Replace n_array  for command table with ct indices instead
    #idx = 0
    for n in n_seq:
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n";
        command_code = command_code + line

    if continuous is True:
        if soft_trigger is False:
            program = sequence_code + "while(true){\n" + command_code +"}\n"
        else:
            program = sequence_code + "while(true){\n setTrigger(1);\n setTrigger(0);\n" + command_code +"}\n"

    else:
        if hard_trigger is True:
            program = sequence_code + "waitDigTrigger(1);\n setDIO(1);\n wait(2);\nsetDIO(0);\nwaitDIOTrigger();\n" + command_code
        elif soft_trigger is True:
            program = sequence_code + "setTrigger(1);\nsetTrigger(0);\n" + command_code
    return program

def make_gateset_sequencer_fast_v2(line_idx, n_seq):
    command_code = "executeTableEntry("+str(line_idx)+");\n"
    for n in n_seq:
        idx_str = str(n)
        line = "executeTableEntry("+idx_str+");\n"
        command_code = command_code + line
    program = "setTrigger(1);\nsetTrigger(0);\n" + command_code
    return program


def generate_reduced_command_table(gt_0, npoints_wait = [], npoints_plunger = None, delta_iq = 0, phi_z = 0):
    ## also add I/Q correction here

    ## npoints_wait: list of number of points for various wait durations
    ## phi_z: phase correction
    ## Note: assumes wv_idx = 0 corresponds to tau_pi_2, wv_idx_2 correspodns to pi
    ## ct_idx = 0 ==> start command table entry
    ## ct_idx = 1-7 ==> pi_2 pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 8-14 ==> pi pulses
    ## ct_idx = 15-21 ==> z gates
    ## ct_idx = 22 - N ==> waits
    ## ct_idx = N+1 - M ==> plunger gates

    ##Add plunger, wait to initial gates
    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": 90, "wave_idx": 0}, "xxx": {"phi": 180, "wave_idx": 0}, "yyy": {"phi": -90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": 90, "wave_idx": 1}, "mxxm": {"phi": 180, "wave_idx": 1}, "myym": {"phi": -90, "wave_idx": 1}}

    ct = []
    n_phases = 7

    waveform_0 = {"index": initial_gates[gt_0]["wave_idx"], "awgChannel0": ["sigout0","sigout1"]}
    phase_0_0 = {"value": initial_gates[gt_0]["phi"], "increment": False}
    phase_1_0 = {"value": initial_gates[gt_0]["phi"]+delta_iq+90, "increment": False}
    ct_entry_0 = {"index": 0, "waveform": waveform_0, "phase0": phase_0_0, "phase1": phase_1_0}
    ct.append(ct_entry_0)

    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}]
    phases = [{"value": 0, "increment": True}, {"value": 90, "increment": True}, {"value": 180, "increment": True}, {"value": 270, "increment": True}, {"value": -90, "increment": True},  {"value": -180, "increment": True},{"value": -270, "increment": True}]

    ct_idx = 1
    for i in range(n_phases):
        ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1
    ct_idx = 7
    for i in range(n_phases):
        ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1
    ct_idx = 14
    for i in range(n_phases):
        ct.append({"index": ct_idx, "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1

    if len(npoints_wait) > 0:
        ct_idx = 21
        for n_t in npoints_wait:
            ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_t}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def generate_reduced_command_table_v2(gts_0, npoints_wait = [], npoints_plunger = None, delta_iq = 0, phi_z = 0, sample_rate=2.4e9):
    ## also add I/Q correction here

    ## npoints_wait: list of number of points for various wait durations
    ## phi_z: phase correction
    ## Note: assumes wv_idx = 0 corresponds to tau_pi_2, wv_idx_2 correspodns to pi
    ## ct_idx = 0-N ==> number of
    ## ct_idx = 1-7 ==> pi_2 pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 8-14 ==> pi pulses
    ## ct_idx = 15-21 ==> z gates
    ## ct_idx = 22 - N ==> waits
    ## ct_idx = N+1 - M ==> plunger gates

    ##Add plunger, wait to initial gates
    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": 90, "wave_idx": 0}, "xxx": {"phi": 180, "wave_idx": 0}, "yyy": {"phi": -90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": 90, "wave_idx": 1}, "mxxm": {"phi": 180, "wave_idx": 1}, "myym": {"phi": -90, "wave_idx": 1}}

    ct = []
    n_phases = 7

    idx = 0
    for gt in gts_0:
        if gt in initial_gates:
             waveform_0 = {"index": initial_gates[gt]["wave_idx"], "awgChannel0": ["sigout0","sigout1"]}
             phase_0_0 = {"value": initial_gates[gt]["phi"], "increment": False}
             phase_1_0 = {"value": initial_gates[gt]["phi"]+delta_iq+90, "increment": False}
             ct_entry_0 = {"index": idx, "waveform": waveform_0, "phase0": phase_0_0, "phase1": phase_1_0}
             ct.append(ct_entry_0)
        elif gt[0] == "t":
             n_t = ceil(sample_rate*int(gt[1:len(gt)])/32)*32
             waveform_0 = {"playZero": True, "length": n_t}
             phase_0_0 = {"value": 0 , "increment": False}
             ct_entry_0 = {"index": idx, "waveform": waveform_0, "phase0": phase_0_0, "phase1": phase_0_0}
             ct.append(ct_entry_0)
        idx += 1

    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}]
    phases = [{"value": 0, "increment": True}, {"value": 90, "increment": True}, {"value": 180, "increment": True}, {"value": 270, "increment": True}, {"value": -90, "increment": True},  {"value": -180, "increment": True},{"value": -270, "increment": True}]

    ct_idx = idx + 1
    for i in range(n_phases):
        ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1
    ct_idx = ct_idx + 1
    for i in range(n_phases):
        ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1
    ct_idx = ct_idx +1
    for i in range(n_phases):
        ct.append({"index": ct_idx, "phase0": phases[i], "phase1": phases[i]})
        ct_idx += 1

    if len(npoints_wait) > 0:
        ct_idx = ct_idx +1
        for n_t in npoints_wait:
            ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_t}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def generate_reduced_command_table_v3(n_pi_2, n_pi):
    ##Note: very simplified. Does not include Z, plungers, and edge cases for combo of pi and pi/2 pulses.
    ## ct_idx = 0-7 ==> initial gates
    ## ct_idx = 8-14 ==> pi_2 pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 15-22 ==> pi pulses (0,90, 180, 270, -90, -180, -270)
    ## ct_idx = 23 - 25 ==> standard pulse delays

    initial_gates = {"x": {"phi": 0, "wave_idx": 0}, "y": {"phi": 90, "wave_idx": 0}, "xxx": {"phi": 180, "wave_idx": 0}, "yyy": {"phi": -90, "wave_idx": 0}, "xx": {"phi": 0, "wave_idx": 1}, "yy": {"phi": 90, "wave_idx": 1}, "mxxm": {"phi": 180, "wave_idx": 1}, "myym": {"phi": -90, "wave_idx": 1}}
    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]}]
    #Initial phases
    phases_0_I = [{"value": 0}, {"value": 90}, {"value": 180}, {"value": -90}]
    phases_0_Q = [{"value": 90}, {"value": 180}, {"value": 270}, {"value": 0}]
    #Incremented phases
    phases_incr = [{"value": 0, "increment": True}, {"value": 90, "increment": True}, {"value": 180, "increment": True}, {"value": 270, "increment": True}, {"value": -90, "increment": True},  {"value": -180, "increment": True},{"value": -270, "increment": True}]

    ## 1. Loop through initial gates
    ct_idx = 0
    for i in range(len(phases_0_I)):
        ## pi/2 lengths
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1
    for i in range(len(phases_0_I)):
        ## pi lengths
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
         ct_idx += 1

    ## 2. Loop through incremented phases
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1
    for i in range(len(phases_incr)):
         ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_incr[i], "phase1": phases_incr[i]})
         ct_idx += 1

   ## 3. Append waits to command table
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct.append({"index": ct_idx+1, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def make_waveform_placeholders(n_array):
    ##Input: n_array. List of lengths for each gate operation.
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

def make_command_table_idxs(gt_seq, sample_rate):
    ct_idxs = []
    n_ts = []
    waits = {}
    phi_l = 0
    ct_idx_t = 21
    for gt in gt_seq:
        if gt[0] in {"x" , "y", "m"}:
            phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
            ct_idx = get_ct_idx(phi_a, gt)
        elif gt[0] == "t":
            n_t = ceil(sample_rate*int(gt[1:len(gt)])*(1e-9)/48)*48
            if n_t in waits:
                ct_idx = waits[str(n_t)]
            else:
                waits[str(n_t)] = ct_idx_t
                ct_idx = ct_idx_t
                n_ts.append(n_t)
                ct_idx_t += 1
        else:
            pass
        ct_idxs.append(ct_idx)
    return ct_idxs, n_ts

def make_command_table_idxs_v2(n_gt0, n_t_t, gt_seq, sample_rate):
    ct_idxs = []
    n_ts = []
    waits = {}
    phi_l = 0
    ct_idx_t = 21 + n_gt0 + n_t_t
    for gt in gt_seq:
        if gt[0] in {"x" , "y", "m"}:
            phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
            ct_idx = get_ct_idx(phi_a, gt)
        elif gt[0] == "t":
            n_t = ceil(sample_rate*int(gt[1:len(gt)])*(1e-9)/48)*48
            if n_t in waits:
                ct_idx = waits[str(n_t)]
            else:
                waits[str(n_t)] = ct_idx_t
                ct_idx = ct_idx_t
                n_ts.append(n_t)
                ct_idx_t += 1
        else:
            pass
        ct_idxs.append(ct_idx)
    return ct_idxs, n_ts

def make_command_table_idxs_v3(gt_seq, tau_pi_s, tau_pi_2_s):
    ct_idxs = []
    phi_l = 0
    for gt in gt_seq:
        if gt[0] in {"x", "y", "m"}:
            phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
            ct_idx = get_ct_idx(phi_a, gt) ## need to edit
        elif gt[0] == "t":
            if int(gt[1:len(gt)]) == tau_pi_2_s:
                ct_idx = 22
            elif int(gt[1:len(gt)]) == tau_pi_s:
                ct_idx = 23
            else:
                pass
        ct_idxs.append(ct_idx)
    return ct_idxs

def make_command_table_idxs_v4(gt_seqs, tau_pi_s, tau_pi_2_s):
    ct_idxs = {}
    initial_gates = {"x": 0, "y": 1,  "xx": 4,  "yy": 5, "xxx": 2, "yyy": 3,  "mxxm": 5,  "myym": 7}
    for idx in gt_seqs
        gate_sequence = gt_seqs[idx]
        ct_idx_list = []
        ii = 0
        for gt in gate_sequence:
            if ii == 0:
                if gt in {"x", "y", "xxx", "yyy"}:
                    ct_idx_list.append(22)
                    ct_idx_list.append(initial_gates[gt])
                    ct_idx_list.append(22)
                elif gt in {"xx", "yy", "mxxm", "myym"}:
                    ct_idx_list.append(23)
                    ct_idx_list.append(initial_gates[gt])
                    ct_idx_list.append(23)
                elif gt[0] == "t":
                    if int(gt[1:len(gt)]) == tau_pi_2_s:
                        ct_idx_list.append(22)
                        ct_idx_list.append(22)
                        ct_idx_list.append(22)
                    elif int(gt[1:len(gt)]) == tau_pi_s:
                        ct_idx_list.append(23)
                        ct_idx_list.append(23)
                        ct_idx_list.append(23)
                    else:
                        pass
                else:
                    pass
            else:
                phi_l = 0
                if gt[0] in {"x", "y", "m"}:
                    phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
                    ct_idx = get_ct_idx(phi_a, gt)
                    if gt in {"x", "y", "xxx", "yyy"}:
                        ct_idx_list.append(22)
                        ct_idx_list.append(ct_idx)
                        ct_idx_list.append(22)
                    else:
                        ct_idx_list.append(23)
                        ct_idx_list.append(ct_idx)
                        ct_idx_list.append(23)
                elif gt[0] == "t":
                    if int(gt[1:len(gt)]) == tau_pi_2_s:
                        ct_idx = 22
                    elif int(gt[1:len(gt)]) == tau_pi_s:
                        ct_idx = 23
                    ct_idx_list.append(ct_idx)
                    ct_idx_list.append(ct_idx)
                    ct_idx_list.append(ct_idx)
                else:
                    pass
            ii += 1
            ct_idxs[idx] = ct_idx_list
    return ct_idxs

#def generate_waveforms(qubit_gate_lengths):
    #returns pi and pi/2 waveforms for each qubit\
