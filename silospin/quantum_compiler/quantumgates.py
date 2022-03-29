import numpy as np
import pandas as pd
from silospin.drivers.zi_hdawg_driver import HdawgDriver
from silospin.math.math_helpers import gauss, rectangular


class SingleQubitGate:
    def __init__(self, gate_type, awg, pulse_settings = {"pulse_type": "rectangular", "sample_rate": 2.4e9, "tau_p": None}, IQ_settings = {"I_sin": 1, "Q_sin": 2, "I_out": 1, "Q_out": 2, "IQ_offset": 0, "osc": 1, "freq": 15e6 , "amp": 0.5}, gauss_settings = {"mu": None , "sigma": None, "amp": 1}):
        ##If tau_p is None ==> use default settings (pull from table). Otherwise, generate new signal
        ##set default values for all input parameters...
        single_gates = {"x", "xx", "xxx", "mxxm", "y", "yy", "yyy", "myym", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic", "wait"}
        sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
        rectangle_gate_df = pd.read_csv("rectangle_singlequbit_gates.csv")

        ##Assertions for input values
        #
        # try:
        #     if type(gate_type) is not str:
        #         raise TypeError("'gate_type' should be a string.")
        # except TypeError:
        #     raise
        # try:
        #     if gate_type not in gates:
        #         raise ValueError("'gate_type' should be in list of gate types.")
        # except ValueError:
        #     raise
        #
        # try:
        #     if type(pulse_type) is not str:
        #         raise TypeError("'pulse_type' should be a string.")
        # except TypeError:
        #     raise
        # try:
        #     if pulse_type not in pulses:
        #         raise ValueError("'pulse_type' should be 'rectangular', 'gaussian', 'chirped', 'adiabatic', 'wait'")
        # except ValueError:
        #     raise

      ##(1) assert awg type
      ##(2) ensure a connection with awg
      ##(3) assert channel settings  (I_channel, I_osc, I_mod_channel, mod_Freq, Q_channel, IQ_offset, etc.)
      ##(4) determine IQ-settings
      ##(5) generate waveform
        # try:
        #     if awg._connection_settings["connection_status"] == 0:
        #         raise ValueError("'awg' should be connected.")
        # except ValueError:
        #     raise
        #
        # try:
        #     if type(I_channel) is not int:
        #         raise TypeError("'I_channel should be type int.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if I_channel < 1 or I_channel > 8:
        #         raise ValueError("'I_channel should be between 1 and 8.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(I_osc) is not int:
        #         raise TypeError("'I_osc should be type int.")
        # except TypeError:
        #     raise

        # try:
        #     if I_osc < 1 or I_osc > 16:
        #         raise ValueError("'I_osc should be between 1 and 16")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(I_mod_channel) is not str:
        #         raise TypeError("'I_mod_channel should be type str.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if I_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
        #         raise TypeError("'I_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(Q_channel) is not int:
        #         raise TypeError("'Q_channel should be type int.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if Q_channel < 1 or Q_channel > 8:
        #         raise ValueError("'Q_channel should be between 1 and 8.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(Q_osc) is not int:
        #         raise TypeError("'Q_osc should be type int.")
        # except TypeError:
        #     raise

        # try:
        #     if Q_osc < 1 or Q_osc > 16:
        #         raise ValueError("'Q_osc should be between 1 and 16")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(Q_mod_channel) is not str:
        #         raise TypeError("'Q_mod_channel should be type str.")
        # except TypeError:
        #     raise

        # try:
        #     if Q_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
        #         raise TypeError("'Q_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'")
        # except TypeError:
        #     raise
        #
        # try:
        #     if Q_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
        #         raise TypeError("'Q_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(mod_freq) is not float or type(mod_freq) is not int:
        #         raise TypeError("Modulation frequency should be type int or float")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(IQ_offset) is not float or type(mod_freq) is not int:
        #         raise TypeError("IQ offset should be type int or float")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(tau_p) is not float or type(tau_p) is not int:
        #         raise TypeError("Pulse duration should be type int or float")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(amp_channel) is not float or type(amp_channel) is not int:
        #         raise TypeError("Channel amplitude should be type int or float")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(amp_pulse) is not float or type(amp_pulse) is not int:
        #         raise TypeError("Pulse amplitude should be type int or float.")
        # except TypeError:
        #     raise
        #
        # try:
        #     if type(sample_rate) is not float or type(sample_rate) is not int :
        #         raise TypeError("Sample rate should be type int or float")
        # except TypeError:
        #     raise
        #
        # try:
        #     if sample_rate not in sample_rates:
        #         raise ValueError("Sample rate should be in sample_rates")
        # except ValueError:
        #     raise

        ### set single qubit gate parameters
        ##set pulse table for single qubit gates  + command table
        ##For Gaussian pulses, set Gauss width = round(npoints/3)
        ## add column to table for pulse amplitude

        I_phase = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["i_phase"].values
        Q_phase = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["q_phase"].values
        IQ_offset = IQ_settings["IQ_offset"]
        if IQ_offset:
           Q_phase = Q_phase + IQ_offset
        else:
           pass

        tau  = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["pulse_time"]
        amp  = rectangle_gate_df[rectangle_gate_df["gate"] == gate_type]["pulse_amp"]

        self._awg = awg
        self._gate_type = gate_type
        self._pulse_duration = tau
        #self._npoints = round(sample_rate*self._pulse_duration/16)*16
        self._IQ_settings = {"I": {"channel": IQ_settings["I_sin"], "wave_out": IQ_settings["I_out"],  "osc": IQ_settings["osc"],  "freq": IQ_settings["freq"], "phase": I_phase, "amp": IQ_settings["amp"]},
        "Q": {"channel": IQ_settings["Q_sin"],  "wave_out": IQ_settings["Q_out"], "osc": IQ_settings["osc"], "freq": IQ_settings["freq"], "phase": Q_phase, "amp": IQ_settings["amp"]}}

        #if gate_type == "wait":
        #   self._waveform = rectangular(self._npoints,0)
        #else:
        #   self._waveform = rectangular(self._npoints,amp_pulse)

       ##sets I-Q frequencies
        self._awg.set_osc_freq(self._IQ_settings["I"]["osc"], self._IQ_settings["I"]["freq"])
        self._awg.set_osc_freq(self._IQ_settings["Q"]["osc"], self._IQ_settings["Q"]["freq"])

       ##sets I-Q amplitudes
        self._awg.set_out_amp(self._IQ_settings["I"]["channel"], self._IQ_settings["I"]["wave_out"], self._IQ_settings["I"]["amp"])
        self._awg.set_out_amp(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["wave_out"], self._IQ_settings["Q"]["amp"])

        print(self._IQ_settings["I"]["phase"])
        print(self._IQ_settings["Q"]["phase"])

       ##sets I-Q phase
        self._awg.set_phase(self._IQ_settings["I"]["channel"], self._IQ_settings["I"]["phase"])
        self._awg.set_phase(self._IQ_settings["Q"]["channel"], self._IQ_settings["Q"]["phase"])

    # def get_awg(self):
    #     return awg
    #
    # def set_awg(self, awg):
    #     try:
    #         if awg._connection_settings["connection_status"] == 0:
    #             raise ValueError("'awg' should be connected.")
    #     except ValueError:
    #         raise
    #     self._awg = awg
    #
    # def get_gate_type(self):
    #     return self._gate_type = gate_type
    #
    # def get_pulse_duration(self):
    #     return self._pulse_duration
    #
    # def set_sample_rate(self, sample_rate):
    #     sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
    #     try:
    #         if type(sample_rate) is not float:
    #             raise TypeError("sample_rate should be a float.")
    #     except TypeError:
    #         raise
    #     try:
    #         if sample_rate not in sample_rates:
    #             raise ValueError("Sample rate should be in sample_rates")
    #     except ValueError:
    #         raise
    #     self._npoints = sample_rate*self._pulse_duration
    #
    # def get_sample_rate(self):
    #     return self._sample_rate
    #
    # def set_IQ_settings(self, IQ, setting, value):
    #     try:
    #         if IQ != "I" or IQ != "Q":
    #             raise ValueError("IQ should be 'I' or 'Q'.")
    #     except ValueError:
    #         raise
    #     settings = {"channel", "osc", "freq", "phase_shift", "modulation_channels", "wave_out", "amp"}
    #     try:
    #         if setting not in settings:
    #             raise ValueError("setting should be in IQ settings")
    #     except ValueError:
    #         raise
    #
    #     self._IQ_settings[IQ][setting] = value
    #
    # def get_IQ_settings(self, IQ, setting, value):
    #     try:
    #         if IQ != "I" or IQ != "Q":
    #             raise ValueError("IQ should be 'I' or 'Q'.")
    #     except ValueError:
    #         raise
    #     settings = {"channel", "osc", "freq", "phase_shift", "modulation_channels", "wave_out", "amp"}
    #     try:
    #         if setting not in settings:
    #             raise ValueError("setting should be in IQ settings")
    #     except ValueError:
    #         raise
    #     return self._IQ_settings[IQ][setting]
    #
    # def make_pulse_envelope(self, pulse_type, npoints, t_start, t_end, amplitude, t_p=None, mu=None, sig=None):
    #     pulse_types = {"gaussian", "rectangular"}
    #     try:
    #         if pulse_type not in pulse_types:
    #             raise ValueError("pulse_type should bse rectangular or gaussian.")
    #     except ValueError:
    #         raise
    #
    #     if pulse_type == "gaussian":
    #         mu = 0
    #         sig = npoints/3
    #         waveform = gauss(npoints, amp, mu, sig)
    #     else:
    #         waveform = rectangular(npoints, amp)

    # def make_pulse_envelope(self, pulse_type, npoints, t_start, t_end, amplitude, t_p=None, mu=None, sig=None):
    #     pulses  = {"rectangular", "gaussian", "adiabatic", "chirped"}
    #     if pulse_type == "rectangular":
    #         wave = recatangular_wave(amplitude, t_p, npoints)
    #     elif pulse_type == "gaussian":
    #         wave = gaussian_wave(amplitude, mu, sig, npoints)
    #     elif pulse_type == "chriped":
    #         pass
    #     else:
    #         pass
    #     self._pulse_envelope = wave
    #
    # def get_pulse_envelope(self):
    #     return make_pulse
#    def make_pulse(self, gate_type):
        ##add assertiion that pulse envelope exists
    #def get_pulse(self):
    #def get_IQ_settings(self):
    #def set_IQ_settings(self):
    #def queue_wave(self):
    #def play_wave(self):
