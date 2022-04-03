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
        self._npoints = round(pulse_settings["sample_rate"]*self._pulse_duration/16)*16
        self._IQ_settings = {"I": {"channel": IQ_settings["I_sin"], "wave_out": IQ_settings["I_out"],  "osc": IQ_settings["osc"],  "freq": IQ_settings["freq"], "phase": I_phase, "amp": IQ_settings["amp"]},
        "Q": {"channel": IQ_settings["Q_sin"],  "wave_out": IQ_settings["Q_out"], "osc": IQ_settings["osc"], "freq": IQ_settings["freq"], "phase": Q_phase, "amp": IQ_settings["amp"]}}

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
        return awg

    def set_awg(self, awg):
        try:
            if awg._connection_settings["connection_status"] == 0:
                raise ValueError("'awg' should be connected.")
        except ValueError:
            raise
        self._awg = awg

    #def get_gate_type(self):

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

        try:
            if IQ != "I" or IQ != "Q":
                raise ValueError("IQ should be 'I' or 'Q'")
        except ValueError:
            raise

    def set_phase_offset(phase_offset):
        try:
            if type(float(phase_offset)) is not float:
                raise TypeError("phase_offset should be a float")
        except TypeError:
            raise
        self._IQ_settings["Q"]["phase"] = self._IQ_settings["Q"]["phase"] + phase_offset

    #def set_freq(freq):
    #def set_channel_amp(amp):
    #def set_tau_p():
    #def set_amp():


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
