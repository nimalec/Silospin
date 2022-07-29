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
from silospin.io.qc_io import read_qubit_paramater_file, write_qubit_parameter_file, quantum_protocol_parser, gst_parser, quantum_protocol_parser_csv_v2, quantum_protocol_parser_Zarb


class MultiQubitGatesSet:
    def __init__(self, gate_strings, awg, qubit_parameters=None, sample_rate=2.4e9, continuous=False, hard_trigger = False, soft_trigger = False, waveforms_preloaded=False, update_qubit_parameters = "0", qubit_parameters_file_path = "qubit_parameters.csv"):
        ##should also add fucntion to check if only one parameter needs to be updated or multiple.
        self._gate_strings = gate_strings
        self._awg = awg
        self._sample_rate = sample_rate
        # 1. update qubit parameters **
        # 2. clear outputs of all awg cores **
        # 3. upload waveforms for all qubits [for both pi and pi/2 gates] (if flag is set to) [8 waveforms for now, could generalize to more]
        # 4. resetOsc for all cores
        # 5. set oscillators, outputs, etc.
        # 6. load command table sequences and compile

        default_qubit_params = {
        "0": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        "1": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
         "2": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        "3": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}


        if update_qubit_parameters == "1":
            self._qubit_parameters = qubit_parameters
            write_qubit_parameter_file(self._qubit_parameters, qubit_parameters_file_path)

        elif update_qubit_parameters == "0":
            self._qubit_parameters = default_qubit_params

        elif update_qubit_parameters == "-1":
            self._qubit_parameters =  read_qubit_paramater_file(qubit_parameters_file_path)
            pass

        awg_cores = []
        command_tables = {}
        cts_idxs = {}
        for key in gate_strings:
            gt_seq = gate_strings[key]
            if gt_seq:
                gt_0 = gt_seq[0]
                ct_idxs, n_ts = make_command_table_idxs(gt_seq[1:len(gt_seq)], sample_rate)
                cts_idxs[key] = ct_idxs
                command_table = generate_reduced_command_table(gt_0, npoints_wait = n_ts, npoints_plunger = None, delta_iq = self._qubit_parameters[key]["delta_iq"], phi_z = 0)
                command_tables[key] = command_table
                awg_idx = int(key)
                awg_cores.append(awg_idx)
            else:
                pass

        self._awg_idxs = awg_cores
        self._command_tables = command_tables

        waveforms_tau_pi = {}
        waveforms_tau_pi_2 = {}
        waveforms_qubits = {}

        for awg_idx in self._awg_idxs:
            n_array = []
            waveforms = Waveforms()
            npoints_tau_pi = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi"]/16)*16
            npoints_tau_pi_2 = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi_2"]/16)*16
            waveforms_tau_pi[str(awg_idx)] = rectangular(npoints_tau_pi, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
            waveforms_tau_pi_2[str(awg_idx)] = rectangular(npoints_tau_pi_2, self._qubit_parameters [str(awg_idx)]["i_amp_pi_2"])
            n_array.append(len(waveforms_tau_pi[str(awg_idx)]))
            n_array.append(len(waveforms_tau_pi_2[str(awg_idx)]))
            waveforms.assign_waveform(slot = 0, wave1 = waveforms_tau_pi[str(awg_idx)])
            waveforms.assign_waveform(slot = 1, wave1 = waveforms_tau_pi_2[str(awg_idx)])
            waveforms_qubits[str(awg_idx)] = waveforms
            seq_code = make_gateset_sequencer_fast(n_array, cts_idxs[str(awg_idx)], continuous=continuous, soft_trigger=soft_trigger, hard_trigger=hard_trigger)
            self._awg.load_sequence(seq_code, awg_idx=awg_idx)
            self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)

        self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

        daq = self._awg._daq
        dev = self._awg._connection_settings["hdawg_id"]
        for awg_idx in self._awg_idxs:
             i_idx = self._channel_idxs[str(awg_idx)][0]
             q_idx = self._channel_idxs[str(awg_idx)][1]
             osc_idx = self._channel_osc_idxs[str(awg_idx)]
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[str(awg_idx)]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[str(awg_idx)]["q_amp_pi"])
             daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(self._command_tables[str(awg_idx)]))



        #daq = self._awg._daq
        #dev = self._awg._connection_settings["hdawg_id"]

     ## write so that gates only need to be calibrated once (only need to keep track of tau_pi, tau_pi_2)
     ## ensure a 4x2 channel grouping
    ## awg: awg core
    ## iq_settings: dictionary of dictionaries for IQ settings
    ## tau_pis: dictionary of tau_pi values
    ## tau_pi_2s: dictiorary of tau_pi_2 values

        # self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        # self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}


         # waves_tau_pi = {}
         # waves_tau_pi_2 = {}
         # n_arrays = {}
         # sequences = {}


         # for awg_idx in awg_cores:
         #     i_idx = channel_idxs[str(awg_idx)][0]
         #     q_idx = channel_idxs[str(awg_idx)][1]
         #     osc_idx = channel_osc_idxs[str(awg_idx)]
         #     self._awg._hdawg.sigouts[i_idx].on(0)
         #     self._awg._hdawg.sigouts[q_idx].on(0)
         #     self._awg.set_osc_freq(osc_idx, self._iq_settings[str(awg_idx)]["freq"])
         #     self._awg.set_sine(i_idx+1, osc_idx)
         #     self._awg.set_sine(q_idx+1, osc_idx)
         #     self._awg.set_out_amp(self._iq_settings[str(awg_idx)]["i_sin"], 1, self._iq_settings[str(awg_idx)]["i_amp"])
         #     self._awg.set_out_amp(self._iq_settings[str(awg_idx)]["q_sin"], 2, self._iq_settings[str(awg_idx)]["q_amp"])
         #
         #     command_tables[str(awg_idx)] = make_command_table(self._gate_strings[str(awg_idx)], self._iq_settings[str(awg_idx)], self._sample_rate)
         #     npoints_tau_pi[str(awg_idx)] = ceil(self._sample_rate*self._taus_pi[str(awg_idx)]/16)*16
         #     npoints_tau_pi_2[str(awg_idx)] = ceil(self._sample_rate*self._taus_pi_2[str(awg_idx)]/16)*16
         #     waves_tau_pi[str(awg_idx)] = rectangular(npoints_tau_pi[str(awg_idx)], 0.5)
         #     waves_tau_pi_2[str(awg_idx)] = rectangular(npoints_tau_pi_2[str(awg_idx)], 0.5)
         #
         #     n_array = []
         #     for gt in self._gate_strings[str(awg_idx)]:
         #         if gt in {"x", "y", "xxx", "yyy"}:
         #             n_array.append(npoints_tau_pi_2[str(awg_idx)])
         #         elif gt in  {"xx", "yy", "mxxm", "myym"}:
         #             n_array.append(npoints_tau_pi[str(awg_idx)])
         #         else:
         #             pass
         #
         #
         #     n_arrays[str(awg_idx)] = n_array
         #
         #     self._awg.load_sequence(phase_reset_seq, awg_idx)
         #     self._awg._awgs["awg"+str(awg_idx+1)].single(True)
         #     self._awg._awgs["awg"+str(awg_idx+1)].enable(True)
         #     sequences[str(awg_idx)] = make_gateset_sequencer(n_arrays[str(awg_idx)], len(self._gate_strings[str(awg_idx)]) , continuous=continuous, trigger=trigger)
         #     self._awg.load_sequence(sequences[str(awg_idx)], awg_idx)
         #
         # self._sequence_code = sequences
         #
         # daq = self._awg._daq
         # dev = self._awg._connection_settings["hdawg_id"]
         # waveforms_awgs = {}
         # for awg_idx in awg_cores:
         #     waveforms = Waveforms()
         #     ii = 0
         #     for gt in self._gate_strings[str(awg_idx)]:
         #         if gt in {"x", "y", "xxx", "yyy"}:
         #             waveforms.assign_waveform(slot = ii, wave1 = waves_tau_pi_2[str(awg_idx)])
         #             waveforms_awgs[str(awg_idx)] = waves_tau_pi_2[str(awg_idx)]
         #             ii += 1
         #
         #         elif gt in  {"xx", "yy", "mxxm", "myym"}:
         #             waveforms.assign_waveform(slot = ii, wave1 =waves_tau_pi[str(awg_idx)])
         #             waveforms_awgs[str(awg_idx)] = waves_tau_pi[str(awg_idx)]
         #             ii += 1
         #         else:
         #             pass
         #     self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)
         #     daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(command_tables[str(awg_idx)]))
         #
         # self._waveforms =  waveforms_awgs

    def compile_program(self):
        phase_reset_seq = "resetOscPhase();\n"
        daq = self._awg._daq
        dev = self._awg._connection_settings["hdawg_id"]
        for awg_idx in self._awg_idxs:
             i_idx = self._channel_idxs[str(awg_idx)][0]
             q_idx = self._channel_idxs[str(awg_idx)][1]
             osc_idx = self._channel_osc_idxs[str(awg_idx)]
             # self._awg._hdawg.sigouts[i_idx].on(0)
             # self._awg._hdawg.sigouts[q_idx].on(0)
             # self._awg._hdawg.sigouts[i_idx].on(1)
             # self._awg._hdawg.sigouts[q_idx].on(1)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[str(awg_idx)]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[str(awg_idx)]["q_amp_pi"])
             self._awg.load_sequence(phase_reset_seq, awg_idx)
             self._awg._awgs["awg"+str(awg_idx+1)].single(True)
             self._awg._awgs["awg"+str(awg_idx+1)].enable(True)
             daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(self._command_tables[str(awg_idx)]))


    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)


class MultiQubitGST:
    def __init__(self, gst_file_path, awg, qubits = {1,2,3,4}):
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  np.array(list(qubits))-1
        self._qubit_parameters = {
        "0": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        "1": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        "2": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        "3": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
        qubit_lengths = {1: {"pi": None, "pi_2": None},2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None},4: {"pi": None, "pi_2": None}}

        for idx in qubits:
            qubit_lengths[idx]["pi"] = ceil(self._sample_rate*self._qubit_parameters[str(idx-1)]["tau_pi"]/48)*48
            qubit_lengths[idx]["pi_2"] = ceil(self._sample_rate*self._qubit_parameters[str(idx-1)]["tau_pi_2"]/48)*48
        self._gate_sequences = quantum_protocol_parser(self._gst_path, qubit_lengths = qubit_lengths, qubit_set = qubits)

        gts_0 = {0: [], 1: [], 2: [], 3: []}   #initial gates
        n_waits = {0: [], 1: [], 2: [], 3: []} #wait times
        ct_idxs_all = {} # command table indices, ct_idxs_all[line][awg_idx]
        command_tables = {} # command tables for each core, command_tables[awg_idx]
        n_t_ts = {0: 0, 1: 0, 2: 0, 3: 0}

        #Loop over number of lines in sequence file
        for idx in self._gate_sequences:
            cts_idxs = {}
            gate_sequence = self._gate_sequences[idx] #sequence dictionary for a line

            for key in gate_sequence: #loops over qubits
                gt_seq = gate_sequence[key] #gt sequence for qubit (list)
                if gt_seq:
                    gts_0[int(key)].append(gt_seq[0])
                    ct_idxs, n_ts = make_command_table_idxs_v2(len(self._gate_sequences), n_t_ts[int(key)], gt_seq[1:len(gt_seq)], self._sample_rate)
                    n_waits[int(key)].append(n_ts)
                    cts_idxs[int(key)] = ct_idxs
                    n_t_ts[int(key)] = n_t_ts[int(key)] + len(n_ts)
                else:
                    pass
            ct_idxs_all[idx] = cts_idxs

        for key in n_waits:
            if n_waits[key]:
                n_waits[key] = list(np.array(n_waits[key]).flatten())
            else:
                pass

        command_tables = {}
        for i in self._awg_cores:
            command_table = generate_reduced_command_table_v2(gts_0[i], npoints_wait = n_waits[i], npoints_plunger = None, delta_iq = self._qubit_parameters[str(i)]["delta_iq"], phi_z = 0)
            command_tables[str(i)] = command_table

        self._command_tables = command_tables

        # waveforms_tau_pi = {}
        # waveforms_tau_pi_2 = {}
        # waveforms_qubits = {}
        # sequencer_code = {}
        # seq_code = {}
        # command_code = {}
        # for awg_idx in self._awg_cores:
        #     n_array = []
        #     waveforms = Waveforms()
        #     npoints_tau_pi = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi"]/16)*16
        #     npoints_tau_pi_2 = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi_2"]/16)*16
        #     waveforms_tau_pi[str(awg_idx)] = rectangular(npoints_tau_pi, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
        #     waveforms_tau_pi_2[str(awg_idx)] = rectangular(npoints_tau_pi_2, self._qubit_parameters [str(awg_idx)]["i_amp_pi_2"])
        #     n_array.append(len(waveforms_tau_pi[str(awg_idx)]))
        #     n_array.append(len(waveforms_tau_pi_2[str(awg_idx)]))
        #     waveforms.assign_waveform(slot = 0, wave1 = waveforms_tau_pi[str(awg_idx)])
        #     waveforms.assign_waveform(slot = 1, wave1 = waveforms_tau_pi_2[str(awg_idx)])
        #     waveforms_qubits[str(awg_idx)] = waveforms
        #     seq_code[awg_idx] =  make_waveform_placeholders(n_array)
        #     command_code[awg_idx] = ""
        #     #command_code[awg_idx] = []
        #     for idx in range(len(ct_idxs_all)):
        #         n_seq = ct_idxs_all[idx][awg_idx]
        #         sequence = make_gateset_sequencer_fast_v2(idx, n_seq)
        #         command_code[awg_idx] = command_code[awg_idx] + sequence
        #         #command_code[awg_idx].append(sequence)
        #     sequencer_code[awg_idx] =  seq_code[awg_idx] + command_code[awg_idx]


        # self._sequencer_code = sequencer_code

        # for awg_idx in self._awg_cores:
        #     #print(command_code[awg_idx][len(command_code[awg_idx])-2])
        #      self._awg.load_sequence(sequencer_code[awg_idx], awg_idx=awg_idx)
        #      self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)
        # #
        # self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        # self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

        # daq = self._awg._daq
        # dev = self._awg._connection_settings["hdawg_id"]
        # for awg_idx in self._awg_cores:
        #      i_idx = self._channel_idxs[str(awg_idx)][0]
        #      q_idx = self._channel_idxs[str(awg_idx)][1]
        #      osc_idx = self._channel_osc_idxs[str(awg_idx)]
        #      self._awg._hdawg.sigouts[i_idx].on(1)
        #      self._awg._hdawg.sigouts[q_idx].on(1)
        #      self._awg.set_osc_freq(osc_idx, self._qubit_parameters[str(awg_idx)]["mod_freq"])
        #      self._awg.set_sine(i_idx+1, osc_idx)
        #      self._awg.set_sine(q_idx+1, osc_idx)
        #      self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
        #      self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[str(awg_idx)]["q_amp_pi"])
        #      daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(self._command_tables[str(awg_idx)]))

    # def run_program(self, awg_idxs=None):
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = self._awg_idxs
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)


class MultiQubitGST_v2:
    def __init__(self, gst_file_path, awg, qubits = [0,1,2,3], hard_trigger = False, trigger_channel=0):
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  qubits
        self._qubit_parameters = {
        0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 140e-9,  "tau_pi_2" :  70e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        2: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 120e-9,  "tau_pi_2" :  60e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        3: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 160e-9,  "tau_pi_2" :  80e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
        tau_pi_2_set = np.array([self._qubit_parameters[0]["tau_pi_2"], self._qubit_parameters[1]["tau_pi_2"], self._qubit_parameters[2]["tau_pi_2"], self._qubit_parameters[3]["tau_pi_2"]])
        tau_pi_2_standard_idx = np.argmax(tau_pi_2_set)

        ##Define standard length of pulse in time
        tau_pi_2_standard = np.max(tau_pi_2_set)
        tau_pi_standard = 2*tau_pi_2_standard

        ##Define standard length of pulse in number of samples
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32

        ##convert back to time
        tau_pi_2_standard_new = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard_new = npoints_pi_standard/self._sample_rate

        qubit_lengths = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
        qubit_npoints = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
        ##Generates pulse lengths for all qubits
        for idx in qubits:
            qubit_lengths[idx]["pi"] = ceil(tau_pi_standard_new*1e9)
            qubit_lengths[idx]["pi_2"] = ceil(tau_pi_2_standard_new*1e9)
            qubit_npoints[idx]["pi"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi"]/32)*32
            qubit_npoints[idx]["pi_2"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi_2"]/32)*32

        self._waveforms = generate_waveforms(qubit_npoints, tau_pi_2_standard_idx, amp=1)
        self._gate_sequences =  quantum_protocol_parser(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})
        self._command_table = generate_reduced_command_table_v3(npoints_pi_2_standard, npoints_pi_standard)

        ##Number of waits
        ct_idxs_all = {} # command table indices, ct_idxs_all[line][awg_idx]
        for idx in self._gate_sequences:
             gate_sequence = self._gate_sequences[idx]
             ct_idxs_all[idx] = make_command_table_idxs_v4(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9))

        self._ct_idxs = ct_idxs_all

        waveforms_awg = {}
        sequencer_code = {}
        seq_code = {}
        command_code = {}
        n_array = [npoints_pi_2_standard, npoints_pi_standard]

        for idx in qubits:
            ##Makes waveform objects for upload
            waveforms = Waveforms()
            waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["pi_2"])
            waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["pi"])
            waveforms_awg[idx] = waveforms
            ##Make a sequence code
            seq_code[idx] =  make_waveform_placeholders(n_array)
            command_code[idx] = ""
            sequence = ""
            for ii in range(len(ct_idxs_all)):
                 n_seq = ct_idxs_all[ii][str(idx)]
                 #seq = make_gateset_sequencer_fast_v2(n_seq)
                 if hard_trigger == False:
                     seq = make_gateset_sequencer_fast_v2(n_seq)
                 else:
                     if idx == trigger_channel:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=True)
                     else:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=False)
                 sequence += seq

            command_code[idx] = command_code[idx] + sequence
            sequencer_code[idx] =  seq_code[idx] + command_code[idx]

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
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
             daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_table))

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)

class MultiQubitGST_v3:
    def __init__(self, gst_file_path, awg, qubit_parameters, channel_mapping, trig_settings = {"hard_trig": False, "trig_channel": 0}, sample_rate = 2.4e9):

        self._gst_path = gst_file_path
        self._awg = awg
        self._channel_mapping = channel_mapping
        self._sample_rate = sample_rate
        self._qubit_parameters = qubit_parameters

        ##Insert mapping function here:
        ## Channel types:  qidx w/ idx = {0, N}. pidx w/ idx = {0, N}.  P0 -> P01, P1 -> P12, etc.
        qubits = [] ##list of channels used for qubits
        plungers = [] ##list of channels used for plunger gates
        for awg_idx in self._channel_mapping:
            end_idx = len(self._channel_mapping[awg_idx])
            if self._channel_mapping[awg_idx][0] == "q":
                qubits.append((awg_idx, int(self._channel_mapping[awg_idx][1:end_idx])))
            elif self._channel_mapping[awg_idx][0] == "p":
                plungers.append((awg_idx,self._channel_mapping[awg_idx][1:end_idx]))
            else:
                pass

        ## Defines set of time delays and standard pulse lengths
        tau_pi_2_set = []
        qubit_lengths = {}
        qubit_npoints = {}
        for q in qubits:
            tau_pi_2_set.append(self._qubit_parameters[q[1]]["tau_pi_2"])
            qubit_lengths[q[0]] = {"pi": None, "pi_2": None}
            qubit_npoints[q[0]] = {"pi": None, "pi_2": None}

        tau_pi_2_set = np.array(tau_pi_2_set)
        tau_pi_2_standard_idx = np.argmax(tau_pi_2_set)
        tau_pi_2_standard = np.max(tau_pi_2_set)
        tau_pi_standard = 2*tau_pi_2_standard
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32
        tau_pi_2_standard_new = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard_new = npoints_pi_standard/self._sample_rate

        ##Generates pulse lengths for all qubits
        for q in qubits:
            if self._sample_rate*ceil(self._qubit_parameters[q[1]]["tau_pi"]/32)*32 ==  npoints_pi_standard:
                tau_pi_2_standard_idx = q[1]
            else:
                pass
            qubit_lengths[q[1]] = {"pi": ceil(tau_pi_standard_new*1e9), "pi_2": ceil(tau_pi_2_standard_new*1e9)}
            qubit_npoints[q[1]] = {"pi": ceil(self._sample_rate*self._qubit_parameters[q[1]]["tau_pi"]/32)*32, "pi_2": ceil(self._sample_rate*self._qubit_parameters[q[1]]["tau_pi_2"]/32)*32}

        self._waveforms = generate_waveforms(qubit_npoints, tau_pi_2_standard_idx, amp=1)

        ##Modify to account for Z and plunger gates
        #self._gate_sequences =  quantum_protocol_parser(gst_file_path, qubit_lengths, qubit_channels = set(qubits), plunger_channels={})

        self._gate_sequences, self._plunger_sequences =  quantum_protocol_parser_csv_v2(self._gst_path, qubit_lengths, qubit_cores={0,1,2}, plunger_channels={3})

        ct_idxs_all = {}
        # Loop over number of lines
        for idx in self._gate_sequences:
             gate_sequence = self._gate_sequences[idx]
             ct_idxs_all[idx], arbZ = make_command_table_idxs_v5(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9))

        self._ct_idxs = ct_idxs_all
        # ## Separate command table for each AWG channel
        # self._command_table = generate_reduced_command_table_v4(npoints_pi_2_standard, npoints_pi_standard, arbZ)
        #
        # waveforms_awg = {}
        # sequencer_code = {}
        # seq_code = {}
        # command_code = {}
        # n_array = [npoints_pi_2_standard, npoints_pi_standard]
        #
        # ## Loop over qubit awg idx
        # for q in qubits:
        #     waveforms = Waveforms()
        #     waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[q[0]]["pi_2"])
        #     waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[q[0]]["pi"])
        #     waveforms_awg[q[0]] = waveforms
        #     ##Make a sequence code
        #     seq_code[q[0]] =  make_waveform_placeholders(n_array)
        #     command_code[q[0]] = ""
        #     sequence = ""
        #     for ii in range(len(ct_idxs_all)):
        #          n_seq = ct_idxs_all[ii][str(q[0])]
        #          #seq = make_gateset_sequencer_fast_v2(n_seq)
        #          if hard_trigger == False:
        #              seq = make_gateset_sequencer_fast_v2(n_seq)
        #          else:
        #              if q[0] == trigger_channel:
        #                  seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=True)
        #              else:
        #                  seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=False)
        #          sequence += seq
        #
        #     command_code[q[0]] = command_code[idx] + sequence
        #     sequencer_code[q[0]] =  seq_code[idx] + command_code[idx]
        #
        # self._sequencer_code = sequencer_code
        #
        # for q in qubits:
        #      self._awg.load_sequence(sequencer_code[q[0]], awg_idx=q[0])
        #      self._awg._awgs["awg"+str(q[0]+1)].write_to_waveform_memory(waveforms_awg[q[0]])

        # self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        # self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
        #
        # daq = self._awg._daq
        # dev = self._awg._connection_settings["hdawg_id"]

        # for q in qubits:
        #      i_idx = self._channel_idxs[str(q[0])][0]
        #      q_idx = self._channel_idxs[str(q[0])][1]
        #      osc_idx = self._channel_osc_idxs[str(q[0])]
        #      self._awg._hdawg.sigouts[i_idx].on(1)
        #      self._awg._hdawg.sigouts[q_idx].on(1)
        #      self._awg.set_osc_freq(osc_idx, self._qubit_parameters[int(q[1:len(q)])]["mod_freq"])
        #      self._awg.set_sine(i_idx+1, osc_idx)
        #      self._awg.set_sine(q_idx+1, osc_idx)
        #      self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[int(q[1:len(q)])]["i_amp_pi"])
        #      self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[int(q[1:len(q)])]["q_amp_pi"])
        #      daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_table))

    # def run_program(self, awg_idxs=None):
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = self._awg_idxs
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)

class MultiQubitGST_v4:
    def __init__(self, gst_file_path, awg, qubits = [0,1,2,3], hard_trigger = False, trigger_channel=0):
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  qubits

        self._qubit_parameters = {
        0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        2: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 120e-9,  "tau_pi_2" :  60e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        3: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 160e-9,  "tau_pi_2" :  80e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
        tau_pi_2_set = np.array([self._qubit_parameters[0]["tau_pi_2"], self._qubit_parameters[1]["tau_pi_2"], self._qubit_parameters[2]["tau_pi_2"], self._qubit_parameters[3]["tau_pi_2"]])
        tau_pi_2_standard_idx = np.argmax(tau_pi_2_set)

        ##Define standard length of pulse in time
        tau_pi_2_standard = np.max(tau_pi_2_set)
        tau_pi_standard = 2*tau_pi_2_standard

        ##Define standard length of pulse in number of samples
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32

        ##convert back to time
        tau_pi_2_standard_new = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard_new = npoints_pi_standard/self._sample_rate

        qubit_lengths = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
        qubit_npoints = {0: {"pi": None, "pi_2": None}, 1: {"pi": None, "pi_2": None}, 2: {"pi": None, "pi_2": None}, 3: {"pi": None, "pi_2": None}}
        ##Generates pulse lengths for all qubits
        for idx in qubits:
            qubit_lengths[idx]["pi"] = ceil(tau_pi_standard_new*1e9)
            qubit_lengths[idx]["pi_2"] = ceil(tau_pi_2_standard_new*1e9)
            qubit_npoints[idx]["pi"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi"]/32)*32
            qubit_npoints[idx]["pi_2"] = ceil(self._sample_rate*self._qubit_parameters[idx]["tau_pi_2"]/32)*32

        self._waveforms = generate_waveforms(qubit_npoints, tau_pi_2_standard_idx, amp=1)
        self._gate_sequences = quantum_protocol_parser_Zarb(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})

        ##Command table stuff. loop over number of lines:
        ct_idxs_all = {}
        command_tables = {}

        ##Keeps track of all arbZs for command table
        #arbZs = []
        ##keeps track of number of arbZs
        #n_arbZ = 0
        for idx in self._gate_sequences:
             gate_sequence = self._gate_sequences[idx]
             ##Implement to generate just 1 command table for all lines, all qubits.
             ct_idxs_all[idx], arbZ = make_command_table_idxs_v5(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9))
             #ct_idxs_all[idx], arbZ = make_command_table_idxs_v6(gt_seqs, tau_pi_s, tau_pi_2_s, n_arbZ)
             #n_arbZ += len(arbZ)
             #arbZs.append(arbZ)
             ## Need to change up implementation ==> 1 ct per qubit for all lines.
             command_tables[idx] = generate_reduced_command_table_v4(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ)

        #command_tables = generate_reduced_command_table_v4(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ)
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
            sequence = ""
            for ii in range(len(ct_idxs_all)):
                 n_seq = ct_idxs_all[ii][str(idx)]
                 if hard_trigger == False:
                     seq = make_gateset_sequencer_fast_v2(n_seq)
                 else:
                     if idx == trigger_channel:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=True)
                     else:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=False)
                 sequence += seq

            command_code[idx] = command_code[idx] + sequence
            sequencer_code[idx] =  seq_code[idx] + command_code[idx]

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
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
             daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables[0]))

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)

class MultiQubitGST_v5:
    def __init__(self, gst_file_path, awg, qubits = [0,1,2,3], hard_trigger = False, trigger_channel=0):
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  qubits

        self._qubit_parameters = {
        0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 100e-9,  "tau_pi_2" :  50e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
        1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 140e-9,  "tau_pi_2" :  70e-9,  "delta_iq" : 0 , "mod_freq": 60e6},
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
        self._gate_sequences = quantum_protocol_parser_Zarb(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})

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
            sequence = ""
            for ii in range(len(ct_idxs_all)):
                 n_seq = ct_idxs_all[ii][str(idx)]
                 if hard_trigger == False:
                     seq = make_gateset_sequencer_fast_v2(n_seq)
                 else:
                     if idx == trigger_channel:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=True)
                     else:
                         seq = make_gateset_sequencer_hard_trigger(n_seq, trig_channel=False)
                 sequence += seq

            command_code[idx] = command_code[idx] + sequence
            sequencer_code[idx] =  seq_code[idx] + command_code[idx]

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
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
             daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables))

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_idxs
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)

class MultiQubitRamseyTypes:
    ##should generalize for all qubits ==> only change will be pulse type
    def __init__(self, awg, t_range, npoints_t, npoints_av, taus_pulse, axis = "x", sample_rate = 2.4e9):
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

class MultiQubitRabiTypes:
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
