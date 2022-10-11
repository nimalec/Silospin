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
from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular
from silospin.quantum_compiler.qc_helpers_v2 import *
from silospin.quantum_compiler.qc_io_v2 import *


class GateSetTomographyProgramPlunger:
    """
    Class representing an instance of compiler gate set tomography experiment (uses entirely rectangular waves).
    ..
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
    Methods
    -------
    __init__(gst_file_path, awg, n_inner=1, n_outer=1, qubits=[0,1,2,3], qubit_parameters=None, external_trigger=False, trigger_channel=0)
        Constructor object for GST compilation object.
    run_program(awg_idxs):
        Compiles and runs programs over specified awg_idxs.
    """
    def __init__(self, gst_file_path, awg, gate_parameters, n_inner=1, n_outer=1, external_trigger=True, trigger_channel=0, sample_rate=2.4e9):
        '''
        Constructor method for CompileGateSetTomographyProgram.
        Parameters:
            gst_file_path : str
                File path for gate set tomography program being read and compiled.
            awg : HdawgDriver
                Instance of HdawgDriver object, native to silospin.
            n_inner : int
                Number of inner frames (for each line in GST file) to loop over.
            n_outer : int
                Number of outer frames (over entire GST file) to loop over.
            qubits : list
                List of indcices corresponding to the qubits (AWG cores) used in the program.
            qubit_parameters : dict
                Dictionary of standard parameters for each qubit. Dicionary keys correspond to qubit (AWG core) indices and value is dictonary of qubit parameters (["i_amp_pi", "q_amp_pi", "i_amp_pi_2", "q_amp_pi_2", "tau_pi",  "tau_pi_2", "delta_iq", "mod_freq"]).
            external_trigger : bool
                True if an external hardware trigger is used. False if the instrument's internal trigger is used.
            trigger_channel : int
                Trigger channel used if external_trigger = True.
            sample_rate : float
                Sample rate of AWG in Sa/s.
       '''

        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = sample_rate
        channel_mapping = self._awg._channel_mapping
        self._gate_parameters = gate_parameters

        ##1. Append plunger gate lengths to tau_pi_2_set. Standard pi length will be defined from pi_2 length.
        tau_pi_2_set = []
        for idx in self._gate_parameters["rf"]:
            tau_pi_2_set.append((idx, self._gate_parameters["rf"][idx]["tau_pi_2"]))

       ##assumes that plungers will alwyas be shorter than rf pulses
        plunger_set = []
        plunger_set_npoints = []
        plunger_set_npoints_tups = []
        for idx in self._gate_parameters["p"]:
            plunger_set.append((idx, self._gate_parameters["p"][idx]["tau"]))
            plunger_set_npoints.append(ceil(self._gate_parameters["p"][idx]["tau"]*2.4/32)*32)
            plunger_set_npoints_tups.append((idx, ceil(self._gate_parameters["p"][idx]["tau"]*2.4/32)*32))

        ##Define standard pi/2 length and corresponding gate index
        tau_pi_2_standard = max(tau_pi_2_set,key=itemgetter(1))[1]
        tau_pi_standard = 2*tau_pi_2_standard
        standard_rf_idx = max(tau_pi_2_set,key=itemgetter(1))[0]

        ##Define standard plunger and corresponding gate length
        tau_p_standard = max(plunger_set,key=itemgetter(1))[1]
        standard_p_idx = max(plunger_set,key=itemgetter(1))[0]

        ##2. Defines standard npoints for each gate
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard*1e-9/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard*1e-9/32)*32
        npoints_p_standard = ceil(self._sample_rate*tau_p_standard*1e-9/32)*32

        ##3. Define standard plunger gate lengths here
        tau_pi_2_standard = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard = npoints_pi_standard/self._sample_rate
        tau_p_standard = npoints_p_standard/self._sample_rate

        p_dict = {}

        for idx in plunger_set:
            p_dict[idx[0]] = ceil(idx[1]*1e-9)


        gate_standard_lengths = {"pi_2": ceil(tau_pi_2_standard*1e-9), "pi": ceil(tau_pi_standard*1e-9), "p": p_dict}


        self._gate_npoints = make_gate_npoints(self._gate_parameters, self._sample_rate)
        self._gate_lengths = make_gate_lengths(self._gate_parameters)



        ##5. Modify to generte plunger waveforms
        ## Waveform output should be separated into rf and plunger waveforms
        #self._waveforms = generate_waveforms_v3(self._gate_npoints, channel_mapping)
        ##Need to modify this
        self._waveforms = generate_waveforms_v4(self._gate_npoints, channel_mapping)

        #6. Modify to account for new gate seq format
        #1. Modify this function to take in "qubit_lenghts of differnet form "
        self._gate_sequences = quantum_protocol_parser_v4(self._gst_path, self._gate_lengths, channel_mapping)

        ##7. Modify ct_idxs to account for plunger gates
        ##ct_idxs_all ==> ct_idxs_all[line_number]['rf'][core_number]
        ct_idxs_all = {}

        arbZs = []
        n_arbZ = 0 #counter for the number of arbZ  rotatiosn in the file
        # #Loops over every line in gate sequence
        #taus_std = (tau_, ceil(tau_pi_2_standard*1e-9))
        taus_std = (ceil(tau_pi_2_standard), ceil(tau_pi_standard))
        taus_std_v2 = (self._gate_lengths['rf'][standard_rf_idx]['pi_2'],  self._gate_lengths['rf'][standard_rf_idx]['pi'])

        for idx in self._gate_sequences:
            gate_sequence = self._gate_sequences[idx]
            ##each element ct_idxs_all[idx] has 'rf' and 'plungers'
            ct_idxs_all[idx], arbZ = make_command_table_idxs_rf_p_v0(gate_sequence, taus_std_v2, plunger_set, n_arbZ)
            n_arbZ += len(arbZ)
            arbZs.append(arbZ)

        arbZ_s = []
        for lst in arbZs:
            for i in lst:
                arbZ_s.append(i)


        command_tables_rf = generate_reduced_command_table_rf_core_v0(npoints_pi_2_standard, npoints_pi_standard, n_p=plunger_set_npoints, arbZ=arbZ_s)
        command_table_plunger = generate_reduced_command_table_p_core_v1(n_p=plunger_set_npoints_tups, n_rf=(npoints_pi_2_standard, npoints_pi_standard))
        self._ct_idxs = ct_idxs_all
        self._command_tables = {'rf': command_tables_rf, 'plunger': command_table_plunger}




        waveforms_awg = {}
        sequencer_code = {}
        seq_code = {}
        command_code = {}
        n_array_rf = [len(self._waveforms[1]["pi_pifr"]), len(self._waveforms[1]["pi_2_pi_2fr"]), len(self._waveforms[1]["pi_2_pifr"])]
        n_array_p = [len(self._waveforms[4]["p1_p1fr"]), len(self._waveforms[4]["p2_p2fr"]),  len(self._waveforms[4]["p1_p2fr"]), len(self._waveforms[4]["p2_p1fr"]), len(self._waveforms[4]["p1_pi_2fr"]), len(self._waveforms[4]["p2_pi_2fr"]),len(self._waveforms[4]["p1_pifr"]), len(self._waveforms[4]["p2_pifr"])]


        rf_cores = [1,2,3]
        p_cores = [4]
         ##Generate sequences for RF core
        for idx in rf_cores:
            waveforms = Waveforms()
            waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["pi_pifr"])
            waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["pi_2_pi_2fr"])
            waveforms.assign_waveform(slot = 2, wave1 = self._waveforms[idx]["pi_2_pifr"])
            waveforms_awg[idx] = waveforms
            seq_code[idx] =  make_waveform_placeholders(n_array_rf)
            command_code[idx] = ""
            sequence = "repeat("+str(n_outer)+"){\n "
            for ii in range(len(ct_idxs_all)):
                n_seq = ct_idxs_all[ii]['rf'][str(idx-1)]
                if external_trigger == False:
                    pass
                else:
                  if idx == trigger_channel:
                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=True)
                  else:
                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=False)
                sequence += seq
                command_code[idx] = command_code[idx] + sequence
                sequencer_code[idx] = seq_code[idx] + command_code[idx] + "}"

        ##Generate sequences for DC core
        for idx in p_cores:
            waveforms = Waveforms()
            waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["p1_p1fr"])
            waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["p2_p2fr"])
            waveforms.assign_waveform(slot = 2, wave1 = self._waveforms[idx]["p1_p2fr"])
            waveforms.assign_waveform(slot = 3, wave1 = self._waveforms[idx]["p2_p1fr"])
            waveforms.assign_waveform(slot = 4, wave1 = self._waveforms[idx]["p1_pi_2fr"])
            waveforms.assign_waveform(slot = 5, wave1 = self._waveforms[idx]["p2_pi_2fr"])
            waveforms.assign_waveform(slot = 6, wave1 = self._waveforms[idx]["p1_pifr"])
            waveforms.assign_waveform(slot = 7, wave1 = self._waveforms[idx]["p2_pifr"])
            waveforms_awg[idx] = waveforms
            seq_code[idx] = make_waveform_placeholders(n_array_p)
            command_code[idx] = ""
            sequence = "repeat("+str(n_outer)+"){\n "
            for ii in range(len(ct_idxs_all)):
                n_seq = ct_idxs_all[ii]['plunger'][str(6)]
                if external_trigger == False:
                    pass
                else:
                  if idx == trigger_channel:
                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=True)
                  else:
                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=False)
                sequence += seq
                command_code[idx] = command_code[idx] + sequence
                sequencer_code[idx] = seq_code[idx] + command_code[idx] + "}"
        self._sequencer_code = sequencer_code
        for idx in range(0,3):
          self._awg.load_sequence(self._sequencer_code[idx+1], awg_idx=idx)
          #self._awg._awgs["awg"+str(idx+1 )].write_to_waveform_memory(waveforms_awg[idx+1])

    #     self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
    #     self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

    #     daq = self._awg._daq
    #     dev = self._awg._connection_settings["hdawg_id"]

    #     # ##9. Modify to only set sine waves for modulation cores
    #     rf_cores_2 = [0,1,2]
    #     for idx in rf_cores_2:
    #           i_idx = self._channel_idxs[str(idx)][0]
    #           q_idx = self._channel_idxs[str(idx)][1]
    #           osc_idx = self._channel_osc_idxs[str(idx)]
    #           self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
    #           self._awg.set_sine(i_idx+1, osc_idx)
    #           self._awg.set_sine(q_idx+1, osc_idx)
    #           self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
    #           self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
    #           self._awg._hdawg.sigouts[i_idx].on(1)
    #           self._awg._hdawg.sigouts[q_idx].on(1)
    #           daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables['rf']))

    #      p_idx = 3
    #      i_idx = self._channel_idxs[str(p_idx)][0]
    #      q_idx = self._channel_idxs[str(p_idx)][1]
    #      osc_idx = self._channel_osc_idxs[str(p_idx)]
    #      self._awg.set_osc_freq(osc_idx, self._qubit_parameters[p_idx]["mod_freq"])
    #      self._awg.set_sine(i_idx+1, osc_idx)
    #      self._awg.set_sine(q_idx+1, osc_idx)
    #      self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[p_idx]["i_amp_pi"])
    #      self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[p_idx]["q_amp_pi"])
    #      self._awg._hdawg.sigouts[i_idx].on(1)
    #      self._awg._hdawg.sigouts[q_idx].on(1)
    #      daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables['plunger']))

    # def run_program(self, awg_idxs=None):
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = self._awg_idxs
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)
