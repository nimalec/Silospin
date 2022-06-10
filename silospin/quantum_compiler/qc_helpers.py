from math import ceil

def make_command_table(gate_string, iq_settings, sample_rate, phi_z = 0, del_phi=0):
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

    dPhid_gt = {"x":  0, "y": 90, "xx":  0, "yy": 90 , "xxx":  180, "yyy": -90, "mxxm": 180, "myym": -90}


    #idx = 0

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


        #ct_entry = {"index": idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
        ct_entry = {"index": ct_idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
        ct.append(ct_entry)
    #    idx += 1
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
    idx = 0
    for n in n_seq:
        idx_str = str(idx)
        line = "executeTableEntry("+idx_str+");\n";
        command_code = command_code + line
        idx+=1

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
