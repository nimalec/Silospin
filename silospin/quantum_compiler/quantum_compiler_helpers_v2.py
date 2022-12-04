from math import ceil
from silospin.math.math_helpers import *

def channel_mapper(rf_dc_awg_grouping = {"hdawg1": {"rf":  [1,2,3,4], "dc": []}, "hdawg2":  {"rf": [1], "dc": [2,3,4]}}, trig_channels = {"hdawg1": 1, "hdawg2": 1}):
    '''
    Outputs a dictionary representing the mapping between AWG cores and gate identifiers used by the quantum compiler. \n


    Parameters:
                    rf_dc_awg_grouping (dict): dictionary RF/DC core split. outer key corresponds to HDAWG unit (e.g. "awg1") with values as dictionaries of grouping between RF and DC cores. \n
                    [default set to {"awg1": {"rf":  [1,2,3,4], "dc": []}, "awg2":  {"rf": [1], "dc": [2,3,4]}}\n

    Returns:
       channel_mapper (dict): channel mapping for each core,. each with channel labels "core_idx", "channel_labels", "gate_idx".
    '''
    channel_mapping = {}
    hdawg_mapping = {}
    core_count = 0
    ch_1_idx = -1
    ch_2_idx = 0
    for awg_idx in rf_dc_awg_grouping:
        ch_core_1_idx = -1
        ch_core_2_idx = 0
        channel_mapping[awg_idx] = {1: {}, 2: {}, 3: {}, 4:{}}
        rf_cores = set(rf_dc_awg_grouping[awg_idx]["rf"])
        dc_cores = set(rf_dc_awg_grouping[awg_idx]["dc"])
        for core_idx in channel_mapping[awg_idx]:
            core_count+=1
            ch_1_idx+=2
            ch_2_idx+=2
            ch_core_1_idx += 2
            ch_core_2_idx += 2

            if trig_channels[awg_idx] == ch_core_1_idx:
                trig_in = [1,0]
            elif trig_channels[awg_idx] == ch_core_2_idx:
                trig_in = [0,1]
            else:
                trig_in = [0,0]

            if core_idx in rf_cores:
                rf_dc_awg_grouping[awg_idx]["rf"].append(core_count)
                channel_mapping[awg_idx][core_idx] = {"core_idx": core_count, "channel_core_number":[ch_core_1_idx, ch_core_2_idx], "channel_number":[ch_1_idx, ch_2_idx], "trig_channel": trig_in, "channel_labels":["i"+str(core_count), "q"+str(core_count)],"gate_idx":[core_count,core_count], "rf": 1}
                hdawg_mapping[core_count] = awg_idx
            elif core_idx in dc_cores:
                rf_dc_awg_grouping[awg_idx]["dc"].append(ch_1_idx)
                rf_dc_awg_grouping[awg_idx]["dc"].append(ch_2_idx)
                channel_mapping[awg_idx][core_idx] = {"core_idx": core_count, "channel_core_number":[ch_core_1_idx, ch_core_2_idx], "channel_number":[ch_1_idx, ch_2_idx], "trig_channel": trig_in, "channel_labels":["p"+str(ch_1_idx), "p"+str(ch_2_idx)],"gate_idx":[ch_1_idx,ch_2_idx], "rf": 0}
                hdawg_mapping[ch_1_idx] = awg_idx
                hdawg_mapping[ch_2_idx] = awg_idx
            else:
                pass
    return channel_mapping, hdawg_mapping

def make_gate_parameters(tau_pi, tau_pi_2, i_amp, q_amp, mod_freq, plunger_length, plunger_amp):
    gate_parameters = {}
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

def make_gate_lengths(dc_times, gate_parameters, t_pi_2_max, t_pi_max):
    '''
    Outputs a dictionary with the standard pi, pi/2, and DC pulse lengths in seconds for each gate.

    Parameters:
                    dc_times (dict): dictionary of DC pulse durations for all specified channels, in ns.
                    gate_parameters (dict): dictionary of gate parameters generated by the 'make_gate_parameters' function.
                    t_pi_2_max (float): max pi/2 pulse duration among all qubits, in ns.
                    t_pi_max (float): max pi pulse duration among all qubits, in ns.
    Returns:
       gate_lengths (dict): dictonary of DC an RF gate lengths in ns. Outer dictionary keys are 'rf' and 'plunger'.
    '''
    gate_lengths = {"rf": {}, "plunger": {}}
    for idx in gate_parameters["rf"]:
       t_pi = ceil(t_pi_max)
       t_pi_2 = ceil(t_pi_2_max)
       gate_lengths["rf"][idx] = {"pi": t_pi, "pi_2": t_pi_2}
    for idx in gate_parameters["p"]:
       t_p = ceil(dc_times[idx-1])
       gate_lengths["plunger"][idx] = {"p": t_p}
    return gate_lengths

def make_command_table_indices(gt_seqs, taus_std, taus_p, n_arbZ):
    '''
    Generates a dictionary with lists of command table executions for each core, provided the output of 'gst_file_parser'.
    This is the core of the quantum compiler, as it interprets longs RF and DC gate strings, converting them to FPGA instructions for amplitude and phase modulation.\n
    Outer-most keys "plunger" and "rf", containing instructions to be addressed separatley on the dedicated RF and DC cores.
    Outputs a dictionary with outer keys "rf" and "plunger", corresponding to executions for dedicated RF and DC AWG cores. The values for the "rf" keys are dictionaries with outer keys corresponding to each core and "plunger"
    has values of dictionaries with keys corresponding to each DC channel. Each of these core and channel keys have values of lists of command table (CT) indices (integers) to be addressed on the AWG cores. \n
    Each command table index maps to an entry of a CT, determining the waveform, amplitude, and phase to be played when the CT entry is executed. Phase changes for each gate are computed on-the-fly.
    Note that this function supports the following gates:  'x', 'xxx', 'xx', 'mxxm', 'y', 'yyy', 'y y', 'myym', 'arbZ', 'p', 't'. See 'Quantum Compiler' tab for a more elaborate description.  \n
    Note: this function is currently configured for 1 HDAWG unit with 4 AWG cores. \n

    Parameters:
                    gt_seqs (dict): dictionary output of 'gst_file_parser', representing sequence of RF and DC gate strings on each core.
                    taus_std (list): list of standard pi/2 and pi pulse lengths in ns ([tau_pi2, tau_pi]).
                    taus_p (list): list of tuples, each with elements (ch_idx, tau_p) representing the channel index and corresponding plunger pulse length.
                    n_arbZ (int): the accumulated number of previously seen arbitrary-Z rotations over all lines in GST file being read.

    Returns:
       ct_idxs (dict), arbZ (list): dictonary of command table indices to execute, list of tuples of (arbitrary Z comman table index, rotation angle).
     '''
    arbZ = []
    ct_idxs = {'rf': {}, 'plunger': {}}
    initial_gates = {'xx_pi_fr': 0, 'yy_pi_fr': 1, 'mxxm_pi_fr': 2, 'myym_pi_fr': 3, 'x_pi2_fr': 4, 'y_pi2_fr': 5, 'xxx_pi2_fr': 6, 'yyy_pi2_fr': 7, 'x_pi_fr': 8, 'y_pi_fr':  9, 'xxx_pi_fr':  10, 'yyy_pi_fr': 11}
    ct_idx_incr_pi_pi_fr = {0: 12, -90: 13, -180: 14, -270: 15, 90: 16, 180: 17,  270:  18}
    ct_idx_incr_pi_2_pi_2_fr = {0: 19, -90: 20, -180: 21, -270: 22, 90: 23, 180: 24,  270: 25}
    ct_idx_incr_pi_2_pi_fr = {0: 26, -90: 27, -180: 28, -270: 29, 90: 30, 180: 31,  270: 32}
    phi_ls_gt = {'x':  0, 'y': -90, 'xx':  0, 'yy': -90 , 'xxx':  -180, 'yyy': 90, 'mxxm': -180, 'myym': 90}
    pi_gt_set = {'xx', 'yy', 'mxxm', 'myym'}
    pi_2_gt_set = {'x', 'y', 'xxx', 'yyy'}

    N_p = len(taus_p)
    arbZ_counter = 36 + N_p + n_arbZ
    taus_ct_idxs = {'rf': {'pi2': {'tau_pi2': taus_std[0], 'ct_idx': 33 }, 'pi': {'tau_pi': taus_std[1], 'ct_idx':  34} }, 'plunger': {}}
    idx = 1
    for item in taus_p:
        taus_ct_idxs['plunger'][item[0]] = {'tau_p': item[1] , 'ct_idx': 34+idx}
        idx += 1
    rf_gate_sequence = gt_seqs['rf']
    plunger_gate_sequence = gt_seqs['plunger']

    rf_ct_idxs = {}
    for rf_idx in rf_gate_sequence:
        rf_ct_idxs[rf_idx] = []
        rf_ct_idx_list = []
        rf_diff_idxs = list(set([i for i in rf_gate_sequence.keys()]).difference(rf_idx))
        gate_sequence = rf_gate_sequence[rf_idx]
        n_gates = len(gate_sequence)
        gt_0 = gate_sequence[0]
        if gt_0[0] in  {"x", "y", "m"}:
            phi_l = phi_ls_gt[gt_0]
        else:
            phi_l = 0

        for idx in range(n_gates):
            gt = gate_sequence[idx]
            rf_gates_other = set([rf_gate_sequence[j][idx] for j in rf_diff_idxs])
            pi_2_intersect = rf_gates_other.intersection(pi_2_gt_set)
            pi_intersect = rf_gates_other.intersection(pi_gt_set)

            if idx == 0:
                if gt in pi_gt_set:
                    gt_str = gt+'_pi_fr'
                    rf_ct_idx_list.append(initial_gates[gt_str])

                elif gt in pi_2_gt_set:
                    if len(pi_intersect)>0:
                        gt_str = gt+'_pi_fr'
                        rf_ct_idx_list.append(initial_gates[gt_str])
                    else:
                        gt_str = gt+'_pi2_fr'
                        rf_ct_idx_list.append(initial_gates[gt_str])

                elif gt[0] == 't':
                    gt_t_str = int(gt[1:len(gt)])
                    if gt_t_str == taus_std[0]:
                        rf_ct_idx_list.append(33)
                    elif gt_t_str == taus_std[1]:
                        rf_ct_idx_list.append(34)
                    else:
                        for item in taus_ct_idxs['plunger']:
                            if gt_t_str == taus_ct_idxs['plunger'][item]['tau_p']:
                                rf_ct_idx_list.append(taus_ct_idxs['plunger'][item]['ct_idx'])
                                break
                            else:
                                continue

                elif gt[0] == 'z':
                    z_angle = float(gt[1:len((gt))-1])
                    if int(z_angle) == 0:
                        z0_idx = 35 + N_p
                        rf_ct_idx_list.append(z0_idx)
                    else:
                        rf_ct_idx_list.append(arbZ_counter)
                        arbZ.append((arbZ_counter, -z_angle))
                else:
                    pass
            else:
                if gt[0] in {"x", "y", "m"}:
                    phi_l, phi_a = compute_accumulated_phase(gt, phi_l)
                else:
                    pass
                if gt in pi_gt_set:
                    rf_ct_idx_list.append(ct_idx_incr_pi_pi_fr[-phi_a])

                elif gt in pi_2_gt_set:
                    if len(pi_intersect)>0:
                        rf_ct_idx_list.append(ct_idx_incr_pi_2_pi_fr[-phi_a])
                    else:
                        rf_ct_idx_list.append(ct_idx_incr_pi_2_pi_2_fr[-phi_a])

                elif gt[0] == 't':
                    gt_t_str = int(gt[1:len(gt)])
                    if gt_t_str == taus_std[0]:
                        rf_ct_idx_list.append(33)
                    elif gt_t_str == taus_std[1]:
                        rf_ct_idx_list.append(34)
                    else:
                        for item in taus_ct_idxs['plunger']:
                            if gt_t_str == taus_ct_idxs['plunger'][item]['tau_p']:
                                rf_ct_idx_list.append(taus_ct_idxs['plunger'][item]['ct_idx'])
                                break
                            else:
                                continue

                elif gt[0] == 'z':
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

    plunger_ct_idxs = {}
    for p_idx in plunger_gate_sequence:
        plunger_ct_idxs[p_idx] = []
        p_ct_idx_list = []
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

            if gt[0] == 'z':
                p_ct_idx_list.append(14)
            elif gt == 'p':
                if list(p_gates_other)[0][0] != 'p':
                    if len(pi_intersect) == 0 and len(pi_2_intersect) == 0:
                        if p_idx == '6':
                            p_ct_idx_list.append(0)
                        else:
                            p_ct_idx_list.append(1)

                    elif len(pi_intersect) == 0 and len(pi_2_intersect) != 0:
                        if p_idx == '6':
                            p_ct_idx_list.append(4)
                        else:
                            p_ct_idx_list.append(5)

                    elif len(pi_intersect) != 0:
                        if p_idx == '6':
                            p_ct_idx_list.append(6)
                        else:
                            p_ct_idx_list.append(7)

                elif list(p_gates_other)[0][0] == 'p':
                    if len(pi_intersect) == 0 and len(pi_2_intersect) == 0:
                        p_ct_idx_list.append(2)
                    elif len(pi_intersect) == 0 and len(pi_2_intersect) != 0:
                        p_ct_idx_list.append(8)
                    elif len(pi_intersect) != 0:
                        p_ct_idx_list.append(9)
                else:
                    pass

            elif gt[0] == 't':
                gt_t_str = int(gt[1:len(gt)])
                if gt_t_str == taus_std[0]:
                    p_ct_idx_list.append(10)
                elif gt_t_str == taus_std[1]:
                    p_ct_idx_list.append(11)
                else:
                    if p_idx == '7':
                        p_ct_idx_list.append(12)
                    else:
                        p_ct_idx_list.append(13)
            else:
                pass
            plunger_ct_idxs[p_idx] = p_ct_idx_list

    new_p_gate_lst = []
    for i in range(len(plunger_ct_idxs['6'])):
        if plunger_ct_idxs['6'][i] == plunger_ct_idxs['7'][i]:
            new_p_gate_lst.append(plunger_ct_idxs['6'][i])
        elif plunger_ct_idxs['6'][i] < 10 and  plunger_ct_idxs['7'][i] >= 10:
            new_p_gate_lst.append(plunger_ct_idxs['6'][i])
        elif plunger_ct_idxs['7'][i] < 10 and  plunger_ct_idxs['6'][i] >= 10:
            new_p_gate_lst.append(plunger_ct_idxs['7'][i])
        else:
            pass
    plunger_ct_idxs['6'] = new_p_gate_lst
    plunger_ct_idxs['7'] = new_p_gate_lst
    ct_idxs['plunger'] = plunger_ct_idxs
    return ct_idxs, arbZ

def make_rf_command_table(n_pi_2, n_pi, n_p=[], arbZ=[]):
    '''
    Generates command tables for dedicated RF cores. Each command table index corresponds to a phase increment and waveform play. Command table entries correspond to the following indices:\n
    - 0, initial xx gate in pi frame \n
    - 1, initial yy gate in pi frame\n
    - 2, initial mxxm gate in pi frame\n
    - 3, initial myym gate in pi frame\n
    - 4, initial x gate in pi frame \n
    - 5, initial y gate in pi frame\n
    - 6, initial xxx gate in pi frame\n
    - 7, initial yyy gate in pi frame\n
    - 8, initial x gate in pi/2 frame \n
    - 9, initial y gate in pi/2 frame\n
    - 10, initial xxx gate in pi/2 frame\n
    - 11, initial yyy gate in pi/2 frame\n
    - 12, increment by 0 degrees in for pi gate in a pi frame \n
    - 13, increment by -90 degrees in for pi gate in a pi frame \n
    - 14, increment by -180 degrees in for pi gate in a pi frame \n
    - 15, increment by -270 degrees in for pi gate in a pi frame \n
    - 16, increment by 90 degrees in for pi gate in a pi frame \n
    - 17, increment by 180 degrees in for pi gate in a pi frame \n
    - 18, increment by 270 degrees in for pi gate in a pi frame \n
    - 19, increment by 0 degrees in for pi/2 gate in a pi frame \n
    - 20, increment by -90 degrees in for pi/2 gate in a pi frame \n
    - 21, increment by -180 degrees in for pi/2 gate in a pi frame \n
    - 22, increment by -270 degrees in for pi/2 gate in a pi frame \n
    - 23, increment by 90 degrees in for pi/2 gate in a pi frame \n
    - 24, increment by 180 degrees in for pi/2 gate in a pi frame \n
    - 25, increment by 270 degrees in for pi/2 gate in a pi frame \n
    - 26, increment by 0 degrees in for pi/2 gate in a pi/2 frame \n
    - 27, increment by -90 degrees in for pi/2 gate in a pi/2 frame \n
    - 28, increment by -180 degrees in for pi/2 gate in a pi/2 frame \n
    - 29, increment by -270 degrees in for pi/2 gate in a pi/2 frame \n
    - 30, increment by 90 degrees in for pi/2 gate in a pi/2 frame \n
    - 31, increment by 180 degrees in for pi/2 gate in a pi/2 frame \n
    - 32, increment by 270 degrees in for pi/2 gate in a pi/2 frame \n
    - 33, wait for pi/2 duration \n
    - 34, wait for pi duration \n
    - 35 - 35+n_p, wait for DC pulse durations \n
    - 36+n_p, increment phase by 0 degrees (z0z gate) \n
    - 36+n_p-36+n_p+n_z, perform arbitrary rotation by phi degrees (z phi z)\n

    Parameters:
                    n_pi_2 (int): number of points for a stanard pi/2 pulse.
                    n_pi (int): number of points for a stanard pi pulse.
                    n_p (list): list of number of points for each plunger pulse length (default = []).
                    arbZ (list): list of tuples of (arbitrary Z command table index, rotation angle) (default = []).

    Returns:
       command_table (dict): Dictionary of the RF command table to be directly uploaded onto AWG core.
    '''
    ct = []
    initial_gates = {"xx_pi_fr": {"phi": 0, "wave_idx": 0}, "yy_pi_fr": {"phi": -90, "wave_idx": 0}, "mxxm_pi_fr": {"phi": -180, "wave_idx": 0}, "myym_pi_fr": {"phi": 90, "wave_idx": 0},  "x_pi_2_fr": {"phi": 0, "wave_idx": 1},  "y_pi_2_fr": {"phi": -90, "wave_idx": 1},  "xxx_pi_2_fr": {"phi": -180, "wave_idx": 1},  "yyy_pi_2_fr": {"phi": 90, "wave_idx": 1},  "x_pi_fr": {"phi": 0, "wave_idx": 2},  "y_pi_fr": {"phi": -90, "wave_idx": 2},  "xxx_pi_fr": {"phi": -180, "wave_idx": 2},  "yyy_pi_fr": {"phi": 90, "wave_idx": 2}}
    waves = [{"index": 0, "awgChannel0": ["sigout0","sigout1"]}, {"index": 1, "awgChannel0": ["sigout0","sigout1"]},  {"index": 2, "awgChannel0": ["sigout0","sigout1"]}]
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
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    if len(n_p)==0:
        pass
    else:
        for item in n_p:
            ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": item}, "phase0": {"value": 0,  "increment": True}, "phase1": {"value": 0,  "increment": True}})
            ct_idx += 1
    ct.append({"index": ct_idx, "phase0": {"value": 0, "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    if len(arbZ) == 0:
        pass
    else:
        ii = 0
        for item in arbZ:
            if ii == 0:
                ct.append({"index": item[0], "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})
                ii = item[0]
                ii+= 1
            else:
                ct.append({"index": ii, "phase0": {"value": item[1], "increment": True}, "phase1": {"value": item[1],  "increment": True}})
                ii += 1
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '1.0'}, 'table': ct}
    return command_table

def make_plunger_command_table(n_p, n_rf):
    '''
    Generates command table for a single DC AWG core. Each core has two channels.
    - 0, plunger 1 pulse in plunger 1 frame \n
    - 1, plunger 2 pulse in plunger 2 frame \n
    - 2, plunger 1 pulse in plunger 2 frame \n
    - 3, plunger 2 pulse in plunger 1 frame \n
    - 4, plunger 1 pulse in pi/2 frame \n
    - 5, plunger 2 pulse in pi/2 frame \n
    - 6, plunger 1 pulse in pi frame \n
    - 7, plunger 2 pulse in pi frame \n
    - 8, wait for pi/2 pulse duration \n
    - 9, wait for pi pulse duration \n
    - 10, wait for plunger 1 pulse duration \n
    - 11, wait for plunger 2 pulse duration \n
    - 12, impose 0 degree phase shift \n

    Parameters:
                    n_p (list): list of 2 tuples of the form (ch_idx, n_p) with ch_idx as plunger channel index and n_p as the number of points for the plunger pulse.
                    n_rf (tuple):  tuple of the form (n_pi_2, n_pi), as the number of points for a pi/2 and pi pulse.

    Returns:
       command_table (dict): Dictionary of the plunger command table to be directly uploaded onto AWG core.
    '''
    waves = [{"index": 0}, {"index": 1}, {"index": 2}, {"index": 3}, {"index": 4}, {"index": 5}, {"index": 6}, {"index": 7}, {"index": 8}, {"index": 9}]
    n_pi_2 = n_rf[0]
    n_pi = n_rf[1]
    ct = []
    ct_idx = 0
    ct.append({"index": ct_idx, "waveform": waves[0]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[1]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[2]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[3]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[4]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[5]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[6]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[7]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[8]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": waves[9]})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi_2}})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_pi}})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_p[0][1]}})
    ct_idx += 1
    ct.append({"index": ct_idx, "waveform": {"playZero": True, "length": n_p[1][1]}})
    ct_idx += 1
    ct.append({"index": ct_idx, "phase0": {"value": 0, "increment": True}, "phase1": {"value": 0,  "increment": True}})
    ct_idx += 1
    command_table  = {'$schema': 'https://json-schema.org/draft-04/schema#', 'header': {'version': '1.0'}, 'table': ct}
    return command_table

def make_waveform_placeholders(n_array):
    '''
    Generates sequencer code for waveform placeholders on HDAWG FPGAs.

    Parameters:
                n_array (list): list of the number of points used for each waveform. Note, that each element of n_array must be at least 48 and an integer multiple of 16.
    Returns:
       sequence_code (str): sequencer code for waveform placeholders.
    '''
    ii = 0
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

def make_waveform_placeholders_plungers(n_array):
    '''
    Generates sequencer code for plunger gate waveform placeholders on HDAWG FPGAs.

    Parameters:
                n_array (list): list of the number of points used for each waveform. Note, that each element of n_array must be at least 48 and an integer multiple of 16.
    Returns:
       sequence_code (str): sequencer code for waveform placeholders.
    '''
    idx = 0
    #line_1 = "assignWaveIndex(placeholder("+str(n_array[0])+"),"+"0"+");\n"
    line_1 = "assignWaveIndex(placeholder("+str(n_array[0])+"),"+ "placeholder("+str(n_array[0])+"),"+"0"+");\n"
    line_2 = "assignWaveIndex(placeholder("+str(n_array[1])+"),"+ "placeholder("+str(n_array[1])+"),"+"1"+");\n"
    line_3 = "assignWaveIndex(placeholder("+str(n_array[2])+"),"+ "placeholder("+str(n_array[3])+"),"+"2"+");\n"
    line_4 = "assignWaveIndex(placeholder("+str(n_array[2])+"),"+ "placeholder("+str(n_array[3])+"),"+"3"+");\n"
    line_5 = "assignWaveIndex(placeholder("+str(n_array[4])+"),"+ "placeholder("+str(n_array[4])+"),"+"4"+");\n"
    line_6 = "assignWaveIndex(placeholder("+str(n_array[5])+"),"+ "placeholder("+str(n_array[5])+"),"+"5"+");\n"
    line_7 = "assignWaveIndex(placeholder("+str(n_array[6])+"),"+ "placeholder("+str(n_array[6])+"),"+"6"+");\n"
    line_8 = "assignWaveIndex(placeholder("+str(n_array[7])+"),"+ "placeholder("+str(n_array[7])+"),"+"7"+");\n"
    line_9 = "assignWaveIndex(placeholder("+str(n_array[4])+"),"+ "placeholder("+str(n_array[5])+"),"+"8"+");\n"
    line_10 = "assignWaveIndex(placeholder("+str(n_array[6])+"),"+ "placeholder("+str(n_array[7])+"),"+"9"+");\n"
    sequence_code = line_1+line_2+line_3+line_4+line_5+line_6+line_7+line_8+line_9+line_10
    return sequence_code

def make_gateset_sequencer_hard_trigger(n_seq, n_av, trig_channel=True):
    '''
    Generates sequencer code for waveform placeholders on HDAWG FPGAs.

    Parameters:
                n_array (list): list of the command table indices being executed on the AWG core.
                n_av (int): number of inner loops to iterate over during a GST run.
                trig_channel (bool): True if this core receives a physical trigger input, False otherwise.
    Returns:
       program (str): sequencer code for with command table executions for a given quantum algorithm.
    '''
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

def make_gate_npoints(gate_parameters, sample_rate):
    '''
    Generates a dictionary with the number of poitns for each pulse type used in a quantum algorithm.

    Parameters:
                n_array (list): list of the command table indices being executed on the AWG core.
                sample_rate (float): sample rate of the HDAWG in samples per second.
    Returns:
       program (str): sequencer code for with command table executions for a given quantum algorithm.
    '''
    gate_npoints = {"rf": {}, "plunger": {}}
    for idx in gate_parameters["rf"]:
        n_pi = ceil(sample_rate*gate_parameters["rf"][idx]["tau_pi"]*1e-9/16)*16
        n_pi_2 = ceil(sample_rate*gate_parameters["rf"][idx]["tau_pi_2"]*1e-9/16)*16
        gate_npoints["rf"][idx] = {"pi": n_pi, "pi_2": n_pi_2}
    for idx in gate_parameters["p"]:
        n_p = ceil(sample_rate*gate_parameters["p"][idx]["tau"]*1e-9)
        gate_npoints["plunger"][idx] = {"p": n_p}
    return gate_npoints

def generate_waveforms(gate_npoints, channel_map, added_padding=0):
    '''
    Generates a dictionary with all waveforms to be uploaded on 4 AWG cores, provided the number of points for each gate, channel mapping, and additional uniform padding per gate. Waveforms generated in the form lists, accounting for all padding schemes. Additional padding adds delays uniformly to all gates in a sequenc. Padding on either side of gates not to exceed 5 ns.

    Outer elements keys of waveform dictionary correspond to AWG core index (from 1-4). Dedicated RF cores have keys corresponding to each waveform:
    - "pi_pifr", pi pulse in a pi frame
    - "pi_2_pi_2fr", pi/2 pulse in a pi/2 frame
    - "pi_2_pifr", pi/2 pulse in a pi frame

    Dedicated DC cores have keys corresponding to each waveform:\n
    - "p1_p1fr", plunger 1 pulse in plunger 1 frame\n
    - "p2_p2fr", plunger 2 pulse in plunger 2 frame\n
    - "p1_p2fr", plunger 1 pulse in plunger 2 frame\n
    - "p2_p1fr", plunger 2 pulse in plunger 1 frame\n
    - "p1_pi_2fr", plunger 1 pulse in pi/2 frame\n
    - "p2_pi_2fr", plunger 2 pulse in pi/2 frame\n
    - "p1_pifr", plunger 1 pulse in pi frame\n
    - "p2_pifr", plunger 2 pulse in pi frame\n


    Parameters:
                gate_npoints (dict): dictionary of number of points per gate
                channel_map (dict): channel mapping dictionary.
                added_padding (float): added padding to either side of a gate pulse, in ns.
    Returns:
       waveforms (dict): dictionary of waveforms to be uploaded on each core.
    '''
    amp = 1
    waveforms = {}
    for idx in channel_map:
        if channel_map[idx]["rf"] == 1:
            waveforms[idx] = {"pi_pifr": None, "pi_2_pi_2fr": None, "pi_2_pifr": None}
        elif channel_map[idx]["rf"] == 0:
            waveforms[idx] = {"p1_p1fr": None, "p2_p2fr": None, "p1_p2fr": None, "p2_p1fr": None, "p1_pi_2fr": None , "p2_pi_2fr": None, "p1_pifr": None , "p2_pifr": None}
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
    for i in channel_map:
        if channel_map[i]["rf"] == 1:
            rf_ch = channel_map[i]["ch"]["gateindex"][0]
            rf_core = i
            ch_map_rf[rf_ch] = rf_core
        else:
            p_ch_1 = channel_map[i]["ch"]["gateindex"][0]
            p_ch_2 = channel_map[i]["ch"]["gateindex"][1]
            p_core = i
            ch_map_p[p_ch_1] = p_core
            ch_map_p[p_ch_2] = p_core

    max_rf_key = max(rf_pi_npoints, key=lambda k: rf_pi_npoints[k])
    npoints_pi_std = gate_npoints["rf"][max_rf_key]["pi"]
    npoints_pi_2_std = gate_npoints["rf"][max_rf_key]["pi_2"]
    max_p_key = max(plunger_npoints, key=lambda k: plunger_npoints[k])
    npoints_p_std = gate_npoints["plunger"][max_p_key]["p"]

    n_std_waveform_pi = len(rectangular_add_padding(gate_npoints["rf"][max_rf_key]["pi"], amp, min_points = npoints_pi_std, side_pad=added_padding))
    n_std_waveform_pi_2 = len(rectangular_add_padding(gate_npoints["rf"][max_rf_key]["pi_2"], amp, min_points = npoints_pi_2_std, side_pad=added_padding))

    if npoints_pi_std < 48:
         npoints_pi_std_1 = 48
    elif npoints_pi_std >= 48:
         npoints_pi_std_1 = npoints_pi_std
    else:
        pass
    if npoints_pi_2_std < 48:
         npoints_pi_2_std_1 = 48
    elif npoints_pi_2_std >= 48:
        npoints_pi_2_std_1 = npoints_pi_2_std
    else:
       pass

    for i in gate_npoints["rf"]:
        idx = ch_map_rf[i]
        waveforms[idx]["pi_pifr"] = rectangular_add_padding(gate_npoints["rf"][i]["pi"], amp, min_points = n_std_waveform_pi , side_pad=added_padding)
        waveforms[idx]["pi_2_pi_2fr"] = rectangular_add_padding(gate_npoints["rf"][i]["pi_2"], amp, min_points = n_std_waveform_pi_2, side_pad=added_padding)
        waveforms[idx]["pi_2_pifr"] = rectangular_add_padding(gate_npoints["rf"][i]["pi_2"], amp, min_points = n_std_waveform_pi , side_pad=added_padding)

    idx_p = ch_map_p[7]
    if gate_npoints["plunger"][7]["p"] < 48:
        npoints_p_1 = 48
    elif gate_npoints["plunger"][7]["p"] >= 48:
        npoints_p_1 = gate_npoints["plunger"][7]["p"]
    else:
        pass
    if gate_npoints["plunger"][8]["p"] < 48:
        npoints_p_2 = 48
    elif gate_npoints["plunger"][8]["p"] >= 48:
        npoints_p_2 = gate_npoints["plunger"][8]["p"]
    else:
        pass
    npoints_p1p2_fr = max([npoints_p_1,npoints_p_2])
    waveforms[idx_p]["p1_p2fr"] = rectangular_add_padding(gate_npoints["plunger"][7]["p"], amp, min_points = npoints_p1p2_fr, side_pad =added_padding)
    waveforms[idx_p]["p2_p1fr"] = rectangular_add_padding(gate_npoints["plunger"][8]["p"], amp, min_points = npoints_p1p2_fr, side_pad =added_padding)
    waveforms[idx_p]["p1_p1fr"] = rectangular_add_padding(gate_npoints["plunger"][7]["p"], amp, min_points = npoints_p_1, side_pad=added_padding)
    waveforms[idx_p]["p2_p2fr"] = rectangular_add_padding(gate_npoints["plunger"][8]["p"], amp, min_points = npoints_p_2, side_pad =added_padding)
    waveforms[idx_p]["p1_pi_2fr"] = rectangular_add_padding(gate_npoints["plunger"][7]["p"], amp, min_points = n_std_waveform_pi_2, side_pad =added_padding)
    waveforms[idx_p]["p2_pi_2fr"] = rectangular_add_padding(gate_npoints["plunger"][8]["p"], amp, min_points = n_std_waveform_pi_2, side_pad =added_padding)
    waveforms[idx_p]["p1_pifr"] = rectangular_add_padding(gate_npoints["plunger"][7]["p"], amp, min_points = n_std_waveform_pi, side_pad =added_padding)
    waveforms[idx_p]["p2_pifr"] = rectangular_add_padding(gate_npoints["plunger"][8]["p"], amp, min_points = n_std_waveform_pi, side_pad =added_padding)
    return waveforms

def config_hdawg(awg, gate_parameters, channel_mapping, channels_on=True):
    ## Should have a generic channel mapping funciton from channels to cores
    '''
    Configures HDAWG module to run a quantum algorithm. In particular, this function does the following:
    - enables oscillator control \n
    - sets oscillator frequencies \n
    - sets output amplitudes for each channel \n
    - turns on output channels \n


    Parameters:
                    awg (silospin.drivers.zi_hdawg.HdawgDriver): instance of HDAWG.
                    gate_parameters (dict): dictionary of gate paramters for each qubit.

    Returns:
       None.
    '''
    daq = awg._daq
    dev = awg._connection_settings["hdawg_id"]
    daq.setInt(f"/{dev}/system/awg/oscillatorcontrol", 1)
    rf_gate_param = gate_parameters["rf"]
    p_gate_param = gate_parameters["p"]
    channel_idxs = {"1": [1,2], "2": [3,4], "3": [5,6], "4": [7,8]}
    channel_osc_idxs = {1: 1, 2: 5, 3: 9, 4: 13}

    for core in channel_mapping:
        if channel_mapping[core]['rf'] == 1:
            core_idx = channel_mapping[core]['core_idx']
            osc_idx = channel_osc_idxs[core]
            i_idx = channel_mapping[core]['channel_core_number'][0]
            q_idx = channel_mapping[core]['channel_core_number'][1]
            awg.set_osc_freq(osc_idx, rf_gate_param[core_idx]["mod_freq"])
            awg.set_sine(i_idx, osc_idx)
            awg.set_sine(q_idx, osc_idx)
            awg.set_out_amp(i_idx, 1, rf_gate_param[core_idx]["i_amp"])
            awg.set_out_amp(q_idx, 2, rf_gate_param[core_idx]["q_amp"])
            if channels_on == True:
                awg._hdawg.sigouts[i_idx].on(1)
                awg._hdawg.sigouts[q_idx].on(1)
            else:
                pass
        # elif channel_mapping[core]['rf'] == 0:
        #     core_idx = channel_mapping[core]['core_idx']
        #     p1_idx = channel_mapping[core]['channel_core_number'][0]
        #     p2_idx = channel_mapping[core]['channel_core_number'][0]
        #     p1_core_idx = channel_mapping[core]['channel_core_number'][0]
        #     p2_core_idx = channel_mapping[core]['channel_core_number'][1]
        #     awg.set_out_amp(p1_core_idx, 1, p_gate_param[p1_idx]["i_amp"])
        #     awg.set_out_amp(p2_core_idx, 2, p_gate_param[p2_idx]["q_amp"])
        #     if channels_on == True:
        #         awg._hdawg.sigouts[i_idx].on(1)
        #         awg._hdawg.sigouts[q_idx].on(1)
            else:
                pass
