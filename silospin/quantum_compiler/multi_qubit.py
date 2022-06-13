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
     def __init__(self, gate_strings, awg, iq_settings=None, sample_rate=2.4e9, taus_pi = None, taus_pi_2 = None, continuous=False, trigger = False):
         ##ensure 4x2 channel grouping
         ##
         ##

         ## gate_strings: dictionary of gate strings for each AWG core: {"AWG 1": ["x", "t", "x"] , "AWG 2": ["y","t" , "x", "t"]}
         ## awg: awg core
         ##iq_settings: dictionary of dictionaries for IQ settings
         ##tau_pis: dictionary of tau_pi values
         ##tau_pi_2s: dictiorary of tau_pi_2 values

        # iq_settings =
         #if iq_settings is not None:
        #     self._iq_settings = iq_settings
         #else:
         self._iq_settings = {"0": {"i_sin": 1, "q_sin": 2, "i_out": 1, "q_out": 2, "iq_offset": 0, "osc": 1, "freq": 60e6 , "i_amp": 0.5, "q_amp": 0.5},
             "1": {"i_sin": 1, "q_sin": 2, "i_out": 1, "q_out": 2, "iq_offset": 0, "osc": 1, "freq": 60e6 , "i_amp": 0.5, "q_amp": 0.5},
             "2": {"i_sin": 1, "q_sin": 2, "i_out": 1, "q_out": 2, "iq_offset": 0, "osc": 1, "freq": 60e6 , "i_amp": 0.5, "q_amp": 0.5},
             "3": {"i_sin": 1, "q_sin": 2, "i_out": 1, "q_out": 2, "iq_offset": 0, "osc": 1, "freq": 60e6 , "i_amp": 0.5, "q_amp": 0.5}}


         tau_pi_default = 200e-9
         tau_pi_2_default = 100e-9
         #if taus_pi is not None:
    #         self._taus_pi = taus_pi
         #else:
         self._taus_pi = {"0": tau_pi_default, "1": tau_pi_default, "2": tau_pi_default, "3": tau_pi_default}

         #if taus_pi_2 is not None:
        #     self._taus_pi_2 = taus_pi_2
         #else:
         self._taus_pi_2 = {"0": tau_pi_2_default, "1": tau_pi_2_default, "2": tau_pi_2_default, "3": tau_pi_2_default}

         self._gate_strings = gate_strings
         self._awg = awg

         awg_cores = []
         for key in gate_strings:
             if gate_strings[key]:
                 awg_idx = int(key)
                 awg_cores.append(awg_idx)
                 self._awg._hdawg.awgs[awg_idx].enable(False)
             else:
                 pass

         self._sample_rate = sample_rate
         channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
         channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

         command_tables = {}
         npoints_tau_pi = {}
         npoints_tau_pi_2 = {}
         waves_tau_pi = {}
         waves_tau_pi_2 = {}
         n_arrays = {}
         sequences = {}
         phase_reset_seq = "resetOscPhase();\n"

         for awg_idx in awg_cores:
             i_idx = channel_idxs[str(awg_idx)][0]
             q_idx = channel_idxs[str(awg_idx)][1]
             osc_idx = channel_osc_idxs[str(awg_idx)]
             self._awg._hdawg.sigouts[i_idx].on(0)
             self._awg._hdawg.sigouts[q_idx].on(0)
             self._awg.set_osc_freq(osc_idx, self._iq_settings[str(awg_idx)]["freq"])
             self._awg.set_sine(i_idx+1, osc_idx)
             self._awg.set_sine(q_idx+1, osc_idx)
             self._awg.set_out_amp(self._iq_settings[str(awg_idx)]["i_sin"], 1, self._iq_settings[str(awg_idx)]["i_amp"])
             self._awg.set_out_amp(self._iq_settings[str(awg_idx)]["q_sin"], 2, self._iq_settings[str(awg_idx)]["q_amp"])
             command_tables[str(awg_idx)] = make_command_table(self._gate_strings[str(awg_idx)], self._iq_settings[str(awg_idx)], self._sample_rate)
             npoints_tau_pi[str(awg_idx)] = ceil(self._sample_rate*self._taus_pi[str(awg_idx)]/48)*48
             npoints_tau_pi_2[str(awg_idx)] = ceil(self._sample_rate*self._taus_pi_2[str(awg_idx)]/48)*48
             waves_tau_pi[str(awg_idx)] = rectangular(npoints_tau_pi[str(awg_idx)], 0.5)
             waves_tau_pi_2[str(awg_idx)] = rectangular(npoints_tau_pi_2[str(awg_idx)], 0.5)

             n_array = []
             for gt in self._gate_strings:
                 if gt in {"x", "y", "xxx", "yyy"}:
                     n_array.append(npoints_tau_pi_2[str(awg_idx)])
                 elif gt in  {"xx", "yy", "mxxm", "myym"}:
                     n_array.append(npoints_tau_pi[str(awg_idx)])
                 else:
                     pass

             n_arrays[str(awg_idx)] = n_array

             self._awg.load_sequence(phase_reset_seq, awg_idx)
             self._awg._awgs["awg"+str(awg_idx+1)].single(True)
             self._awg._awgs["awg"+str(awg_idx+1)].enable(True)
             sequences[str(awg_idx)] = make_gateset_sequencer(n_arrays[str(awg_idx)], len(self._gate_strings[str(awg_idx)]) , continuous=continuous, trigger=trigger)
             self._awg.load_sequence(sequences[str(awg_idx)])

         self._sequence_code = sequences

         daq = self._awg._daq
         dev = self._awg._connection_settings["hdawg_id"]
         waveforms_awgs = {}
         for awg_idx in awg_cores:
             waveforms = Waveforms()
             ii = 0
             for gt in self._gate_strings:
                 if gt in {"x", "y", "xxx", "yyy"}:
                     waveforms.assign_waveform(slot = ii, wave1 = waves_tau_pi_2[str(awg_idx)])
                     ii += 1

                 elif gt in  {"xx", "yy", "mxxm", "myym"}:
                     waveforms.assign_waveform(slot = ii, wave1 =waves_tau_pi[str(awg_idx)])
                     ii += 1
                 else:
                     pass
             #waveforms_awgs[waves_tau_pi[str(awg_idx)]] = waveforms
             self._awg._awgs["awg"+str(awg_idx+1)].write_to_waveform_memory(waveforms)
             daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(command_tables[str(awg_idx)]))

         self._waveforms =  waveforms_awgs


     def run_program(self, awg_idxs):
         channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
         channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
         for idx in awg_idxs:
             self._awg._hdawg.sigouts[channel_idxs[str(idx)][0]].on(1)
             self._awg._hdawg.sigouts[channel_idxs[str(idx)][0]].on(1)
             self._awg._awgs["awg"+str(idx+1)].single(True)
             self._awg._awgs["awg"+str(idx+1)].enable(True)
