def make_command_table(gate_string, iq_settings):
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
    phases = {"x": {"phase0": 0, "phase1": 90} , "y": {"phase0": 90, "phase1": 180},
    "xx": {"phase0": 0, "phase1": 90} , "yy": {"phase0": 90, "phase1": 180},
    "xxx": {"phase0": 360, "phase1": 270} , "yyy": {"phase0": 270 , "phase1": 180} ,
    "mxxm": {"phase0": 360, "phase1": 270} , "myym":  {"phase0": 270, "phase1": 180}}

    idx = 0
    ct = []
    for gt in gate_string:
        #break into 2 cases: playZero = False, playZero = True.
        if gt == "tau":
            waveform = {"length": 10, "playZero": True}
            phase0 = {"value": 0,  "increment": True}
            phase1 = {"value":  0,  "increment": True}
        else:
            waveform = {"index": wave_idx[gt]}
            phase0 = {"value": phases[gt]["phase0"], "increment": True}
            phase1 = {"value": phases[gt]["phase1"]+ iq_settings["iq_offset"], "increment": True}

        ct_entry = {"index": idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
        ct.append(ct_entry)
        idx += 1

    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table
