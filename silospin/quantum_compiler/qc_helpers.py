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

def make_gateset_sequencer_fast(n_array, n_seq, continuous=False, trigger=False):
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
    "0": {"x": 1, "y": 1, "xxx": 1, "yyy": 1,  "xx": 8, "yy": 8, "mxxm": 8, "myym": 8},
    "90" : {"x": 2, "y": 2, "xxx": 2, "yyy": 2,  "xx": 9, "yy": 9, "mxxm": 9, "myym": 9},
    "180" : {"x": 3, "y": 3, "xxx": 3, "yyy": 3,  "xx": 10, "yy": 10, "mxxm": 10, "myym":10} ,
    "270": {"x": 4, "y": 4, "xxx": 4, "yyy": 4 ,  "xx": 11, "yy": 11, "mxxm": 11, "myym": 11},
    "-90" : {"x": 5, "y": 5, "xxx": 5, "yyy": 5,  "xx": 12, "yy": 12, "mxxm": 12, "myym": 12},
    "-180" : {"x": 6, "y": 6, "xxx": 6, "yyy": 6,  "xx": 13, "yy": 13, "mxxm": 13, "myym": 13},
    "-270": {"x": 7, "y": 7,  "xxx": 7, "yyy": 7,  "xx": 14, "yy": 14, "mxxm": 14, "myym": 14}}
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
            n_t = ceil(sample_rate*int(t)*(1e-9)/48)*48
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
