import numpy as np
import pandas as pd
import os
from math import ceil
import json
import time
from pkg_resources import resource_filename
from zhinst.toolkit import Waveforms
import zhinst.utils
from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular
from silospin.quantum_compiler.qc_helpers import *
from silospin.io.qc_io import read_qubit_paramater_file, write_qubit_parameter_file, quantum_protocol_parser, gst_parser, quantum_protocol_parser_csv_v2, quantum_protocol_parser_Zarb, quantum_protocol_parser_Zarb_v2

class CompileGST:
    def __init__(self, gst_file_path, awg, qubits = [0,1,2,3], hard_trigger = False, trigger_channel=0, n_av = 1, n_fr = 1):
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  qubits

        self._qubit_parameters = {
        0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 200e-9,  "tau_pi_2" :  100e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 200e-9,  "tau_pi_2" :  100e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        2: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 120e-9,  "tau_pi_2" :  60e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        3: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 160e-9,  "tau_pi_2" :  80e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
        tau_pi_2_set = np.array([self._qubit_parameters[0]["tau_pi_2"], self._qubit_parameters[1]["tau_pi_2"], self._qubit_parameters[2]["tau_pi_2"], self._qubit_parameters[3]["tau_pi_2"]])
        tau_pi_2_standard_idx = np.argmax(tau_pi_2_set)

        ##Define standard length of pulse in time
        tau_pi_2_standard = np.max(tau_pi_2_set)
        tau_pi_standard = 2*tau_pi_2_standard

        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32

        tau_pi_2_standard_new = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard_new = npoints_pi_standard/self._sample_rate

        qubit_lengths = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
        qubit_npoints = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}

        for idx in qubits:
            qubit_lengths[idx]["pi"] = ceil(tau_pi_standard_new*1e9)
            qubit_lengths[idx]["pi_2"] = ceil(tau_pi_2_standard_new*1e9)
            qubit_npoints[idx]["pi"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi"]/32)*32
            qubit_npoints[idx]["pi_2"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi_2"]/32)*32

        self._waveforms = generate_waveforms(qubit_npoints, tau_pi_2_standard_idx, amp=1)
        #self._gate_sequences = quantum_protocol_parser_Zarb(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})
        self._gate_sequences = quantum_protocol_parser_Zarb_v2(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})

        ct_idxs_all = {}
        arbZs = []
        n_arbZ = 0
        for idx in self._gate_sequences:
             gate_sequence = self._gate_sequences[idx]
             ct_idxs_all[idx], arbZ = make_command_table_idxs_v6(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9), n_arbZ)
             n_arbZ += len(arbZ)
             arbZs.append(arbZ)

        arbZ_s = []
        for lst in arbZs:
            for i in lst:
                arbZ_s.append(i)
        command_tables = generate_reduced_command_table_v4(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ_s)
        self._ct_idxs = ct_idxs_all
        self._command_tables = command_tables

        waveforms_awg = {}
        sequencer_code = {}
        seq_code = {}
        command_code = {}
        n_array = [npoints_pi_2_standard, npoints_pi_standard]

        for idx in qubits:
            waveforms = Waveforms()
            waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["pi_2"])
            waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["pi"])
            waveforms_awg[idx] = waveforms
            ##Make a sequence code
            seq_code[idx] =  make_waveform_placeholders(n_array)
            command_code[idx] = ""
            ##outer frame loop
            sequence = "repeat("+str(n_fr)+"){\n "
            for ii in range(len(ct_idxs_all)):
                 n_seq = ct_idxs_all[ii][str(idx)]
                 if hard_trigger == False:
                     seq = make_gateset_sequencer_fast_v2(n_seq)
                 else:
                     if idx == trigger_channel:
                         seq = make_gateset_sequencer_hard_trigger_v2(n_seq, n_av, trig_channel=True)
                     else:
                         seq = make_gateset_sequencer_hard_trigger_v2(n_seq, n_av, trig_channel=False)
                 sequence += seq

            command_code[idx] = command_code[idx] + sequence
            sequencer_code[idx] =  seq_code[idx] + command_code[idx] + "}"

        self._sequencer_code = sequencer_code

        for idx in qubits:
             self._awg.load_sequence(sequencer_code[idx], awg_idx=idx)
             self._awg._awgs["awg"+str(idx+1)].write_to_waveform_memory(waveforms_awg[idx])

        self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

        daq = self._awg._daq
        dev = self._awg._connection_settings["hdawg_id"]

        for idx in qubits:
             i_idx = self._channel_idxs[str(idx)][0]
             q_idx = self._channel_idxs[str(idx)][1]
             osc_idx = self._channel_osc_idxs[str(idx)]
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
             daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables))

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)
class RamseyTypes:
    ##should generalize for all qubits ==> only change will be pulse type
    def __init__(self, awg, t_range, npoints_t, npoints_av, taus_pulse, axis = "x", sample_rate = 2.4e9, n_fr=1):
        ##taus_pulse  ==> dictionary
        self._sample_rate = sample_rate
        self._awg = awg
        t_start = t_range[0]
        t_end = t_range[1]
        n_start = ceil(t_range[0]*sample_rate/32)*32
        dn = ceil(((t_range[1]-t_range[0])/npoints_t)*sample_rate/16)*16
        n_end = ceil(t_range[1]*sample_rate/dn)*dn
        n_steps = int(n_end/dn)
        t_steps = []
        n_s = []
        self._channel_idxs = {0: [0,1], 1: [2,3], 2: [4,5], 3: [6,7]}
        for i in range(n_start, n_end, dn):
            n_s.append(i)
            t_steps.append(i/sample_rate)

        n_durations = []
        qubits = []
        self._sequences = {}
        for idx in taus_pulse:
            qubits.append(idx)
            n_rect = ceil(self._sample_rate*taus_pulse[idx]/32)*32
            #self._sequences[idx] = make_ramsey_sequencer_v2(n_start, n_end, dn, n_rect, npoints_av, n_fr)
            self._sequences[idx] = make_ramsey_sequencer(n_start, n_end, dn, n_rect, npoints_av)
            self._awg.load_sequence(self._sequences[idx], awg_idx=idx)
            if axis == "x":
                self._awg.set_phase(self._channel_idxs[idx][0]+1, 0)
                self._awg.set_phase(self._channel_idxs[idx][1]+1, 90)
            elif axis == "y":
                self._awg.set_phase(self._channel_idxs[idx][0]+1, 90)
                self._awg.set_phase(self._channel_idxs[idx][1]+1, 180)
            else:
                pass

        self._n_samples = n_s
        self._tau_steps  = t_steps
        self._awg_idxs = qubits

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)

class RabiTypes:
    ##should generalize for all qubits ==> only change will be pulse type
    def __init__(self, awg, t_range, npoints_t, npoints_av, tau_wait, qubits, axis = "x", sample_rate = 2.4e9):
        ##taus_pulse  ==> dictionary
        self._sample_rate = sample_rate
        self._awg = awg
        t_start = t_range[0]
        t_end = t_range[1]
        n_wait = ceil(tau_wait*sample_rate/32)*32
        n_start = ceil(t_range[0]*sample_rate/48)*48
        dn = ceil(((t_range[1]-t_range[0])/npoints_t)*sample_rate/16)*16
        n_end = ceil(t_range[1]*sample_rate/dn)*dn
        n_steps = int(n_end/dn)
        t_steps = []
        n_s = []
        self._channel_idxs = {0: [0,1], 1: [2,3], 2: [4,5], 3: [6,7]}
        for i in range(n_start, n_end, dn):
            n_s.append(i)
            t_steps.append(i/sample_rate)

        n_durations = []
        self._sequences = {}
        for idx in qubits:
            self._sequences[idx] = make_rabi_sequencer(n_start, n_end, dn, n_wait, npoints_av)
            self._awg.load_sequence(self._sequences[idx], awg_idx=idx)
            if axis == "x":
                self._awg.set_phase(self._channel_idxs[idx][0]+1, 0)
                self._awg.set_phase(self._channel_idxs[idx][1]+1, 90)
            elif axis == "y":
                self._awg.set_phase(self._channel_idxs[idx][0]+1, 90)
                self._awg.set_phase(self._channel_idxs[idx][1]+1, 180)
            else:
                pass

        self._n_samples = n_s
        self._tau_steps  = t_steps
        self._awg_idxs = qubits

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)
