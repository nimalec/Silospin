import numpy as np
import pandas as pd
import os
from math import ceil
import json
import time
from operator import itemgetter
from pkg_resources import resource_filename
from zhinst.toolkit import Waveforms
import zhinst.utils
import zhinst.core
import zhinst.utils
from silospin.drivers.zi_hdawg_driver_v2 import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular
from silospin.quantum_compiler.quantum_compiler_helpers_v2 import *
from silospin.quantum_compiler.quantum_compiler_io import *
from silospin.quantum_compiler.quantum_compiler_io_v2 import *

##Modifications:
##1. Keep track of redundant Z gates
##2. Account for arbitrary waveforms
##3. Account for 2 HDAWG cores
##4. Arbitrary parameter sweeps

## QC should take in a flag for reconfiguring AWG settings.
## Store AWG channel map in a pickle file
## New channel mapping function ==>  {AWG1:  , AWG2: }
class GateSetTomographyQuantumCompiler:
    """
    Class representing an instance of compiler gate set tomography experiment (uses entirely rectangular waves).

    Attributes
    ----------
    _gst_path : str
        File path for gate set tomography program being read and compiled.
    _awg : HdawgDriver
        Instance of HdawgDriver object, native to silospin.
    _sample_rate : float
        Sampling rate used by AWG. Set to 2.4 GSa/s
    _awg_cores : list
        List of indcices corresponding to the qubits (AWG cores) used in the program.
    _qubit_parameters : dict
        Dictionary of standard parameters for each qubit. Dicionary keys correspond to qubit (AWG core) indices and value is dictonary of qubit parameters (["i_amp_pi", "q_amp_pi", "i_amp_pi_2", "q_amp_pi_2", "tau_pi",  "tau_pi_2", "delta_iq", "mod_freq"]).
    _waveforms : dict
        Dictionary of rectangular 'pi' and 'pi/2' waveforms to be uploaded to each core of HDAWG. Dict keys correspond to qubit (AWG core) indices. Values are 2 element lists containing waveforms in the form of numpy arrays (['pi/2', 'pi']).
    _gate_sequences : dict
        Dictionary of quantum gate sequences for each AWG core read in from GST file. Outer dictonary keys correspond to GST line number. Inner keys correspond to qubit (AWG core) indices and values are lists of gate strings.
    _ct_idxs : dict
        Dictionary of command table entries executed in HDAWG FPGA sequencer. Outer dictonary keys correspond to GST line number. Inner keys correspond to qubit (AWG core) indices and values are lists of gate strings.
    _command_tables : dict
        Command table uplaoded to HDAWG containing phase change instructions for each gate.
    _sequencer_code : dict
        Dictionary of sequencer code uploaded to each HDAWG coer.
    _channel_idxs : dict
        Grouping of channel indices for  each core.
    _channel_osc_idxs : dict
        Grouping of oscillator indices for  each core.
    """
    def __init__(self, gst_file_path, awgs, gate_parameters, n_inner=1, n_outer=1, added_padding=0, config_awg=True):
        """
        Constructor method for CompileGateSetTomographyProgram.
        Parameters:
            gst_file_path : str
                File path for gate set tomography program being read and compiled.
            awgs : dict
                Dictionary of HdawgDriver instances.
            n_inner : int
                Number of inner frames (for each line in GST file) to loop over.
            n_outer : int
                Number of outer frames (over entire GST file) to loop over.
            trigger_channels : dict
                Dictionary of trigger channels per HDAWG unit use (trigger_channels={"hdawg1":0,"hdawg2":0}).
            qubit_parameters : dict
                Dictionary of standard parameters for each qubit. Dicionary keys correspond to qubit (AWG core) indices and value is dictonary of qubit parameters (["i_amp_pi", "q_amp_pi", "i_amp_pi_2", "q_amp_pi_2", "tau_pi",  "tau_pi_2", "delta_iq", "mod_freq"]).
            external_trigger : bool
                True if an external hardware trigger is used. False if the instrument's internal trigger is used.
            trigger_channel : int
                Trigger channel used if external_trigger = True.
            sample_rate : float
                Sample rate of AWG in Sa/s.
        """

        sample_rate = 2.4e9 ##add to pickle
        self._gst_path = gst_file_path
        self._awgs = awgs
        channel_mapping = self._awgs["hdawg1"]._channel_mapping
        awg_core_split = self._awgs["hdawg1"]._hdawg_core_split
        arb_dc_waveforms_dict = {}
        self._channel_mapping = channel_mapping

        rf_cores = []
        plunger_channels = []
        for awg in channel_mapping:
            arb_dc_waveforms_dict[awg] = {}
            for idx in channel_mapping[awg]:
                arb_dc_waveforms_dict[awg][idx] = {}
                if channel_mapping[awg][idx]['rf'] == 1:
                    rf_cores.append((awg, channel_mapping[awg][idx]['core_idx']))
                else:
                    plunger_channels.append((awg, channel_mapping[awg][idx]['gate_idx'][0]))
                    plunger_channels.append((awg, channel_mapping[awg][idx]['gate_idx'][1]))


        self._gate_parameters = {}
        gate_param_all_rf = gate_parameters["rf"]
        gate_param_all_dc = gate_parameters["p"]

        for awg in channel_mapping:
            self._gate_parameters[awg] = {"rf": {} , "p": {}}
        for gt_idx in gate_param_all_rf:
            self._gate_parameters[awg_core_split[gt_idx][0]]["rf"][gt_idx] = gate_param_all_rf[gt_idx]
        for gt_idx in gate_param_all_dc:
            self._gate_parameters[awg_core_split[gt_idx][0]]["p"][gt_idx] = gate_param_all_dc[gt_idx]

        if config_awg:
            for awg in self._awgs:
                config_hdawg(self._awgs[awg], self._gate_parameters[awg], channel_mapping[awg])
        else:
            pass

        tau_pi_2_set = []
        for idx in gate_parameters["rf"]:
            tau_pi_2_set.append((idx, gate_parameters["rf"][idx]["tau_pi_2"]))
        tau_pi_2_standard_1 = max(tau_pi_2_set,key=itemgetter(1))[1]
        tau_pi_standard_1 = 2*tau_pi_2_standard_1
        standard_rf_idx = max(tau_pi_2_set,key=itemgetter(1))[0]
        npoints_pi_2_standard = ceil(sample_rate*tau_pi_2_standard_1*1e-9/16)*16
        npoints_pi_standard = ceil(sample_rate*tau_pi_standard_1*1e-9/16)*16
        tau_pi_2_standard = npoints_pi_2_standard/sample_rate
        tau_pi_standard = npoints_pi_standard/sample_rate

        plunger_set = []
        plunger_set_npoints = []
        plunger_set_npoints_tups = []
        for idx in gate_parameters["p"]:
            plunger_set.append((idx, gate_parameters["p"][idx]["tau"]))
            plunger_set_npoints.append(ceil(gate_parameters["p"][idx]["tau"]*2.4/16)*16)
            plunger_set_npoints_tups.append((idx, ceil(gate_parameters["p"][idx]["tau"]*2.4/16)*16))
        hdawg_std_rf = awg_core_split[standard_rf_idx][0]
        npoints_p_standard = max(plunger_set_npoints)

        for core_idx in channel_mapping[hdawg_std_rf]:
            if channel_mapping[hdawg_std_rf][core_idx]['core_idx'] == standard_rf_idx:
                core_std_rf = core_idx
            else:
                pass

        standard_rf = (hdawg_std_rf, standard_rf_idx)
        n_std = (npoints_pi_2_standard, npoints_pi_standard, npoints_p_standard)



        try:
         if added_padding > 5e-9:
            raise TypeError("Padding should not exceed 5 ns!!")
        except TypeError:
            raise

        self._gate_npoints = {}
        for awg in self._gate_parameters:
            self._gate_npoints[awg] = make_gate_npoints(self._gate_parameters[awg], sample_rate)
        #self._waveforms = generate_waveforms_v2(self._gate_npoints, channel_mapping, added_padding, standard_rf)
        self._waveforms = generate_waveforms_v3(self._gate_npoints, channel_mapping, added_padding, standard_rf, n_std)

        dc_lengths = {}
        for awg in channel_mapping:
            for core_idx in channel_mapping[awg]:
                if channel_mapping[awg][core_idx]['rf'] == 1:
                    tau_waveform_pi_2_std  = ceil(1e9*len(self._waveforms[awg][core_idx]["pi_2_pi_2fr"])/sample_rate)
                    tau_waveform_pi_std  = ceil(1e9*len(self._waveforms[awg][core_idx]["pi_pifr"])/sample_rate)

                elif channel_mapping[awg][core_idx]['rf'] == 0:
                    ch_idx_1 = channel_mapping[awg][core_idx]['gate_idx'][0]
                    ch_idx_2 = channel_mapping[awg][core_idx]['gate_idx'][1]
                    ch_idx_1_key = 'p'+str(ch_idx_1)+'_p'+str(ch_idx_1)+'fr'
                    ch_idx_2_key = 'p'+str(ch_idx_2)+'_p'+str(ch_idx_2)+'fr'
                    dc_lengths[ch_idx_1] =  ceil(1e9*len(self._waveforms[awg][core_idx][ch_idx_1_key])/(sample_rate*16))*16
                    dc_lengths[ch_idx_2] = ceil(1e9*len(self._waveforms[awg][core_idx][ch_idx_2_key])/(sample_rate*16))*16
                else:
                    pass

        self._gate_lengths = make_gate_lengths_v2(dc_lengths, tau_waveform_pi_2_std, tau_waveform_pi_std, channel_mapping)

        self._gate_sequences, arbitrary_gates, arbitrary_waveforms, arbitrary_z = gst_file_parser_v3(self._gst_path, self._gate_lengths, channel_mapping, awg_core_split, sample_rate=sample_rate)
        self._arb_waveforms_all = arbitrary_waveforms
        for awg_idx in arb_dc_waveforms_dict:
            for core_idx in arb_dc_waveforms_dict[awg_idx]:
                for line in range(len(self._gate_sequences)):
                    arb_dc_waveforms_dict[awg_idx][core_idx][line+1] = {}


        dc_gate_sequences = {}
        dc_arb_gates = {}
        for line in self._gate_sequences:
            dc_arb_gates[line] = {}
            dc_gate_sequences[line] = self._gate_sequences[line]['plunger']
            for dc_idx in dc_gate_sequences[line]:
                itr = 0
                for gt in dc_gate_sequences[line][dc_idx]:
                    if gt.find('*') != -1:
                        dc_arb_gates[line][itr] = {}
                        for dc_gt_idx in dc_gate_sequences[line]:
                            dc_arb_gates[line][itr][dc_gt_idx] = dc_gate_sequences[line][dc_gt_idx][itr]
                    else:
                        pass
                    itr += 1


        for line in dc_arb_gates:
            for idx in dc_arb_gates[line]:
                for dc_idx in dc_arb_gates[line][idx]:
                    awg_idx = awg_core_split[dc_idx][0]
                    core_idx = awg_core_split[dc_idx][1]

                    if dc_arb_gates[line][idx][dc_idx][0] != 't':
                        if dc_idx%2 != 0:
                            wave1 = dc_arb_gates[line][idx][dc_idx]
                            wave2 = dc_arb_gates[line][idx][dc_idx+1]
                        else:
                            wave1 = dc_arb_gates[line][idx][dc_idx-1]
                            wave2 = dc_arb_gates[line][idx][dc_idx]
                        arb_dc_waveforms_dict[awg_idx][core_idx][line][idx] = (wave1, wave2)
                    else:
                        pass

        self._arb_dc_waveforms_dict = arb_dc_waveforms_dict

        arb_dc_waveforms_dict_temp = {}
        for awg_idx in self._arb_dc_waveforms_dict:
            arb_dc_waveforms_dict_temp[awg_idx]  = {}
            for core_idx in self._arb_dc_waveforms_dict[awg_idx]:
                arb_dc_waveforms_dict_temp[awg_idx][core_idx] = {}
                ct_idx = 0
                for line in self._arb_dc_waveforms_dict[awg_idx][core_idx]:
                    arb_dc_waveforms_dict_temp[awg_idx][core_idx][line] = {}
                    if len(self._arb_dc_waveforms_dict[awg_idx][core_idx][line]) == 0:
                        pass
                    else:
                        for idx in self._arb_dc_waveforms_dict[awg_idx][core_idx][line]:
                            ct_idx += 1
                            tup = self._arb_dc_waveforms_dict[awg_idx][core_idx][line][idx]
                            arb_dc_waveforms_dict_temp[awg_idx][core_idx][line][idx] = (tup, ct_idx)


        self._command_tables = {}
        arbgate_counter = {}
        for awg_idx in channel_mapping:
            self._command_tables[awg_idx] = {}
            arbgate_counter[awg_idx] = {}
            for core_idx in channel_mapping[awg_idx]:
                arbgate_counter[awg_idx][core_idx] = 0
                if channel_mapping[awg_idx][core_idx]['rf'] == 1:
                    self._command_tables[awg_idx][core_idx] = make_rf_command_table_v2(n_std, arbitrary_z, arbitrary_waveforms, plunger_set_npoints_tups, awg_idx, core_idx)
                else:
                    self._command_tables[awg_idx][core_idx] = make_dc_command_table_v3(n_std, arbitrary_waveforms, plunger_set_npoints_tups, awg_idx, core_idx, self._arb_dc_waveforms_dict)

        ct_idxs_all = {}
        taus_std = (tau_waveform_pi_2_std, tau_waveform_pi_std)
        for idx in self._gate_sequences:
            gate_sequence = self._gate_sequences[idx]
            ct_idxs, arbgate_counter = make_command_table_indices_v4(gate_sequence, channel_mapping, awg_core_split, arbitrary_waveforms, plunger_set_npoints_tups, taus_std, self._gate_lengths, arbgate_counter, arbitrary_z, idx, arb_dc_waveforms_dict_temp)
            ct_idxs_all[idx] = ct_idxs
        self._ct_idxs_all = ct_idxs_all
        ##Note: need to modify waveforms function to adapt for size

        # Make a dict for each core following channel groupign
        waveform_lengths = {}
        waveforms_awg = {}
        waveforms_to_awg = {}
        sequencer_code = {}
        for awg_idx in channel_mapping:
            waveform_lengths[awg_idx] = {}
            waveforms_awg[awg_idx] = {}
            waveforms_to_awg[awg_idx] = {}
            sequencer_code[awg_idx] = {}
            for core_idx in channel_mapping[awg_idx]:
                wave_idx = 0
                waveform_lengths[awg_idx][core_idx] = {}
                waveforms_awg[awg_idx][core_idx] = {}
                waveforms_to_awg[awg_idx][core_idx] = {}
                sequencer_code[awg_idx][core_idx] = {}
                waveforms = Waveforms()
                non_arb_waves = self._waveforms[awg_idx][core_idx]
                if channel_mapping[awg_idx][core_idx]['rf'] == 1:
                    ##First assign non_arb, then assign arb
                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(self._waveforms[awg_idx][core_idx]['pi_pifr']))
                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(self._waveforms[awg_idx][core_idx]['pi_pifr']), self._waveforms[awg_idx][core_idx]['pi_pifr']))
                     waveform_lengths[awg_idx][core_idx][wave_idx] = (len(np.array(self._waveforms[awg_idx][core_idx]['pi_pifr'])), len(np.array(self._waveforms[awg_idx][core_idx]['pi_pifr'])))
                     wave_idx += 1
                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(self._waveforms[awg_idx][core_idx]['pi_2_pifr']))
                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(self._waveforms[awg_idx][core_idx]['pi_2_pifr']), self._waveforms[awg_idx][core_idx]['pi_2_pifr']))
                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_pifr'])), len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_pifr'])))
                     wave_idx += 1
                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(self._waveforms[awg_idx][core_idx]['pi_2_pi_2fr']))
                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(self._waveforms[awg_idx][core_idx]['pi_2_pi_2fr']), self._waveforms[awg_idx][core_idx]['pi_2_pi_2fr']))
                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_pi_2fr'])), len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_pi_2fr'])))
                     wave_idx += 1
                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(self._waveforms[awg_idx][core_idx]['pi_p_stdfr']))
                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(self._waveforms[awg_idx][core_idx]['pi_p_stdfr']), self._waveforms[awg_idx][core_idx]['pi_p_stdfr']))
                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(np.array(self._waveforms[awg_idx][core_idx]['pi_p_stdfr'])), len(np.array(self._waveforms[awg_idx][core_idx]['pi_p_stdfr'])))
                     wave_idx += 1
                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(self._waveforms[awg_idx][core_idx]['pi_2_p_stdfr']))
                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(self._waveforms[awg_idx][core_idx]['pi_2_p_stdfr']), self._waveforms[awg_idx][core_idx]['pi_2_p_stdfr']))
                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_p_stdfr'])), len(np.array(self._waveforms[awg_idx][core_idx]['pi_2_p_stdfr'])))
                     wave_idx += 1

                     if len(self._arb_waveforms_all[awg_idx][core_idx]) == 0:
                         pass
                     else:
                         for arbwav in self._arb_waveforms_all[awg_idx][core_idx]:
                             waveforms.assign_waveform(slot = wave_idx, wave1 = np.array(arbwav[1]))
                             waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(np.array(arbwav[1]),np.array(arbwav[1]))
                             waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(np.array(arbwav[1])), len(np.array(arbwav[1])))
                             wave_idx += 1
                     waveforms_awg[awg_idx][core_idx] = waveforms

                else:
                    arb_waveforms = self._arb_dc_waveforms_dict[awg_idx][core_idx]
                    channel_idxs_core = channel_mapping[awg_idx][core_idx]['channel_number']
                    plunger_idxs = list(self._gate_lengths['plunger'].keys())
                    ## Str1  == 'p'+channel_idxs_core[0]+'_p'+str(wave_idx)+'fr'
                    ## Str2   == 'p'+channel_idxs_core[1]+'_p'+str(wave_idx)+'fr'
                    ## Order:
                    ## 1. [(p1)_1, 0]...[(p1)_N, 0]
                    ## 2. [0, (p2)_1]...[0, (p2)_N]
                    ## 3.[(p1)_1, (p2)_1]...[(p1)_N, (p2)_N]
                    ## 4. [(p1)_pi, 0]
                    ## 5.  [0, (p2)_pi]
                    ## 6. [(p1)_pi/2, 0]
                    ## 7. [0, (p2)_pi/2]
                    ## 8. [(p1)_pi, (p2)_pi]
                    ## 9. [(p1)_pi/2, (p2)_pi/2]
                    ## 10. arbitrary gates

                    ## 1. [(p1)_1, 0]...[(p1)_N, 0]
                    for i in plunger_idxs:
                        wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_p'+str(i)+'fr'])
                        waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, np.zeros(len(wave_1)))
                        waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = np.zeros(len(wave_1)))
                        waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                        wave_idx += 1
                    ## 2. [0, (p2)_1]...[0, (p2)_N]
                    for i in plunger_idxs:
                        wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_p'+str(i)+'fr'])
                        waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(np.zeros(len(wave_2)), wave_2)
                        waveforms.assign_waveform(slot = wave_idx, wave1 = np.zeros(len(wave_2)), wave2 = wave_2)
                        waveform_lengths[awg_idx][core_idx][wave_idx] = (len(wave_2),len(wave_2))
                        wave_idx += 1
                    ## 3.[(p1)_1, (p2)_1]...[(p1)_N, (p2)_N]
                    for i in plunger_idxs:
                    #    print('p'+str(channel_idxs_core[0])+'_p'+str(i)+'fr','p'+str(channel_idxs_core[1])+'_p'+str(i)+'fr')
                        wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_p'+str(i)+'fr'])
                        wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_p'+str(i)+'fr'])
                        waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, wave_2)
                        # print('p'+str(channel_idxs_core[0])+'_p'+str(i)+'fr', len(wave_1))
                        # print('p'+str(channel_idxs_core[1])+'_p'+str(i)+'fr', len(wave_2))
                        waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                        waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = wave_2)
                        wave_idx += 1
                    ## 4. [(p1)_pi, 0]
                    wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_pifr'])
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, np.zeros(len(wave_1)))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = np.zeros(len(wave_1)))
                    wave_idx += 1
                    ## 5. [0, (p2)_pi]
                    wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_pifr'])
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(np.zeros(len(wave_2))), wave_2)
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_2),len(wave_2))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = np.zeros(len(wave_2)), wave2 = wave_2)
                    wave_idx += 1
                    ## 6. [(p1)_pi/2, 0]
                    wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_pi_2fr'])
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, np.zeros(len(wave_1)))
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = np.zeros(len(wave_1)))
                    wave_idx += 1
                    ## 7. [0, (p2)_pi/2]
                    wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_pi_2fr'])
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(np.zeros(len(wave_2)), wave_2)
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_2),len(wave_2))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = np.zeros(len(wave_2)), wave2 = wave_2)
                    wave_idx += 1
                    ## 8. [(p1)_pi, (p2)_pi]
                    wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_pifr'])
                    wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_pifr'])
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, wave_2)
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = wave_2)
                    wave_idx += 1
                    ## 9. [(p1)_pi/2, (p2)_pi/2]
                    wave_1 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[0])+'_pi_2fr'])
                    wave_2 = np.array(self._waveforms[awg_idx][core_idx]['p'+str(channel_idxs_core[1])+'_pi_2fr'])
                    waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, wave_2)
                    waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                    waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = wave_2)
                    wave_idx += 1
                   ## 10. arbitrary gates
                    for line in arb_waveforms:
                        if len(arb_waveforms[line]) == 0:
                            pass
                        else:
                            for itr in arb_waveforms[line]:
                                 gate_tup = arb_waveforms[line][itr]
                                 if gate_tup[0][0] == 't':
                                     wave_2 = evaluate_arb_waveform(gate_tup[1])
                                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(np.zeros(len(wave_2)), wave_2)
                                     waveforms.assign_waveform(slot = wave_idx, wave1 = np.zeros(len(wave_2)), wave2 = wave_2)
                                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_2),len(wave_2))
                                     wave_idx += 1

                                 elif gate_tup[1][0] == 't':
                                     wave_1 = evaluate_arb_waveform(gate_tup[0])
                                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1,  np.zeros(len(wave_1))
                                     waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = np.zeros(len(wave_1)))
                                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                                     wave_idx += 1

                                 else:
                                     wave_1 = evaluate_arb_waveform(gate_tup[0])
                                     wave_2 = evaluate_arb_waveform(gate_tup[1])
                                     waveforms_to_awg[awg_idx][core_idx][wave_idx] = zhinst.utils.convert_awg_waveform(wave_1, wave_2)
                                     waveforms.assign_waveform(slot = wave_idx, wave1 = wave_1, wave2 = wave_2)
                                     waveform_lengths[awg_idx][core_idx][wave_idx] =  (len(wave_1),len(wave_1))
                                     wave_idx += 1
                    waveforms_awg[awg_idx][core_idx] = waveforms


        sequencer_code = {}
        seq_code = {}
        command_code = {}

        for awg_idx in self._channel_mapping:
            sequencer_code[awg_idx] = {}
            command_code[awg_idx] = {}
            seq_code[awg_idx] = {}
            for core_idx in self._channel_mapping[awg_idx]:
                seq_code[awg_idx][core_idx] = make_waveform_placeholders_v2(waveform_lengths[awg_idx][core_idx])
                command_code[awg_idx][core_idx] = ""
                sequence = "repeat("+str(n_outer)+"){\n "
                for line in range(len(self._ct_idxs_all)):
                    n_seq = self._ct_idxs_all[line+1][awg_idx][core_idx]
                    if self._channel_mapping[awg_idx][core_idx]['trig_channel'][0] == 1  or self._channel_mapping[awg_idx][core_idx]['trig_channel'][1] == 1:
                        seq = make_gateset_sequencer_hard_trigger_v2(n_seq, n_inner, trig_channel=True)
                    else:
                        seq = make_gateset_sequencer_hard_trigger_v2(n_seq, n_inner, trig_channel=False)
                    sequence += seq
                command_code[awg_idx][core_idx] = command_code[awg_idx][core_idx] + sequence
                sequencer_code[awg_idx][core_idx] = seq_code[awg_idx][core_idx] + command_code[awg_idx][core_idx]+ "}"

        self._sequencer_code = sequencer_code
        for awg_idx in self._channel_mapping:
            for core_idx in self._channel_mapping[awg_idx]:
                daq = self._awgs[awg_idx]._daq
                device_id = self._awgs[awg_idx]._connection_settings["hdawg_id"]
                device_type = daq.getString(f"/{device_id}/features/devtype")
                samplerate = daq.getDouble(f"/{device_id}/system/clocks/sampleclock/freq")
                elf, compiler_info = zhinst.core.compile_seqc(self._sequencer_code[awg_idx][core_idx], devtype=device_type, samplerate=samplerate, index = core_idx-1)
                daq.setVector(f"/{device_id}/awgs/"+str(core_idx-1)+"/elf/data", elf)
                daq.setVector(f"/{device_id}/awgs/"+str(core_idx-1)+"/commandtable/data", json.dumps(self._command_tables[awg_idx][core_idx]))



        for awg_idx in self._channel_mapping:
            for core_idx in self._channel_mapping[awg_idx]:
                daq = self._awgs[awg_idx]._daq
                device_id = self._awgs[awg_idx]._connection_settings["hdawg_id"]
                daq.setVector(f"/{device_id}/awgs/"+str(core_idx-1)+"/elf/data", elf)
                daq.setVector(f"/{device_id}/awgs/"+str(core_idx-1)+"/commandtable/data", json.dumps(self._command_tables[awg_idx][core_idx]))
        # 
        # for awg_idx in self._channel_mapping:
        #     for core_idx in self._channel_mapping[awg_idx]:
        #         for wave in

    #     for idx in range(0,4):
    #         self._awg.load_sequence(self._sequencer_code[idx+1], awg_idx=idx)
    #         self._awg._awgs["awg"+str(idx+1 )].write_to_waveform_memory(waveforms_awg[idx+1])
    #
    #     for idx in rf_cores:
    #           daq.setVector(f"/{dev}/awgs/{idx-1}/commandtable/data", json.dumps(self._command_tables['rf']))
    #     p_idx = 3
    #     daq.setVector(f"/{dev}/awgs/{p_idx}/commandtable/data", json.dumps(self._command_tables['plunger']))
    #
    # def run_program(self, awg_idxs=None):
    #     """
    #      Runs uploaded quantum algorithm on the specified AWG cores.
    #
    #      Waits for external hardware trigger event to execute program.
    #
    #      Parameters
    #      ----------
    #      awg_idxs : 'list'
    #      List of awg_idxs (default set to [0,1,2,3]) to run.
    #
    #      Returns
    #      -------
    #      None.
    #     """
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = [0,1,2,3]
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)


class GateSetTomographyQuantumCompiler_v2:
    """
    Class representing an instance of compiler gate set tomography experiment (uses entirely rectangular waves).

    Attributes
    ----------
    _gst_path : str
        File path for gate set tomography program being read and compiled.
    _awg : HdawgDriver
        Instance of HdawgDriver object, native to silospin.
    _sample_rate : float
        Sampling rate used by AWG. Set to 2.4 GSa/s
    _awg_cores : list
        List of indcices corresponding to the qubits (AWG cores) used in the program.
    _qubit_parameters : dict
        Dictionary of standard parameters for each qubit. Dicionary keys correspond to qubit (AWG core) indices and value is dictonary of qubit parameters (["i_amp_pi", "q_amp_pi", "i_amp_pi_2", "q_amp_pi_2", "tau_pi",  "tau_pi_2", "delta_iq", "mod_freq"]).
    _waveforms : dict
        Dictionary of rectangular 'pi' and 'pi/2' waveforms to be uploaded to each core of HDAWG. Dict keys correspond to qubit (AWG core) indices. Values are 2 element lists containing waveforms in the form of numpy arrays (['pi/2', 'pi']).
    _gate_sequences : dict
        Dictionary of quantum gate sequences for each AWG core read in from GST file. Outer dictonary keys correspond to GST line number. Inner keys correspond to qubit (AWG core) indices and values are lists of gate strings.
    _ct_idxs : dict
        Dictionary of command table entries executed in HDAWG FPGA sequencer. Outer dictonary keys correspond to GST line number. Inner keys correspond to qubit (AWG core) indices and values are lists of gate strings.
    _command_tables : dict
        Command table uplaoded to HDAWG containing phase change instructions for each gate.
    _sequencer_code : dict
        Dictionary of sequencer code uploaded to each HDAWG coer.
    _channel_idxs : dict
        Grouping of channel indices for  each core.
    _channel_osc_idxs : dict
        Grouping of oscillator indices for  each core.
    """
    def __init__(self, gst_file_path, awgs, gate_parameters, n_inner=1, n_outer=1, added_padding=0, config_awg=True):
        """
        Constructor method for CompileGateSetTomographyProgram.
        Parameters:
            gst_file_path : str
                File path for gate set tomography program being read and compiled.
            awgs : dict
                Dictionary of HdawgDriver instances.
            n_inner : int
                Number of inner frames (for each line in GST file) to loop over.
            n_outer : int
                Number of outer frames (over entire GST file) to loop over.
            trigger_channels : dict
                Dictionary of trigger channels per HDAWG unit use (trigger_channels={"hdawg1":0,"hdawg2":0}).
            qubit_parameters : dict
                Dictionary of standard parameters for each qubit. Dicionary keys correspond to qubit (AWG core) indices and value is dictonary of qubit parameters (["i_amp_pi", "q_amp_pi", "i_amp_pi_2", "q_amp_pi_2", "tau_pi",  "tau_pi_2", "delta_iq", "mod_freq"]).
            external_trigger : bool
                True if an external hardware trigger is used. False if the instrument's internal trigger is used.
            trigger_channel : int
                Trigger channel used if external_trigger = True.
            sample_rate : float
                Sample rate of AWG in Sa/s.
        """

        sample_rate = 2.4e9 ##add to pickle
        self._gst_path = gst_file_path
        self._awgs = awgs
        channel_mapping = self._awgs["hdawg1"]._channel_mapping
        awg_core_split = self._awgs["hdawg1"]._hdawg_core_split

        rf_cores = []
        plunger_channels = []
        for awg in channel_mapping:
            for idx in channel_mapping[awg]:
                if channel_mapping[awg][idx]['rf'] == 1:
                    rf_cores.append((awg, channel_mapping[awg][idx]['core_idx']))
                else:
                    plunger_channels.append((awg, channel_mapping[awg][idx]['gate_idx'][0]))
                    plunger_channels.append((awg, channel_mapping[awg][idx]['gate_idx'][1]))

        self._gate_parameters = {}
        gate_param_all_rf = gate_parameters["rf"]
        gate_param_all_dc = gate_parameters["p"]

        for awg in channel_mapping:
            self._gate_parameters[awg] = {"rf": {} , "p": {}}
        for gt_idx in gate_param_all_rf:
            self._gate_parameters[awg_core_split[gt_idx][0]]["rf"][gt_idx] = gate_param_all_rf[gt_idx]
        for gt_idx in gate_param_all_dc:
            self._gate_parameters[awg_core_split[gt_idx][0]]["p"][gt_idx] = gate_param_all_dc[gt_idx]

        if config_awg:
            for awg in self._awgs:
                config_hdawg(self._awgs[awg], self._gate_parameters[awg], channel_mapping[awg])
        else:
            pass

        tau_pi_2_set = []
        for idx in gate_parameters["rf"]:
            tau_pi_2_set.append((idx, gate_parameters["rf"][idx]["tau_pi_2"]))
        tau_pi_2_standard_1 = max(tau_pi_2_set,key=itemgetter(1))[1]
        tau_pi_standard_1 = 2*tau_pi_2_standard_1
        standard_rf_idx = max(tau_pi_2_set,key=itemgetter(1))[0]
        npoints_pi_2_standard = ceil(sample_rate*tau_pi_2_standard_1*1e-9/16)*16
        npoints_pi_standard = ceil(sample_rate*tau_pi_standard_1*1e-9/16)*16
        tau_pi_2_standard = npoints_pi_2_standard/sample_rate
        tau_pi_standard = npoints_pi_standard/sample_rate

        plunger_set = []
        plunger_set_npoints = []
        plunger_set_npoints_tups = []
        for idx in gate_parameters["p"]:
            plunger_set.append((idx, gate_parameters["p"][idx]["tau"]))
            plunger_set_npoints.append(ceil(gate_parameters["p"][idx]["tau"]*2.4/16)*16)
            plunger_set_npoints_tups.append((idx, ceil(gate_parameters["p"][idx]["tau"]*2.4/16)*16))
        hdawg_std_rf = awg_core_split[standard_rf_idx][0]
        npoints_p_standard = max(plunger_set_npoints)

        for core_idx in channel_mapping[hdawg_std_rf]:
            if channel_mapping[hdawg_std_rf][core_idx]['core_idx'] == standard_rf_idx:
                core_std_rf = core_idx
            else:
                pass

        standard_rf = (hdawg_std_rf, standard_rf_idx)
        n_std = (npoints_pi_2_standard, npoints_pi_standard, npoints_p_standard)

        # try:
        #  if tau_p_standard > tau_pi_2_standard:
        #     raise TypeError("DC pulse lengths should always be shorter than RF pulse lengths!!")
        # except TypeError:
        #     raise
        try:
         if added_padding > 5e-9:
            raise TypeError("Padding should not exceed 5 ns!!")
        except TypeError:
            raise

        self._gate_npoints = {}
        for awg in self._gate_parameters:
            self._gate_npoints[awg] = make_gate_npoints(self._gate_parameters[awg], sample_rate)
        self._waveforms = generate_waveforms_v2(self._gate_npoints, channel_mapping, added_padding, standard_rf)

        dc_lengths = {}
        for awg in channel_mapping:
            for core_idx in channel_mapping[awg]:
                if channel_mapping[awg][core_idx]['rf'] == 1:
                    tau_waveform_pi_2_std  = ceil(1e9*len(self._waveforms[awg][core_idx]["pi_2_pi_2fr"])/sample_rate)
                    tau_waveform_pi_std  = ceil(1e9*len(self._waveforms[awg][core_idx]["pi_pifr"])/sample_rate)

                elif channel_mapping[awg][core_idx]['rf'] == 0:
                    ch_idx_1 = channel_mapping[awg][core_idx]['gate_idx'][0]
                    ch_idx_2 = channel_mapping[awg][core_idx]['gate_idx'][1]
                    ch_idx_1_key = 'p'+str(ch_idx_1)+'_p'+str(ch_idx_1)+'fr'
                    ch_idx_2_key = 'p'+str(ch_idx_2)+'_p'+str(ch_idx_2)+'fr'
                    dc_lengths[ch_idx_1] =  ceil(1e9*len(self._waveforms[awg][core_idx][ch_idx_1_key])/(sample_rate*16))*16
                    dc_lengths[ch_idx_2] = ceil(1e9*len(self._waveforms[awg][core_idx][ch_idx_2_key])/(sample_rate*16))*16
                else:
                    pass

        self._gate_lengths = make_gate_lengths_v2(dc_lengths, tau_waveform_pi_2_std, tau_waveform_pi_std, channel_mapping)

        self._gate_sequences, arbitrary_gates, arbitrary_waveforms, arbitrary_z = gst_file_parser_v3(self._gst_path, self._gate_lengths, channel_mapping, awg_core_split, sample_rate=sample_rate)

        self._command_tables = {}
        arbgate_counter = {}
        for awg_idx in channel_mapping:
            self._command_tables[awg_idx] = {}
            arbgate_counter[awg_idx] = {}
            for core_idx in channel_mapping[awg_idx]:
                arbgate_counter[awg_idx][core_idx] = 0
                if channel_mapping[awg_idx][core_idx]['rf'] == 1:
                    self._command_tables[awg_idx][core_idx] = make_rf_command_table_v2(n_std, arbitrary_z, arbitrary_waveforms, plunger_set_npoints_tups, awg_idx, core_idx)
                else:
                    self._command_tables[awg_idx][core_idx] = make_dc_command_table_v2(n_std, arbitrary_waveforms, plunger_set_npoints_tups, awg_idx, core_idx)


        ct_idxs_all = {}
        taus_std = (tau_waveform_pi_2_std, tau_waveform_pi_std)
        for idx in self._gate_sequences:
            gate_sequence = self._gate_sequences[idx]
            ct_idxs, arbgate_counter = make_command_table_indices_v3(gate_sequence, channel_mapping, awg_core_split, arbitrary_waveforms, plunger_set_npoints_tups, taus_std, self._gate_lengths, arbgate_counter, arbitrary_z)
            ct_idxs_all[idx] = ct_idxs
        self._ct_idxs_all = ct_idxs_all
    #     waveforms_awg = {}
    #     sequencer_code = {}
    #     seq_code = {}
    #     command_code = {}
    #     n_array_rf = [len(self._waveforms[1]["pi_pifr"]), len(self._waveforms[1]["pi_2_pi_2fr"]), len(self._waveforms[1]["pi_2_pifr"])]
    #     n_array_p = [len(self._waveforms[4]["p1_p1fr"]), len(self._waveforms[4]["p2_p2fr"]),  len(self._waveforms[4]["p1_p2fr"]), len(self._waveforms[4]["p2_p1fr"]), len(self._waveforms[4]["p1_pi_2fr"]), len(self._waveforms[4]["p2_pi_2fr"]),len(self._waveforms[4]["p1_pifr"]), len(self._waveforms[4]["p2_pifr"])]
    #     rf_cores = [1,2,3]
    #
    #     for idx in rf_cores:
    #         waveforms = Waveforms()
    #         waveforms.assign_waveform(slot = 0, wave1 = np.array(self._waveforms[idx]["pi_pifr"]))
    #         waveforms.assign_waveform(slot = 1, wave1 = np.array(self._waveforms[idx]["pi_2_pi_2fr"]))
    #         waveforms.assign_waveform(slot = 2, wave1 = np.array(self._waveforms[idx]["pi_2_pifr"]))
    #         waveforms_awg[idx] = waveforms
    #         seq_code[idx] =  make_waveform_placeholders(n_array_rf)
    #         command_code[idx] = ""
    #         sequence = "repeat("+str(n_outer)+"){\n "
    #         for ii in range(len(ct_idxs_all)):
    #             n_seq = ct_idxs_all[ii]['rf'][str(idx-1)]
    #             if idx-1 == trigger_channel:
    #                 seq = make_gateset_sequencer_hard_trigger(n_seq, n_inner, trig_channel=True)
    #             else:
    #                 seq = make_gateset_sequencer_hard_trigger(n_seq, n_inner, trig_channel=False)
    #             sequence += seq
    #         command_code[idx] = command_code[idx] + sequence
    #         sequencer_code[idx] = seq_code[idx] + command_code[idx] + "}"
    #
    #     idx = 4
    #     waveforms = Waveforms()
    #     waveforms.assign_waveform(slot = 0, wave1 = np.array(self._waveforms[idx]["p1_p1fr"]), wave2 = np.zeros(len(self._waveforms[idx]["p2_p2fr"])))
    #     waveforms.assign_waveform(slot = 1, wave1 = np.zeros(len(self._waveforms[idx]["p2_p2fr"])), wave2 = np.array(self._waveforms[idx]["p2_p2fr"]))
    #     waveforms.assign_waveform(slot = 2, wave1 = np.array(self._waveforms[idx]["p1_p2fr"]), wave2 = np.array(self._waveforms[idx]["p2_p1fr"]))
    #     waveforms.assign_waveform(slot = 3, wave1 = np.array(self._waveforms[idx]["p1_p2fr"]), wave2 = np.array(self._waveforms[idx]["p2_p1fr"]))
    #     waveforms.assign_waveform(slot = 4, wave1 = np.array(self._waveforms[idx]["p1_pi_2fr"]), wave2=np.zeros(len(self._waveforms[idx]["p1_pi_2fr"])))
    #     waveforms.assign_waveform(slot = 5, wave1 = np.zeros(len(self._waveforms[idx]["p2_pi_2fr"])), wave2 = np.array(self._waveforms[idx]["p2_pi_2fr"]))
    #     waveforms.assign_waveform(slot = 6, wave1 = np.array(self._waveforms[idx]["p1_pifr"]), wave2=np.zeros(len(self._waveforms[idx]["p1_pifr"])))
    #     waveforms.assign_waveform(slot = 7, wave1 = np.zeros(len(self._waveforms[idx]["p2_pifr"])), wave2 = np.array(self._waveforms[idx]["p2_pifr"]))
    #     waveforms.assign_waveform(slot = 8, wave1 = np.array(self._waveforms[idx]["p1_pi_2fr"]), wave2 = np.array(self._waveforms[idx]["p2_pi_2fr"]))
    #     waveforms.assign_waveform(slot = 9, wave1 = np.array(self._waveforms[idx]["p1_pifr"]),  wave2 = np.array(self._waveforms[idx]["p2_pifr"]))
    #
    #     waveforms_awg[idx] = waveforms
    #     seq_code[idx] = make_waveform_placeholders_plungers(n_array_p)
    #     command_code[idx] = ""
    #
    #     sequence = "repeat("+str(n_outer)+"){\n "
    #     for ii in range(len(ct_idxs_all)):
    #         n_seq = ct_idxs_all[ii]['plunger'][str(6)]
    #         if idx == trigger_channel:
    #             seq = make_gateset_sequencer_hard_trigger(n_seq, n_inner, trig_channel=True)
    #         else:
    #             seq = make_gateset_sequencer_hard_trigger(n_seq, n_inner, trig_channel=False)
    #         sequence += seq
    #     command_code[idx] = command_code[idx] + sequence
    #     sequencer_code[idx] = seq_code[idx] + command_code[idx] + "}"
    #
    #     self._sequencer_code = sequencer_code
    #     for idx in range(0,4):
    #         self._awg.load_sequence(self._sequencer_code[idx+1], awg_idx=idx)
    #         self._awg._awgs["awg"+str(idx+1 )].write_to_waveform_memory(waveforms_awg[idx+1])
    #
    #     daq = self._awg._daq
    #     dev = self._awg._connection_settings["hdawg_id"]
    #
    #     for idx in rf_cores:
    #           daq.setVector(f"/{dev}/awgs/{idx-1}/commandtable/data", json.dumps(self._command_tables['rf']))
    #     p_idx = 3
    #     daq.setVector(f"/{dev}/awgs/{p_idx}/commandtable/data", json.dumps(self._command_tables['plunger']))
    #
    # def run_program(self, awg_idxs=None):
    #     """
    #      Runs uploaded quantum algorithm on the specified AWG cores.
    #
    #      Waits for external hardware trigger event to execute program.
    #
    #      Parameters
    #      ----------
    #      awg_idxs : 'list'
    #      List of awg_idxs (default set to [0,1,2,3]) to run.
    #
    #      Returns
    #      -------
    #      None.
    #     """
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = [0,1,2,3]
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)
