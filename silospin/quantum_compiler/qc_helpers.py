from math import ceil

def make_command_table(gate_string, iq_settings, sample_rate, phi_z = 0):
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

    ##X, Y, XXX, YYY  :  wave_idx = 0 (tau = tau_0)
    ##XX, YY, mXXm, mYYm :  wave_idx = 1 (tau = tau_1) (XX = mXm)
    wave_idx = {"x": 0, "y": 0, "xx": 1, "yy": 1, "xxx": 0, "yyy": 0, "mxxm": 1, "myym": 1}
    dPhid_gt = {"x":  0, "y": 90, "xx":  0, "yy": 90 , "xxx":  360, "yyy": 270, "mxxm":  360, "myym": 270}


    idx = 0
    ct = []
    for gt in gate_string:
        #break into 2 cases: playZero = False, playZero = True.
        if gt[0] == "t":
            t = gt[1:4]
            n_t = ceil(sample_rate*int(t)*(1e-9)/32)*32
            waveform = {"length": n_t, "playZero": True}
            phase0 = {"value": 0,  "increment": True}
            phase1 = {"value":  0,  "increment": True}

        else:
            waveform = {"index": wave_idx[gt], "awgChannel0": ["sigout0","sigout1"]}
            dPhi_d = dPhid_gt[gt] + phi_z
            dPhi_a = dPhi_d - dPhi_l
            phase0 = {"value": dPhi_a, "increment": True}
            phase1 = {"value": dPhi_a + 90, "increment": True}
            dPhi_l = dPhi_a


        ct_entry = {"index": idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
        ct.append(ct_entry)
        idx += 1

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def make_gateset_sequencer(n_array, continuous=False):
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
    idx = 0
    for n in n_array:
        idx_str = str(idx)
        line = "executeTableEntry("+idx_str+");\n";
        command_code = command_code + line
        idx+=1

    if continuous is True:
        program = sequence_code + "while(true){\n" + command_code +"}\n"
    else:
        program = sequence_code + command_code
    return program
