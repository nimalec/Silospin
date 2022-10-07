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
from silospin.quantum_compiler.qc_helpers import *
from silospin.io.qc_io import read_qubit_paramater_file, write_qubit_parameter_file, quantum_protocol_parser, quantum_protocol_parser_v4

class GateSetTomographyProgram:
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
    def __init__(self, gst_file_path, awg, n_inner=1, n_outer=1, qubits=[0,1,2,3], qubit_parameters=None, external_trigger=True, trigger_channel=0):
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
       '''
        self._gst_path = gst_file_path
        self._awg = awg
        self._sample_rate = 2.4e9
        self._awg_cores =  qubits

        if qubit_parameters is None:
            self._qubit_parameters =  {0: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 200e-9,  "tau_pi_2" :  100e-9,  "delta_iq" : 0 , "mod_freq": 60e6}, 1: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 200e-9,  "tau_pi_2" :  100e-9,  "delta_iq" : 0 , "mod_freq": 60e6}, 2: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 120e-9,  "tau_pi_2" :  60e-9,  "delta_iq" : 0 ,  "mod_freq": 60e6}, 3: {"i_amp_pi": 1.0, "q_amp_pi": 1.0 , "i_amp_pi_2": 1.0, "q_amp_pi_2": 1.0, "tau_pi" : 160e-9,  "tau_pi_2" :  80e-9,  "delta_iq" : 0 , "mod_freq": 60e6}}
        else:
            self._qubit_parameters = qubit_parameters
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
        self._gate_sequences = quantum_protocol_parser(gst_file_path, qubit_lengths, qubit_set = {1,2,3,4})

        ct_idxs_all = {}
        arbZs = []
        n_arbZ = 0
        for idx in self._gate_sequences:
             gate_sequence = self._gate_sequences[idx]
             ct_idxs_all[idx], arbZ = make_command_table_idxs(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9), n_arbZ)
             n_arbZ += len(arbZ)
             arbZs.append(arbZ)
        arbZ_s = []
        for lst in arbZs:
            for i in lst:
                arbZ_s.append(i)
        command_tables = generate_reduced_command_table(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ_s)
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
            seq_code[idx] =  make_waveform_placeholders(n_array)
            command_code[idx] = ""
            sequence = "repeat("+str(n_outer)+"){\n "
            for ii in range(len(ct_idxs_all)):
                 n_seq = ct_idxs_all[ii][str(idx)]
                 if external_trigger == False:
                     seq = make_gateset_sequencer(n_seq)
                 else:
                     if idx == trigger_channel:
                         seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=True)
                     else:
                         seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=False)
                 sequence += seq
            command_code[idx] = command_code[idx] + sequence
            sequencer_code[idx] =  seq_code[idx] + command_code[idx] + "}"


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

        for idx in qubits:
             self._awg.load_sequence(sequencer_code[idx], awg_idx=idx)
             self._awg._hdawg.awgs[idx].write_to_waveform_memory(waveforms_awg[idx])
        self._sequencer_code = sequencer_code
        self._waveforms_awg = waveforms_awg

        # self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
        # self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}

        # daq = self._awg._daq
        # dev = self._awg._connection_settings["hdawg_id"]

        # for idx in qubits:
        #      i_idx = self._channel_idxs[str(idx)][0]
        #      q_idx = self._channel_idxs[str(idx)][1]
        #      osc_idx = self._channel_osc_idxs[str(idx)]
        #      self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
        #      self._awg.set_sine(i_idx+1, osc_idx)
        #      self._awg.set_sine(q_idx+1, osc_idx)
        #      self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
        #      self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
        #      self._awg._hdawg.sigouts[i_idx].on(1)
        #      self._awg._hdawg.sigouts[q_idx].on(1)
        #      daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables))

    def run_program(self, awg_idxs=None):
        if awg_idxs:
            awg_idxs = awg_idxs
        else:
            awg_idxs = self._awg_cores
        for idx in awg_idxs:
            self._awg._awgs["awg"+str(idx+1)].single(True)
            self._awg._awgs["awg"+str(idx+1)].enable(True)

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

        plunger_set = []
        for idx in self._gate_parameters["p"]:
            plunger_set.append((idx, self._gate_parameters["p"][idx]["tau"]))

        ##Define standard pi/2 length and corresponding gate index
        tau_pi_2_standard = max(tau_pi_2_set,key=itemgetter(1))[1]
        tau_pi_standard = 2*tau_pi_2_standard
        standard_rf_idx = max(tau_pi_2_set,key=itemgetter(1))[0]

        ##Define standard plunger and corresponding gate length
        tau_p_standard = max(plunger_set,key=itemgetter(1))[1]
        standard_p_idx = max(plunger_set,key=itemgetter(1))[0]

        ##2. Defines standard npoints for each gate
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32
        npoints_p_standard = ceil(self._sample_rate*tau_p_standard/32)*32

        ##3. Define standard plunger gate lengths here
        tau_pi_2_standard = npoints_pi_2_standard/self._sample_rate
        tau_pi_standard = npoints_pi_standard/self._sample_rate
        tau_p_standard = npoints_p_standard/self._sample_rate

        p_dict = {}
        for idx in plunger_set:
            p_dict[idx[0]] = ceil(idx[1]*1e-9)

        gate_standard_lengths = {"pi_2": ceil(tau_pi_2_standard*1e-9), "pi": ceil(tau_pi_standard*1e-9), "p": p_dict}

        self._gate_npoints = make_gate_npoints(self._gate_parameters, self._sample_rate)

        ##5. Modify to generte plunger waveforms
        ## Waveform output should be separated into rf and plunger waveforms
        self._waveforms = generate_waveforms_v3(self._gate_npoints, channel_mapping)

        ##6. Modify to account for new gate seq format
        #1. Modify this function to take in "qubit_lenghts of differnet form "
        self._gate_sequences = quantum_protocol_parser_v4(self._gst_path, qubit_lengths, channel_mapping)

    #     ##7. Modify ct_idxs to account for plunger gates
        # ct_idxs_all = {}
        # arbZs = []
        # n_arbZ = 0
        # for idx in self._gate_sequences:
        #      gate_sequence = self._gate_sequences[idx]
        #      ct_idxs_all[idx], arbZ = make_command_table_idxs(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9), n_arbZ)
        #      n_arbZ += len(arbZ)
        #      arbZs.append(arbZ)
        # arbZ_s = []
        # for lst in arbZs:
        #     for i in lst:
        #         arbZ_s.append(i)
        # command_tables = generate_reduced_command_table(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ_s)
        # self._ct_idxs = ct_idxs_all
        # self._command_tables = command_tables
    #
    #     waveforms_awg = {}
    #     sequencer_code = {}
    #     command_code = {}
    #     n_array = [npoints_pi_2_standard, npoints_pi_standard]
    #
    #     ##8. Modify make_waveform_placeholder to account for plunger waveforms  (only for the relevant core). Generates sequence on given core
    #     for idx in qubits:
    #         waveforms = Waveforms()
    #         waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["pi_2"])
    #         waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["pi"])
    #         waveforms_awg[idx] = waveforms
    #         seq_code[idx] =  make_waveform_placeholders(n_array)
    #         command_code[idx] = ""
    #         sequence = "repeat("+str(n_outer)+"){\n "
    #         for ii in range(len(ct_idxs_all)):
    #              n_seq = ct_idxs_all[ii][str(idx)]
    #              if external_trigger == False:
    #                  seq = make_gateset_sequencer(n_seq)
    #              else:
    #                  if idx == trigger_channel:
    #                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=True)
    #                  else:
    #                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=False)
    #              sequence += seq
    #         command_code[idx] = command_code[idx] + sequence
    #         sequencer_code[idx] =  seq_code[idx] + command_code[idx] + "}"
    #     self._sequencer_code = sequencer_code
    #
    #     for idx in qubits:
    #          self._awg.load_sequence(sequencer_code[idx], awg_idx=idx)
    #          self._awg._awgs["awg"+str(idx+1)].write_to_waveform_memory(waveforms_awg[idx])
    #
    #     self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
    #     self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
    #
    #     daq = self._awg._daq
    #     dev = self._awg._connection_settings["hdawg_id"]
    #
    #     ##9. Modify to only set sine waves for modulation cores
    #     for idx in qubits:
    #          i_idx = self._channel_idxs[str(idx)][0]
    #          q_idx = self._channel_idxs[str(idx)][1]
    #          osc_idx = self._channel_osc_idxs[str(idx)]
    #          self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
    #          self._awg.set_sine(i_idx+1, osc_idx)
    #          self._awg.set_sine(q_idx+1, osc_idx)
    #          self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
    #          self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
    #          self._awg._hdawg.sigouts[i_idx].on(1)
    #          self._awg._hdawg.sigouts[q_idx].on(1)
    #          daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables))
    #
    # def run_program(self, awg_idxs=None):
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = self._awg_idxs
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)


class RamseyTypes:
    def __init__(self, awg, t_range, npoints_t, npoints_av, taus_pulse, axis = "x", sample_rate = 2.4e9, n_fr=1):
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

class RabiTypes:
    def __init__(self, awg, t_range, npoints_t, npoints_av, tau_wait, qubits, axis = "x", sample_rate = 2.4e9):
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

class GateSetTomographyProgramPlunger_V3:
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
    def __init__(self, gst_file_path, channel_mapping, gate_parameters, n_inner=1, n_outer=1, external_trigger=True, trigger_channel=0, sample_rate=2.4e9):
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
        #self._awg = awg
        self._sample_rate = sample_rate
        #channel_mapping = self._awg._channel_mapping
        self._gate_parameters = gate_parameters

        ##1. Append plunger gate lengths to tau_pi_2_set. Standard pi length will be defined from pi_2 length.
        tau_pi_2_set = []
        for idx in self._gate_parameters["rf"]:
            tau_pi_2_set.append((idx, self._gate_parameters["rf"][idx]["tau_pi_2"]))

       ##assumes that plungers will alwyas be shorter than rf pulses
        plunger_set = []
        for idx in self._gate_parameters["p"]:
            plunger_set.append((idx, self._gate_parameters["p"][idx]["tau"]))

        ##Define standard pi/2 length and corresponding gate index
        tau_pi_2_standard = max(tau_pi_2_set,key=itemgetter(1))[1]
        tau_pi_standard = 2*tau_pi_2_standard
        standard_rf_idx = max(tau_pi_2_set,key=itemgetter(1))[0]

        ##Define standard plunger and corresponding gate length
        tau_p_standard = max(plunger_set,key=itemgetter(1))[1]
        standard_p_idx = max(plunger_set,key=itemgetter(1))[0]

        ##2. Defines standard npoints for each gate
        npoints_pi_2_standard = ceil(self._sample_rate*tau_pi_2_standard/32)*32
        npoints_pi_standard = ceil(self._sample_rate*tau_pi_standard/32)*32
        npoints_p_standard = ceil(self._sample_rate*tau_p_standard/32)*32

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
        self._waveforms = generate_waveforms_v3(self._gate_npoints, channel_mapping)


        ##6. Modify to account for new gate seq format
        #1. Modify this function to take in "qubit_lenghts of differnet form "
        self._gate_sequences = quantum_protocol_parser_v4(self._gst_path, self._gate_lengths, channel_mapping)


        ##Start here!! think now about generalizing for 2-3 HDAWG untits :) :)


        ##7. Modify ct_idxs to account for plunger gates
        ct_idxs_all = {}
        arbZs = []
        n_arbZ = 0 #counter for the number of arbZ  rotatiosn in the file  s
        #Loops over every line in gate sequence
        for idx in self._gate_sequences:
              gate_sequence = self._gate_sequences[idx]
              ##Start here !! need to modify make commanbd table idxs function  in additon to generate commadn tables
              #gate_sequence corresponding to each line
              ct_idxs_all[idx], arbZ = make_command_table_idxs_rf_p_v0(gate_sequence, ceil(tau_pi_standard_new*1e9), ceil(tau_pi_2_standard_new*1e9), n_arbZ)
              n_arbZ += len(arbZ)
              arbZs.append(arbZ)
        # arbZ_s = []
        # for lst in arbZs:
        #     for i in lst:
        #         arbZ_s.append(i)
        # command_tables = generate_reduced_command_table(npoints_pi_2_standard, npoints_pi_standard, arbZ=arbZ_s)
        # self._ct_idxs = ct_idxs_all
        # self._command_tables = command_tables
    #
    #     waveforms_awg = {}
    #     sequencer_code = {}
    #     command_code = {}
    #     n_array = [npoints_pi_2_standard, npoints_pi_standard]
    #
    #     ##8. Modify make_waveform_placeholder to account for plunger waveforms  (only for the relevant core). Generates sequence on given core
    #     for idx in qubits:
    #         waveforms = Waveforms()
    #         waveforms.assign_waveform(slot = 0, wave1 = self._waveforms[idx]["pi_2"])
    #         waveforms.assign_waveform(slot = 1, wave1 = self._waveforms[idx]["pi"])
    #         waveforms_awg[idx] = waveforms
    #         seq_code[idx] =  make_waveform_placeholders(n_array)
    #         command_code[idx] = ""
    #         sequence = "repeat("+str(n_outer)+"){\n "
    #         for ii in range(len(ct_idxs_all)):
    #              n_seq = ct_idxs_all[ii][str(idx)]
    #              if external_trigger == False:
    #                  seq = make_gateset_sequencer(n_seq)
    #              else:
    #                  if idx == trigger_channel:
    #                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=True)
    #                  else:
    #                      seq = make_gateset_sequencer_ext_trigger(n_seq, n_inner, trig_channel=False)
    #              sequence += seq
    #         command_code[idx] = command_code[idx] + sequence
    #         sequencer_code[idx] =  seq_code[idx] + command_code[idx] + "}"
    #     self._sequencer_code = sequencer_code
    #
    #     for idx in qubits:
    #          self._awg.load_sequence(sequencer_code[idx], awg_idx=idx)
    #          self._awg._awgs["awg"+str(idx+1)].write_to_waveform_memory(waveforms_awg[idx])
    #
    #     self._channel_idxs = {"0": [0,1], "1": [2,3], "2": [4,5], "3": [6,7]}
    #     self._channel_osc_idxs = {"0": 1, "1": 5, "2": 9, "3": 13}
    #
    #     daq = self._awg._daq
    #     dev = self._awg._connection_settings["hdawg_id"]
    #
    #     ##9. Modify to only set sine waves for modulation cores
    #     for idx in qubits:
    #          i_idx = self._channel_idxs[str(idx)][0]
    #          q_idx = self._channel_idxs[str(idx)][1]
    #          osc_idx = self._channel_osc_idxs[str(idx)]
    #          self._awg.set_osc_freq(osc_idx, self._qubit_parameters[idx]["mod_freq"])
    #          self._awg.set_sine(i_idx+1, osc_idx)
    #          self._awg.set_sine(q_idx+1, osc_idx)
    #          self._awg.set_out_amp(i_idx+1, 1, self._qubit_parameters[idx]["i_amp_pi"])
    #          self._awg.set_out_amp(q_idx+1, 2, self._qubit_parameters[idx]["q_amp_pi"])
    #          self._awg._hdawg.sigouts[i_idx].on(1)
    #          self._awg._hdawg.sigouts[q_idx].on(1)
    #          daq.setVector(f"/{dev}/awgs/{idx}/commandtable/data", json.dumps(self._command_tables))
    #
    # def run_program(self, awg_idxs=None):
    #     if awg_idxs:
    #         awg_idxs = awg_idxs
    #     else:
    #         awg_idxs = self._awg_idxs
    #     for idx in awg_idxs:
    #         self._awg._awgs["awg"+str(idx+1)].single(True)
    #         self._awg._awgs["awg"+str(idx+1)].enable(True)
