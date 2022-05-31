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

class SingleQubitGate:
    def __init__(self, gate_type, awg, pulse_settings = {"pulse_type": "rectangular", "sample_rate": 2.4e9, "tau_p": None}, IQ_settings = {"I_sin": 1, "Q_sin": 2, "I_out": 1, "Q_out": 2, "IQ_offset": 0, "osc": 1, "freq": 15e6 , "amp": 0.5}, gauss_settings = {"mu": None , "sigma": None, "amp": 1}):

        gates = {"x", "xx", "xxx", "mxxm", "y", "yy", "yyy", "myym", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic", "wait"}
        sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
        gates_path = resource_filename("silospin.quantum_compiler.quantumgates","rectangle_singlequbit_gates.csv")
        rectangle_gate_df = pd.read_csv(gates_path)

        try:
            if type(gate_type) is not str:
                raise TypeError("'gate_type' should be a string.")
        except TypeError:
            raise
        try:
            if gate_type not in gates:
                raise ValueError("'gate_type' should be in list of gate types.")
        except ValueError:
            raise

        pulse_type = pulse_settings["pulse_type"]

        try:
            if type(pulse_type) is not str:
                raise TypeError("'pulse_type' should be a string.")
        except TypeError:
            raise
        try:
            if pulse_type not in pulses:
                raise ValueError("'pulse_type' should be 'rectangular', 'gaussian', 'chirped', 'adiabatic', 'wait'")
        except ValueError:
            raise

        try:
            if awg._connection_settings["connection_status"] == 0:
                raise ValueError("'awg' should be connected.")
        except ValueError:
            raise

        try:
            if type(IQ_settings["I_sin"]) is not int:
                raise TypeError("'I_channel should be type int.")
        except TypeError:
            raise

        try:
            if IQ_settings["I_sin"] < 1 or IQ_settings["I_sin"] > 8:
                raise ValueError("'I_channel should be between 1 and 8.")
        except ValueError:
            raise

        try:
            if type(IQ_settings["Q_sin"]) is not int:
                raise TypeError("'Q_channel should be type int.")
        except TypeError:
            raise

        try:
            if IQ_settings["Q_sin"] < 1 or IQ_settings["Q_sin"] > 8:
                raise ValueError("'Q_channel should be between 1 and 8.")
        except ValueError:
            raise

        try:
            if pulse_settings["sample_rate"] not in sample_rates:
                raise ValueError("Sample rate should be in sample_rates")
        except ValueError:
            raise

        I_phase = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["i_phase"].values[0]
        Q_phase = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["q_phase"].values[0]
        IQ_offset = IQ_settings["IQ_offset"]
        if IQ_offset:
           Q_phase = Q_phase + IQ_offset
        else:
           pass

        tau  = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["pulse_time"].values[0]
        amp  = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["pulse_amp"].values[0]

        self._awg = awg
        self._gate_type = gate_type
        self._pulse_duration = tau
        self._sample_rate = pulse_settings["sample_rate"]
        self._npoints = round(pulse_settings["sample_rate"]*self._pulse_duration/16)*16
        self._IQ_settings = {"I": {"channel": IQ_settings["I_sin"], "wave_out": IQ_settings["I_out"],  "osc": IQ_settings["osc"],  "freq": IQ_settings["freq"], "phase": I_phase, "amp": IQ_settings["amp"]},
        "Q": {"channel": IQ_settings["Q_sin"],  "wave_out": IQ_settings["Q_out"], "osc": IQ_settings["osc"], "freq": IQ_settings["freq"], "phase": Q_phase, "amp": IQ_settings["amp"]}}
        self._awg.assign_osc(self._IQ_settings["I"]["channel"] ,IQ_settings["osc"])
        self._awg.assign_osc(self._IQ_settings["Q"]["channel"] ,IQ_settings["osc"])

        ##Use rectangular pulses for now
        if gate_type == "wait":
          self._waveform = rectangular(self._npoints,0)
        else:
          self._waveform = rectangular(self._npoints,1)

       ##sets I-Q frequencies
        self._awg.set_osc_freq(self._IQ_settings["I"]["osc"], self._IQ_settings["I"]["freq"])
        self._awg.set_osc_freq(self._IQ_settings["Q"]["osc"], self._IQ_settings["Q"]["freq"])

       ##sets I-Q amplitudes
        self._awg.set_out_amp(self._IQ_settings["I"]["channel"], self._IQ_settings["I"]["wave_out"], self._IQ_settings["I"]["amp"])
        self._awg.set_out_amp(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["wave_out"], self._IQ_settings["Q"]["amp"])

       ##sets I-Q phase
        self._awg.set_phase(self._IQ_settings["I"]["channel"], self._IQ_settings["I"]["phase"])
        self._awg.set_phase(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["phase"])


    def get_awg(self):
        return self._awg

    def set_awg(self, awg):
        try:
            if awg._connection_settings["connection_status"] == 0:
                raise ValueError("'awg' should be connected.")
        except ValueError:
            raise
        self._awg = awg

    def get_gate_type(self):
        return self._gate_type

    def get_pulse_duration(self):
        return self._pulse_duration

    def set_sample_rate(self, sample_rate):
        sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
        try:
            if sample_rate not in sample_rates:
                raise ValueError("Sample rate should be in sample_rates")
        except ValueError:
            raise
        self._npoints = round(sample_rate*self._pulse_duration/16)*16

    def get_sample_rate(self):
        return self._sample_rate

    def set_IQ_channel(self, sin_num, IQ):
        try:
            if type(sin_num) is not int:
                raise TypeError("'sin_num should be type int.")
        except TypeError:
            raise

        try:
            if sin_num < 1 or sin_num > 8:
                raise ValueError("'sin_num should be between 1 and 8.")
        except ValueError:
            raise

        # try:
        #     if IQ != "I" or IQ != "Q":
        #         raise ValueError("IQ should be 'I' or 'Q'")
        # except ValueError:
        #     raise

    def set_phase_offset(phase_offset):
        try:
            if type(float(phase_offset)) is not float:
                raise TypeError("phase_offset should be a float")
        except TypeError:
            raise
        self._IQ_settings["Q"]["phase"] = self._IQ_settings["Q"]["phase"] + phase_offset
        self._awg.set_phase(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["phase"])

    def get_phase(self, IQ):
        # try:
        #     if IQ != "I" or IQ != "Q":
        #         raise ValueError("IQ should be 'I' or 'Q'")
        # except ValueError:
        #     raise
        return self._IQ_settings[IQ]["phase"]

    def set_freq(self, osc_num, freq):
        try:
            if osc_num < 1 or osc_num > 16:
                raise ValueError("Oscillator number should be between 1 and 16")
        except ValueError:
            raise
        try:
            if type(float(freq)) is not float:
                raise TypeError("freq should be a float")
        except TypeError:
            raise

        self._IQ_settings["I"]["osc"] = osc_num
        self._IQ_settings["Q"]["osc"] = osc_num
        self._IQ_settings["I"]["freq"] = freq
        self._IQ_settings["Q"]["freq"] = freq
        self._awg.set_osc_freq(osc_num, freq)

    def get_freq(self):
        return self._IQ_settings["I"]["freq"]

    def set_amp(self, amp):
        self._awg.set_out_amp(self._IQ_settings["I"]["channel"], self._IQ_settings["I"]["wave_out"], amp)
        self._awg.set_out_amp(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["wave_out"], amp)
        self._IQ_settings["I"]["amp"] = amp
        self._IQ_settings["Q"]["amp"] = amp

    def get_amp(self):
        return self._IQ_settings["I"]["amp"]

    #def set_tau_p(self, tau):

    #def set_pulse(self):

    #def get_pulse(self):

    #def compile_gate(self):

    #def play_gate(self):
#
class QubitGatesSet:
    ##Defines waveforms and command table for a given set of input gates
    ##Inputs:
    #-  awg
    #-  gate sequence
    #-  IQ settings (IQ channels, IQ offset,  mod freq,  I_amp, Q_amp)
    # - sample rate
    #-
    #-pulse_settings (shape, tau_p)
    #-

    ##AWG settings: IQ channels: 12, 34, 56, 78.
    #IQ_settings = {"I_sin": 1, "Q_sin": 2, "I_out": 1, "Q_out": 2, "IQ_offset": 0, "osc": 1, "freq": 15e6 , "amp": 0.5}
    #pulse_settings = {"pulse_type": "rectangular", "sample_rate": 2.4e9, "tau_p": None}
    ##Waveform settings:
    # (1) rectangular or gauss?
    # (2) sample rate

     def __init__(self, gate_string, awg, awg_idx = 0, iq_settings= {"i_sin": 1, "q_sin": 2, "i_out": 1, "q_out": 2, "iq_offset": 0, "osc": 1, "freq": 60e6 , "i_amp": 0.5, "q_amp": 0.5}, sample_rate=2.4e9, pulse_type = "gaussian", gauss_width = 1/8, tau_pi = 200e-9, tau_pi2 = 100e-9, continuous=False):
         self._gate_string = gate_string
         self._awg = awg
         self._awg._hdawg.awgs[0].enable(False)
         self._sample_rate = sample_rate
         self._iq_settings = iq_settings
         self._awg._hdawg.sigouts[self._iq_settings["i_out"]-1].on(0)
         self._awg._hdawg.sigouts[self._iq_settings["q_out"]-1].on(0)

         self._awg.set_osc_freq(self._iq_settings["osc"], self._iq_settings["freq"])
         self._awg.set_sine(self._iq_settings["i_sin"], self._iq_settings["osc"])
         self._awg.set_sine(self._iq_settings["q_sin"], self._iq_settings["osc"])
         self._awg.set_out_amp(self._iq_settings["i_sin"], 1, self._iq_settings["i_amp"])
         self._awg.set_out_amp(self._iq_settings["q_sin"], 2, self._iq_settings["q_amp"])

         self._command_table = make_command_table(self._gate_string, self._iq_settings, self._sample_rate)
         self._pulse_type = pulse_type

         self._tau_pi = tau_pi
         self._tau_pi_2 = tau_pi2

         npoints_tau_pi = ceil(self._sample_rate*self._tau_pi/32)*32
         npoints_tau_pi_2 = ceil(self._sample_rate*self._tau_pi_2/32)*32

         if  self._pulse_type == "rectangular":
             self._tau_pi_wave = rectangular(npoints_tau_pi, 0.5)
             self._tau_pi_2_wave = rectangular(npoints_tau_pi_2, 0.5)

         elif self._pulse_type == "gaussian":
             self._tau_pi_wave = gauss(np.array(range(npoints_tau_pi)), 0.5, ceil(npoints_tau_pi/2),  ceil(npoints_tau_pi/8))
             self._tau_pi_2_wave = gauss(np.array(range(npoints_tau_pi_2)), 0.5, ceil(npoints_tau_pi_2/2),  ceil(npoints_tau_pi_2/8))


         n_array = []
         #n_array = {}
         for gt in self._gate_string:
             if gt in {"x", "y", "xxx", "yyy"}:
                 n_array.append(npoints_tau_pi_2)

             elif gt in  {"xx", "yy", "mxxm", "myym"}:
                # n_array.add(npoints_tau_pi)
                 n_array.append(npoints_tau_pi)

             elif gt[0] == "t":
                 npoints_tau = ceil(sample_rate*int(gt[1:4])*(1e-9)/32)*32
                 n_array.append(npoints_tau)
                 pass
             else:
                 pass

         self._sequence_code = make_gateset_sequencer(n_array, continuous=continuous)
         self._awg.load_sequence(self._sequence_code)
         time.sleep(3)


         daq = self._awg._daq
         dev = self._awg._connection_settings["hdawg_id"]
         awg_index = awg_idx

         waveforms = Waveforms()
         idx = 0
         #waveforms.assign_waveform(slot = 0, wave1 = self._tau_pi_2_wave)
         #waveforms.assign_waveform(slot = 1, wave1 = self._tau_pi_wave)

         for gt in self._gate_string:
              if gt in {"x", "y", "xxx", "yyy"}:
                 waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_2_wave)

              elif gt in {"xx", "yy", "mxxm", "myym"}:
                 waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_wave)

              elif gt[0]=="t":
                 t = gt[1:4]
                 n_t = ceil(sample_rate*int(t)*(1e-9)/32)*32
                 waveforms.assign_waveform(slot = idx, wave1 = np.zeros(n_t))
              idx += 1


         #     if gt == "x":
         #         waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_2_wave)
         #
         #     elif gt == "y":
         #         waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_2_wave)
         #
         #     elif gt == "xxx":
         #         waveforms.assign_waveform(slot = idx, wave1 = -self._tau_pi_2_wave)
         #
         #     elif gt == "yyy":
         #         waveforms.assign_waveform(slot = idx, wave1 = -self._tau_pi_2_wave)
         #
         #     elif gt == "xx":
         #         waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_wave)
         #
         #     elif gt == "yy":
         #         waveforms.assign_waveform(slot = idx, wave1 = self._tau_pi_wave)
         #
         #     elif gt == "mxxm":
         #         waveforms.assign_waveform(slot = idx, wave1 = -self._tau_pi_wave)
         #
         #     elif gt == "myym":
         #         waveforms.assign_waveform(slot = idx, wave1 = -self._tau_pi_wave)
         #
         #     elif gt[0]=="t":
         #         t = gt[1:4]
         #         n_t = ceil(sample_rate*int(t)*(1e-9)/32)*32
         #         waveforms.assign_waveform(slot = idx, wave1 = np.zeros(n_t))
         #     idx += 1

         time.sleep(3)
         self._waveforms = waveforms
         self._awg._awgs["awg"+str(awg_index+1)].write_to_waveform_memory(self._waveforms)
         daq.setVector(f"/{dev}/awgs/{awg_index}/commandtable/data", json.dumps(self._command_table))

     def run_program(self, awg_idx=0):
         self._awg._hdawg.sigouts[self._iq_settings["i_out"]-1].on(1)
         self._awg._hdawg.sigouts[self._iq_settings["q_out"]-1].on(1)
         self._awg._awgs["awg"+str(awg_idx+1)].single(True)
         self._awg._awgs["awg"+str(awg_idx+1)].enable(True)

    #def plot_waveforms(self):
