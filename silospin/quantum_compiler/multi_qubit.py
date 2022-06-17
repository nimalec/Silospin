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
from silospin.quantum_compiler.qc_helpers import make_command_table, make_gateset_sequencer


class MultiQubitGatesSet:
    def __init__(self, gate_strings, awg, qubit_parameters=None, sample_rate=2.4e9, continuous=False, soft_trigger = False, waveforms_preloaded=False, update_qubit_parameters = "0", parameters_path = None):
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
        # 7.
        # 8.

        default_qubit_params = {
        {"0": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  15e-9,  "delta_iq" : 0 , "mod_freq": 60e6}},
        {"1": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  15e-9,  "delta_iq" : 0 , "mod_freq": 60e6}},
        {"2": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  15e-9,  "delta_iq" : 0 , "mod_freq": 60e6}},
        {"3": {"i_amp_pi": 0.5, "q_amp_pi": 0.5 , "i_amp_pi_2": 0.5, "q_amp_pi_2": 0.5, "tau_pi" : 100e-9,  "tau_pi_2" :  15e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}}

        if update_qubit_parameters == "1":
            self._qubit_parameters = qubit_parameters
        elif update_qubit_parameters == "0":
            self._qubit_parameters = default_qubit_params
        elif update_qubit_parameters == "-1":
            ## Add a read csv file (make a helper function for this)
            pass

        awg_cores = []
        for key in gate_strings:
            if gate_strings[key]:
                awg_idx = int(key)
                awg_cores.append(awg_idx)
                self._awg._hdawg.awgs[awg_idx].enable(False)
                ## add line to clear out previous sequence run
            else:
                pass

        waveforms_tau_pi = {}
        waveforms_tau_pi_2 = {}
        waveforms = Waveforms()
        n_array = []
        idx = 0
        if waveforms_preloaded is True:
            pass
        else:
            for awg_idx in awg_cores:
                npoints_tau_pi = ceil(self._sample_rate*self._qubit_parameters[str(idx)]["tau_pi"]/16)*16
                npoints_tau_pi_2 = ceil(self._sample_rate*self._qubit_parameters[str(idx)]["tau_pi_2"]/16)*16
                waveforms_tau_pi[str(idx)] = rectangular(npoints_tau_pi)
                waveforms_tau_pi_2[str(idx)] = rectangular(npoints_tau_pi_2)
                n_array.append(len(waveforms_tau_pi[str(idx)]))
                n_array.append(len(waveforms_tau_pi_2[str(idx)]))
                waveforms.assign_waveform(slot = idx, wave1 = waveforms_tau_pi[str(idx)])
                waveforms.assign_waveform(slot = idx, wave1 = waveforms_tau_pi_2[str(idx)])
                idx += 1
        place_holder_code = make_waveform_placeholders(n_array)
        self._awg.load_sequence(place_holder_code)
        daq = self._awg._daq
        dev = self._awg._connection_settings["hdawg_id"]

        #self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)
        #daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(command_tables[str(awg_idx)]))



     ## write so that gates only need to be calibrated once (only need to keep track of tau_pi, tau_pi_2)
     ## ensure a 4x2 channel grouping
     ## gate_strings: dictionary of gate strings for each AWG core: {"AWG 1": ["x", "t", "x"] , "AWG 2": ["y","t" , "x", "t"]}
    ## awg: awg core
    ## iq_settings: dictionary of dictionaries for IQ settings
    ## tau_pis: dictionary of tau_pi values
    ## tau_pi_2s: dictiorary of tau_pi_2 values


         #
         # channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
         # channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
         #
         # command_tables = {}
         # npoints_tau_pi = {}
         # npoints_tau_pi_2 = {}
         # waves_tau_pi = {}
         # waves_tau_pi_2 = {}
         # n_arrays = {}
         # sequences = {}
         # phase_reset_seq = "resetOscPhase();\n"


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


     def run_program(self, awg_idxs):
         channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
         channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
         for idx in awg_idxs:
             self._awg._hdawg.sigouts[channel_idxs[str(idx)][0]].on(1)
             self._awg._hdawg.sigouts[channel_idxs[str(idx)][1]].on(1)
             self._awg._awgs["awg"+str(idx+1)].single(True)
             self._awg._awgs["awg"+str(idx+1)].enable(True)
