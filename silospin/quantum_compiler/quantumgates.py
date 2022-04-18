import numpy as np
import pandas as pd
from pkg_resources import resource_filename
from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular

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
class GateString:
    ##Defines waveforms and command table for a given set of input gates
     def __init__(self, gate_string, iq_settings = None, waveform_settings = None):
         self._gate_string = gate_string
         self._command_table = None


     def make_command_table(self):
         ##Need to specify AWG and output channel.
         ## I ==> out = 0 , Q ==> out = 1.
         ## 1: AWG = 0 , out = 0
         ## 2: AWG = 0 , out = 1
         ## 3: AWG = 1 , out = 0
         ## 4 : AWG = 1 , out = 1
         ## 5 : AWG = 2 , out = 0
         ## 6 : AWG = 2 , out = 1
         ## 7 : AWG = 3 , out = 0
         ## 8 : AWG = 3 , out = 1

         ##X, Y, XXX, YYY  :  wave_idx = 0 (tau = tau_0)
         ##XX, YY, mXXm, mYYm :  wave_idx = 1 (tau = tau_1) (XX = mXm)
         wave_idx = {"x": 0, "y": 0, "xx": 1, "yy": 1, "xxx": 0, "yyy": 0, "mxxm": 1, "myym": 1}
         phases = {"x": {"phase0": 0, "phase1": 90} , "y": {"phase0": 90, "phase1": 180},
         "xx": {"phase0": 0, "phase1": 90} , "yy": {"phase0": 90, "phase1": 180},
         "xxx": {"phase0": 360, "phase1": 270} , "yyy": {"phase0": 270 , "phase1": 180} ,
         "mxxm": {"phase0": 360, "phase1": 270} , "myym":  {"phase0": 270, "phase1": 180}}

         idx = 0
         ct = []
         for gt in self._gate_string:
             #break into 2 cases: playZero = False, playZero = True.
             if gt == "tau":
                 waveform = {"length": 10, "playZero": True}
                 phase0 = {"value": 0,  "increment": True}
                 phase1 = {"value":  0,  "increment": True}
             else:
                 waveform = {"index": wave_idx[gt]}
                 phase0 = {"value": phases[gt]["phase0"], "increment": True}
                 phase1 = {"value": phases[gt]["phase1"], "increment": True}

             ct_entry = {"index": idx, "waveform": waveform, "phase0": phase0, "phase1": phase1}
             ct.append(ct_entry)
             idx += 1

         self._command_table = ct
