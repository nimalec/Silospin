import numpy as np
import pandas as pd
from math import ceil
import json
import time
from pkg_resources import resource_filename
from zhinst.toolkit import Waveforms
import zhinst.utils
from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular
from silospin.quantum_compiler.qc_helpers import *
from silospin.io.qc_io import read_qubit_paramater_file, write_qubit_parameter_file

class MultiQubitGatesSet:
    def __init__(self, gate_strings, awg, qubit_parameters=None, sample_rate=2.4e9, continuous=False, soft_trigger = False, waveforms_preloaded=False, update_qubit_parameters = "0", qubit_parameters_file_path = "qubit_parameters.csv"):
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
                ct_idxs, n_ts = make_command_table_idxs(gt_seq, sample_rate)
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
            #npoints_tau_pi = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi"]/16)*16
            #npoints_tau_pi_2 = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi_2"]/16)*16
            npoints_tau_pi = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi"])
            npoints_tau_pi_2 = ceil(self._sample_rate*self._qubit_parameters[str(awg_idx)]["tau_pi_2"])
            waveforms_tau_pi[str(awg_idx)] = rectangular(npoints_tau_pi, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
            waveforms_tau_pi_2[str(awg_idx)] = rectangular(npoints_tau_pi_2, self._qubit_parameters [str(awg_idx)]["i_amp_pi_2"])
            n_array.append(len(waveforms_tau_pi[str(awg_idx)]))
            n_array.append(len(waveforms_tau_pi_2[str(awg_idx)]))
            waveforms.assign_waveform(slot = 0, wave1 = waveforms_tau_pi[str(awg_idx)])
            waveforms.assign_waveform(slot = 1, wave1 = waveforms_tau_pi_2[str(awg_idx)])
            print(len(waveforms_tau_pi_2[str(awg_idx)]))
            waveforms_qubits[str(awg_idx)] = waveforms
            seq_code = make_gateset_sequencer_fast(n_array, cts_idxs[str(awg_idx)], continuous=continuous, trigger=soft_trigger)
            self._awg.load_sequence(seq_code, awg_idx=awg_idx)
            self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)

        self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

        #phase_reset_seq = "resetOscPhase();\n"
        daq = self._awg._daq
        dev = self._awg._connection_settings["hdawg_id"]
        for awg_idx in self._awg_idxs:
             i_idx = self._channel_idxs[str(awg_idx)][0]
             q_idx = self._channel_idxs[str(awg_idx)][1]
             osc_idx = self._channel_osc_idxs[str(awg_idx)]
             self._awg._hdawg.sigouts[i_idx].on(0)
             self._awg._hdawg.sigouts[q_idx].on(0)
             self._awg.set_osc_freq(osc_idx, self._qubit_parameters[str(awg_idx)]["mod_freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[str(awg_idx)]["i_amp_pi"])
             self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[str(awg_idx)]["q_amp_pi"])
             #self._awg.load_sequence(phase_reset_seq, awg_idx)
             #self._awg._awgs["awg"+str(awg_idx+1)].single(True)
             #self._awg._awgs["awg"+str(awg_idx+1)].enable(True)
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
             self._awg._hdawg.sigouts[i_idx].on(0)
             self._awg._hdawg.sigouts[q_idx].on(0)
             self._awg._hdawg.sigouts[i_idx].on(1)
             self._awg._hdawg.sigouts[q_idx].on(1)
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
            #self._awg._hdawg.sigouts[self._channel_idxs[str(idx)][0]].on(1)
            #self._awg._hdawg.sigouts[self._channel_idxs[str(idx)][1]].on(1)
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)
