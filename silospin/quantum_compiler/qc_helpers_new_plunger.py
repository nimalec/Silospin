from math import ceil
from silospin.math.math_helpers import compute_accumulated_phase, rectangular

def make_command_table_idxs_rf_p_v0(gt_seqs, taus_std, taus_p, n_arbZ):
    ##Use this one!!
    ##RF gates
    #0-3: pi (pi_fr) [xx, yy, mxxm, myym]
    #4-7: pi/2 (pi/2_fr) [x, y, xxx, yyy]
    #8-11: pi/2 (pi_fr) f[x, y, xxx, yyy]
    #12-18: pi (pi_fr) [0, 90, 180, 270, -90, -180, -270]
    #19-25: pi/2 (pi/2_fr) [0, 90, 180, 270, -90, -180, -270]
    #26-27: pi/2 (pi/2_fr) [0, 90, 180, 270, -90, -180, -270]

    #Args:
    ## gt_seq ==> gate sequence obtained after parsing
    ## taus_std ==> standard pulse durations (pi/2, pi)
    ## taus_p ==> list of tuples [(idx, tau_p) ] with idx as command table index and tau_p as corresponding duration
    ##n_arbZ ==> list of arb Z indices
    #Ouptuts:
    # ct_idxs
    # nArbz

    arbZ = [] #output: list of arbZ tuples
    #ct_idxs: outer loop = 'rf' or 'plunger'. inner_loop = AWG cores.
    ct_idxs = {'rf': {}, 'plunger': {}} #command table indices
    #mapping of initial gate type to CT index
    initial_gates = {'xx_pi_fr': 0, 'yy_pi_fr': 1, 'mxxm_pi_fr': 2, 'myym_pi_fr': 3, 'x_pi2_fr': 4, 'y_pi2_fr': 5, 'xxx_pi2_fr': 6, 'yyy_pi2_fr': 7, 'x_pi_fr': 8, 'y_pi_fr':  9, 'xxx_pi_fr':  10, 'yyy_pi_fr': 11}
    #mapping from  pi (pi_fr) incremental angle to ct indx
    ct_idx_incr_pi_pi_fr = {0: 12, -90: 13, -180: 14, -270: 15, 90: 16, 180: 17,  270:  18}
    #mapping from  pi_2 (pi_2_fr) incremental angle to ct indx
    ct_idx_incr_pi_2_pi_2_fr = {0: 19, -90: 20, -180: 21, -270: 22, 90: 23, 180: 24,  270: 25}
    #mapping from  pi_2 (pi_fr) incremental angle to ct indx
    ct_idx_incr_pi_2_pi_fr = {0: 26, -90: 27, -180: 28, -270: 29, 90: 30, 180: 31,  270: 32}

    #mapping from gate type to pahse angle
    phi_ls_gt = {'x':  0, 'y': -90, 'xx':  0, 'yy': -90 , 'xxx':  -180, 'yyy': 90, 'mxxm': -180, 'myym': 90}

    #group pi and pi/2 gate sets
    pi_gt_set = {'xx', 'yy', 'mxxm', 'myym'}
    pi_2_gt_set = {'x', 'y', 'xxx', 'yyy'}
    #Number of plunger gates
    N_p = len(taus_p)

    #Arb Z counter
    arbZ_counter = 36 + N_p + n_arbZ

#     ##populate dict with t_waits
#     #2 types of pulse delays: rf and plunger.
#     ## rf delays: tau_pi and tau_pi_2
#     ## plunger delays: populate from taus_p
#     ## Extract mapping from taus_p to ct_idx

    ##Populates dictionnary of taus (33 - 33 + N_p)
    taus_ct_idxs = {'rf': {'pi2': {'tau_pi2': taus_std[0], 'ct_idx': 33 }, 'pi': {'tau_pi': taus_std[1], 'ct_idx':  34} }, 'plunger': {}}
    idx = 1
    for item in taus_p:
        #taus_ct_idxs['plunger'][str(idx)] = {'tau_p': item[1] , 'ct_idx': 34+idx}
        taus_ct_idxs['plunger'][item[0]] = {'tau_p': item[1] , 'ct_idx': 34+idx}
        idx += 1

    ##CT idxs grouped for each  gate type ('rf' and 'p') and plunger gate (need not worry about core index here)
    rf_gate_sequence = gt_seqs['rf']
    plunger_gate_sequence = gt_seqs['plunger']
    #Case I: RF gates
    #Loops over RF cores and populates rf_ct_idxs with lists of CT idxs for each core
    rf_ct_idxs = {}
    for rf_idx in rf_gate_sequence:
        #For a single AWG core ==> populate a list with CT idxs
        rf_ct_idxs[rf_idx] = []
        rf_ct_idx_list = []

        #Intersection of indices between differnet cores
        rf_diff_idxs = list(set([i for i in rf_gate_sequence.keys()]).difference(rf_idx))

        #List of gate for a single core
        gate_sequence = rf_gate_sequence[rf_idx]
        n_gates = len(gate_sequence)

        ##Initializes phase for first gate of each sequence
        gt_0 = gate_sequence[0]
        if gt_0[0] in  {"x", "y", "m"}:
            phi_l = phi_ls_gt[gt_0]
        else:
            phi_l = 0

        #Loop over list of gates
        for idx in range(n_gates):
            gt = gate_sequence[idx]
            rf_gates_other = set([rf_gate_sequence[j][idx] for j in rf_diff_idxs])
            pi_2_intersect = rf_gates_other.intersection(pi_2_gt_set)
            pi_intersect = rf_gates_other.intersection(pi_gt_set)

            ##Case A: Initial gates of sequence
            if idx == 0:
               # 1. Case 1: xx, yy, mxxm, myym [pi (pi_fr)]
                if gt in pi_gt_set:
                    gt_str = gt+'_pi_fr'
                    rf_ct_idx_list.append(initial_gates[gt_str])

                #2. Case 2: pi/2 gates
                elif gt in pi_2_gt_set:
                    if len(pi_intersect)>0:
                        ##work in pi frame
                        gt_str = gt+'_pi_fr'
                        rf_ct_idx_list.append(initial_gates[gt_str])
                    else:
                        ##work in pi/2 frame
                        gt_str = gt+'_pi2_fr'
                        rf_ct_idx_list.append(initial_gates[gt_str])

                #3. Case 3: wait is present
                elif gt[0] == 't':
                    #Gets duration for single gate s
                    gt_t_str = int(gt[1:len(gt)])
                    #Checks if duration corresponds to pi/2 pulse duration
                    if gt_t_str == taus_std[0]:
                        ##assign ct index 33 if pi/2
                        rf_ct_idx_list.append(33)
                    elif gt_t_str == taus_std[1]:
                        ##assign ct index 34 if pi/2
                        rf_ct_idx_list.append(34)
                    else:
                        ##last case, check if wait corresponds to a plunger gate
                        for item in taus_ct_idxs['plunger']:
                            ##if corresponds to any plunger gate duration ==> assgn correspondig ct index (35 <= ct_idx <= 35 + N_p)
                            if gt_t_str == taus_ct_idxs['plunger'][item]['tau_p']:
                                rf_ct_idx_list.append(taus_ct_idxs['plunger'][item]['ct_idx'])
                            else:
                                continue

                #4  Case 4: Z gate is present
                elif gt[0] == 'z':
                    z_angle = float(gt[1:len((gt))-1])
                    if int(z_angle) == 0:
                        z0_idx = 35+ N_p
                        rf_ct_idx_list.append(z0_idx)
                    else:
                        rf_ct_idx_list.append(arbZ_counter)
                        arbZ.append((arbZ_counter, -z_angle))
                else:
                    pass

            # ##Case B : Following gates
            #For each conditional (pi and pi/2 gates in case 1 and case 2 ==> compute phase and determne CT entry)
            else:
                if gt[0] in {"x", "y", "m"}:
                    phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
                else:
                    pass

             # 1. Case 1: xx, yy, mxxm, myym [pi (pi_fr)]
                if gt in pi_gt_set:
                    rf_ct_idx_list.append(ct_idx_incr_pi_pi_fr[phi_a])

                #2. Case 2: pi/2 gates
                elif gt in pi_2_gt_set:
                    if len(pi_intersect)>0:
                        ##work in pi frame
                        rf_ct_idx_list.append(ct_idx_incr_pi_2_pi_fr[phi_a])
                    else:
                        ##work in pi/2 frame
                        rf_ct_idx_list.append(ct_idx_incr_pi_2_pi_2_fr[phi_a])

                #3. Case 3: wait is present
                ##Need not change
                elif gt[0] == 't':
                    #Gets duration for single gate s
                    gt_t_str = int(gt[1:len(gt)])
                    #Checks if duration corresponds to pi/2 pulse duration
                    if gt_t_str == taus_std[0]:
                        ##assign ct index 33 if pi/2
                        rf_ct_idx_list.append(33)
                    elif gt_t_str == taus_std[1]:
                        ##assign ct index 34 if pi/2
                        rf_ct_idx_list.append(34)
                    else:
                        ##last case, check if wait corresponds to a plunger gate
                        for item in taus_ct_idxs['plunger']:
                            ##if corresponds to any plunger gate duration ==> assgn correspondig ct index (35 <= ct_idx <= 35 + N_p)
                            if gt_t_str == taus_ct_idxs['plunger'][item]['tau_p']:
                                rf_ct_idx_list.append(taus_ct_idxs['plunger'][item]['ct_idx'])
                            else:
                                continue
                #4  Case 4: Z gate is present
                elif gt[0] == 'z':
                    ##need not change
                    z_angle = float(gt[1:len((gt))-1])
                    if int(z_angle) == 0:
                        z0_idx = 35 + N_p
                        rf_ct_idx_list.append(z0_idx)
                    else:
                        rf_ct_idx_list.append(arbZ_counter)
                        arbZ.append((arbZ_counter, -z_angle))
                else:
                    pass
        rf_ct_idxs[rf_idx] = rf_ct_idx_list

    ct_idxs['rf'] = rf_ct_idxs
    ##START HERE!!!!
    ##Start populating plunger ct indices

    ##Case II: plunger command table indices
    plunger_ct_idxs = {}
    ##Loops over plunger gate channels in plunger gate seqeunce
    for p_idx in plunger_gate_sequence:
        ##Deine a list to append to ==> plunger gate CT indices
        plunger_ct_idxs[p_idx] = []
        p_ct_idx_list = []
        ##Other plunger channels present
        p_diff_idxs = list(set([i for i in plunger_gate_sequence.keys()]).difference(p_idx))

        rf_diff_idxs = list([i for i in rf_gate_sequence.keys()])

        gate_sequence = plunger_gate_sequence[p_idx]
        n_gates = len(gate_sequence)

        for idx in range(n_gates):
            gt = gate_sequence[idx]
            p_gates_other = set([plunger_gate_sequence[j][idx] for j in p_diff_idxs])
            rf_gates_other = set([rf_gate_sequence[j][idx] for j in rf_diff_idxs])

            pi_intersect = rf_gates_other.intersection(pi_gt_set)
            pi_2_intersect = rf_gates_other.intersection(pi_2_gt_set)

            #Case A: Z gate is present
            if gt[0] == 'z':
                p_ct_idx_list.append(12)

           ## p gate is present
            elif gt == 'p':
                ##p is present, no other DC gates
                if list(p_gates_other)[0][0] == 't':
                    ##p is present, no other DC gates, no other rf gates
                    if len(pi_intersect) == 0 and len(pi_2_intersect) == 0:
                        if p_idx == '6':
                            p_ct_idx_list.append(0)
                        else:
                            p_ct_idx_list.append(1)
                else:
                    pass

                if len(pi_intersect) != 0:
                    ##other pi gates are present
                    if p_idx == '7':
                        p_ct_idx_list.append(6)
                    else:
                        p_ct_idx_list.append(7)

                elif len(pi_2_intersect) != 0 and len(pi_intersect) == 0:
                    ##other pi/2 gates are present
                    if p_idx == '7':
                       p_ct_idx_list.append(4)
                    else:
                       p_ct_idx_list.append(5)

                if list(p_gates_other)[0] == 'p':
                    if p_idx == '7':
                       p_ct_idx_list.append(2)
                    else:
                       p_ct_idx_list.append(3)

            ##If a delay is present
            elif gt[0] == 't':
                gt_t_str = int(gt[1:len(gt)])
                #Checks if duration corresponds to pi/2 pulse duration
                if gt_t_str == taus_std[0]:
                    p_ct_idx_list.append(8)
                elif gt_t_str == taus_std[1]:
                    p_ct_idx_list.append(9)
                else:
                    if p_idx == '7':
                        p_ct_idx_list.append(11)
                    else:
                        p_ct_idx_list.append(10)
            else:
                pass
            plunger_ct_idxs[p_idx] = p_ct_idx_list
    ct_idxs['plunger'] = plunger_ct_idxs
    return ct_idxs, arbZ


def generate_reduced_command_table_rf_core_v0(n_pi_2, n_pi, n_p=[], arbZ=[]):
    ##Use this one!!!!

    ##NCommand table index mappings
    #0-3: pi (pi_fr) [xx, yy, mxxm, myym]
    #4-7: pi/2 (pi/2_fr) [x, y, xxx, yyy]
    #8-11: pi/2 (pi_fr) [x, y, xxx, yyy]
    #12-18: pi (pi_fr) [0, 90, 180, 270, -90, -180, -270]
    #19-25: pi/2 (pi/2_fr) [0, 90, 180, 270, -90, -180, -270]
    #26-32: pi/2 (pi_fr) [0, 90, 180, 270, -90, -180, -270]
    #33-33+N_rf+N_p: delays for RF and plunger gates (N_rf = 2 (std pi and pi_2 durations) followed by N_p (number of plunger gates))
    ##33+N_rf+N_p-33+N_rf+N_p+N_z0 +N_z (N_z0 = 1 (0 phase increment) , followed by cdall given phase increments )
    ##33+N_rf+N_p+N_z0 +N_z - 33+N_rf+N_p+N_z0 +N_z + N_arb (arbitrary RF pulses)

    ct = []
    initial_gates = {"xx_pi_fr": {"phi": 0, "wave_idx": 0}, "yy_pi_fr": {"phi": -90, "wave_idx": 0}, "mxxm_pi_fr": {"phi": -180, "wave_idx": 0}, "myym_pi_fr": {"phi": 90, "wave_idx": 0},  "x_pi_2_fr": {"phi": 0, "wave_idx": 1},  "y_pi_2_fr": {"phi": -90, "wave_idx": 1},  "xxx_pi_2_fr": {"phi": -180, "wave_idx": 1},  "yyy_pi_2_fr": {"phi": 90, "wave_idx": 1},  "x_pi_fr": {"phi": 0, "wave_idx": 2},  "y_pi_fr": {"phi": -90, "wave_idx": 2},  "xxx_pi_fr": {"phi": -180, "wave_idx": 2},  "yyy_pi_fr": {"phi": 90, "wave_idx": 2}}
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]},  {"index": 2, "awgChannel0": ["sigout0","sigout1"]}]
    phases_0_I = [{"value": 0}, {"value": -90}, {"value": -180}, {"value": 90}]
    phases_0_Q = [{"value": -90}, {"value": -180}, {"value": -270}, {"value": 0}]
    phases_incr = [{"value": 0, "increment": True}, {"value": -90, "increment": True}, {"value": -180, "increment": True}, {"value": -270, "increment": True}, {"value": 90, "increment": True},  {"value": 180, "increment": True},{"value": 270, "increment": True}]

    ct_idx = 0
    #Generate initial gates
    #pi i n pi frame
    for i in range(len(phases_0_I)):
          ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
          ct_idx += 1
    #pi/2 in pi/2 frame
    for i in range(len(phases_0_I)):
          ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
          ct_idx += 1
    #pi/2 in pi frame
    for i in range(len(phases_0_I)):
          ct.append({"index": ct_idx, "waveform": waves[2], "phase0": phases_0_I[i], "phase1": phases_0_Q[i]})
          ct_idx += 1

    #Generate phase incremented gates.
     #pi i n pi frame
    for i in range(len(phases_incr)):
          ct.append({"index": ct_idx, "waveform": waves[0], "phase0": phases_incr[i], "phase1": phases_incr[i]})
          ct_idx += 1

    #pi/2 in pi/2 frame
    for i in range(len(phases_incr)):
          ct.append({"index": ct_idx, "waveform": waves[1], "phase0": phases_incr[i], "phase1": phases_incr[i]})
          ct_idx += 1

    #pi/2 in pi frame
    for i in range(len(phases_incr)):
          ct.append({"index": ct_idx, "waveform": waves[2], "phase0": phases_incr[i], "phase1": phases_incr[i]})
          ct_idx += 1

    #Delays for RF pulses
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1

    #ct_idx = 33 at this point

    #Delays from plunger gates
    if len(n_p)==0:
        pass
    else:
        for item in n_p:
            ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": item}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1
    ##ct_idx = 34+n_p at this point
    #Adds Z 0 rotation
    ct.append({"index": ct_idx, "phase0": {"value": 0, "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    #ct_idx = 35+n_p at this point
    if len(arbZ) == 0:
        pass
    else:
        for item in arbZ:
            ct.append({"index": item[0], "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})
   #ct_idx = 37+n_p+n_z at this point
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def generate_reduced_command_table_p_core_v0(n_p, n_pi_2, n_pi):
    ##n_p is a list of tuples of availbile plunger gate lengths [(idx,n_p)] with idx as the GST index and n_p as the corresponding gate length
    ##Command table index mappings
    #0-1: p_i (p_i_fr) [channels 1 and 2 of AWG core] (used for only serial plunger gates)
    #2-3:  p_i (p_j_fr) [chanels 1 and 2 of AWG core, defined wrt to standard p pulse] (used for parallel p pulses)
    #4-5: p_i (p_i in rf pi/2 frame)  [chanels 1 and 2 of AWG core, defined wrt to standard pi/2 pulse] (used for p pulses in parallel with pi/2 pulses [no pi])
    #6-7: p_i (p_i in rf pi frame)  [chanels 1 and 2 of AWG core, defined wrt to standard pi pulse] (used for p pulses in parallel with pi pulses)
    #8: 0 degree phase shift2
    #9: standard pi delay
    #10: standard pi/2 delay
    #11-11+n_p: plunger delays

    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0"]}, {"index": 1, "awgChannel1": ["sigout1"]},  {"index": 2, "awgChannel0": ["sigout0"]}, {"index": 3, "awgChannel1": ["sigout1"]} ,  {"index": 4, "awgChannel0": ["sigout0"]}, {"index": 5, "awgChannel1": ["sigout1"]},  {"index": 6, "awgChannel0": ["sigout0"]}, {"index": 1, "awgChannel1": ["sigout1"]},  {"index": 7, "awgChannel0": ["sigout0"]}, {"index": 8, "awgChannel1": ["sigout1"]}]
    ct_idx = 0

    # p_i (p_i_fr)
    ct.append({"index": ct_idx, "waveform": waves[0]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[1]})
    ct_idx += 1
    #p_i (p_j_fr)
    ct.append({"index": ct_idx, "waveform": waves[2]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[3]})
    ct_idx += 1
    # p_i (p_i in rf pi/2 frame)
    ct.append({"index": ct_idx, "waveform": waves[4]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[5]})
    ct_idx += 1
    # p_i (p_i in rf pi frame)
    ct.append({"index": ct_idx, "waveform": waves[6]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[7]})
    ct_idx += 1
    #0 degree phase shift
    ct.append({"index": ct_idx, "phase0": {"value": 0, "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    #Waits on rf gates (pi and pi/2 gates)
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    #Waits on other plunger gates
    for item in n_p:
        ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": item[1]}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
        ct_idx += 1
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table

def generate_reduced_command_table_p_core_v1(n_p, n_rf):
    ##n_p: list of tuples of idx, plunger durations
    ## n_rf: tuple of standard rf pulse duraiotns
    ## Note: 2 plungers per core
    ## CT indices:
    ## 0 = p_1 (p_1_fr)
    ## 1 = p_2 (p_2_fr)
    ## 2 = p_1 (p_2_fr)
    ## 3 = p_2 (p_1_fr)
    ## 4 = p_1 (pi/2 fr)
    ## 5 = p_2 (pi/2 fr)
    ## 6 = p_1 (pi fr)
    ## 7 = p_2 (pi fr)
    ## 8 = pi/2 wait
    ## 9 = pi wait
    ## 10 = p1 wait
    ## 11 = p2 wait
    ## 12 = 0 degree phase shift
    n_pi_2 = n_rf[0]
    n_pi = n_rf[1]
    ct = []
    waves = [{"index": 0, "awgChannel0": ["sigout0"]}, {"index": 1, "awgChannel1": ["sigout1"]},  {"index": 2, "awgChannel0": ["sigout0"]}, {"index": 3, "awgChannel1": ["sigout1"]} ,  {"index": 4, "awgChannel0": ["sigout0"]}, {"index": 5, "awgChannel1": ["sigout1"]},  {"index": 6, "awgChannel0": ["sigout0"]}, {"index": 7, "awgChannel1": ["sigout1"]}]
    ct_idx = 0
    #p_1 (p_1_fr)
    ct.append({"index": ct_idx, "waveform": waves[0]})
    ct_idx += 1
    #p_2 (p_2_fr)
    ct.append({"index": ct_idx, "waveform": waves[1]})
    ct_idx += 1
    #p_1 (p_2_fr)
    ct.append({"index": ct_idx, "waveform": waves[2]})
    ct_idx += 1
    #p_2 (p_1_fr)
    ct.append({"index": ct_idx, "waveform": waves[3]})
    ct_idx += 1
    #p_1 (pi/2_fr)
    ct.append({"index": ct_idx, "waveform": waves[4]})
    ct_idx += 1
    #p_2 (pi/2_fr)
    ct.append({"index": ct_idx, "waveform": waves[5]})
    ct_idx += 1
    #p_1 (pi_fr)
    ct.append({"index": ct_idx, "waveform": waves[6]})
    ct_idx += 1
    #p_2 (pi_fr)
    ct.append({"index": ct_idx, "waveform": waves[7]})
    ct_idx += 1
    #pi/2 wait
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}})
    ct_idx += 1
    #pi wait
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi}})
    ct_idx += 1
    #p_1 wait
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_p[0][1]}})
    ct_idx += 1
    #p_2 wait
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_p[1][1]}})
    ct_idx += 1
    #Z0 phase increment
    ct.append({"index": ct_idx, "phase0": {"value": 0, "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '0.2'}, 'table': ct}
    return command_table
