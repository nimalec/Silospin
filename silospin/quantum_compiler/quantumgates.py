import numpy as np
import pandas as pd
#from silospin.drivers import zi_mfli_v1
from silospin.drivers.math.math_helpers import gauss, rectangular

class SingleQubitGate:
    ##hdawg = HdawgDriver(dev_id = "1234")
    ## X_gate = SingleQubitGate(gate_type="x", pulse_type="rectangular", awg=hdawg)
    ## X_gate.make_queue_pulse(
    ## X_gate.play_pulse()

    def __init__(self, gate_type, pulse_type, awg, I_channel=1, I_osc=1, I_mod_channel="sin11", Q_channel=2, Q_osc=2, Q_mod_channel="sin22", sample_rate=2.4e9, mod_freq=None, IQ_offset=None, tau_p = 10e-6, amp_channel=1, amp_pulse=1):
        ##set default values for all input parameters...
        single_gates = {"x", "xx", "xxx", "mxxm", "y", "yy", "yyy", "myym", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic", "wait"}
        sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
        rectangular_gate_df = pd.read_csv("rectangle_singlequbit_gates.csv")

        ##Assertions for input values

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

      ##(1) assert awg type
      ##(2) ensure a connection with awg
      ##(3) assert channel settings  (I_channel, I_osc, I_mod_channel, mod_Freq, Q_channel, IQ_offset, etc.)
      ##(4) determine IQ-settings
      ##(5) generate waveform
        try:
            if awg._connection_settings["connection_status"] == 0:
                raise ValueError("'awg' should be connected.")
        except ValueError:
            raise

        try:
            if type(I_channel) is not int:
                raise TypeError("'I_channel should be type int.")
        except TypeError:
            raise

        try:
            if I_channel < 1 or I_channel > 8:
                raise ValueError("'I_channel should be between 1 and 8.")
        except TypeError:
            raise

        try:
            if type(I_osc) is not int:
                raise TypeError("'I_osc should be type int.")
        except TypeError:
            raise

        try:
            if I_osc < 1 or I_osc > 16:
                raise ValueError("'I_osc should be between 1 and 16")
        except TypeError:
            raise

        try:
            if type(I_mod_channel) is not str:
                raise TypeError("'I_mod_channel should be type str.")
        except TypeError:
            raise

        try:
            if I_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
                raise TypeError("'I_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'.")
        except TypeError:
            raise

        try:
            if type(Q_channel) is not int:
                raise TypeError("'Q_channel should be type int.")
        except TypeError:
            raise

        try:
            if Q_channel < 1 or Q_channel > 8:
                raise ValueError("'Q_channel should be between 1 and 8.")
        except TypeError:
            raise

        try:
            if type(Q_osc) is not int:
                raise TypeError("'Q_osc should be type int.")
        except TypeError:
            raise

        try:
            if Q_osc < 1 or Q_osc > 16:
                raise ValueError("'Q_osc should be between 1 and 16")
        except TypeError:
            raise

        try:
            if type(Q_mod_channel) is not str:
                raise TypeError("'Q_mod_channel should be type str.")
        except TypeError:
            raise

        try:
            if Q_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
                raise TypeError("'Q_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'")
        except TypeError:
            raise

        try:
            if Q_mod_channel not in {"sin11", "sin22", "sin12", "sin21"}:
                raise TypeError("'Q_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'")
        except TypeError:
            raise

        try:
            if type(mod_freq) is not float or type(mod_freq) is not int:
                raise TypeError("Modulation frequency should be type int or float")
        except TypeError:
            raise

        try:
            if type(IQ_offset) is not float or type(mod_freq) is not int:
                raise TypeError("IQ offset should be type int or float")
        except TypeError:
            raise

        try:
            if type(tau_p) is not float or type(tau_p) is not int:
                raise TypeError("Pulse duration should be type int or float")
        except TypeError:
            raise

        try:
            if type(amp_channel) is not float or type(amp_channel) is not int:
                raise TypeError("Channel amplitude should be type int or float")
        except TypeError:
            raise

        try:
            if type(amp_pulse) is not float or type(amp_pulse) is not int:
                raise TypeError("Pulse amplitude should be type int or float.")
        except TypeError:
            raise

        try:
            if type(sample_rate) is not float or type(sample_rate) is not int :
                raise TypeError("Sample rate should be type int or float")
        except TypeError:
            raise

        try:
            if sample_rate not in sample_rates:
                raise ValueError("Sample rate should be in sample_rates")
        except ValueError:
            raise

        ### set single qubit gate parameters
        ##set pulse table for single qubit gates  + command table
        ##For Gaussian pulses, set Gauss width = round(npoints/3)
        ## add column to table for pulse amplitude
        if gate_type == "x" or gate_type == "xx" or gate_type == "xxx" or gate_type == "mxxm":
            if IQ_offset:
                I_phase = 0
                Q_phase = np.pi/2 + IQ_offset
            else:
                I_phase = rectangle_singlequbit_gates_df["i_phase"][0]
                Q_phase = rectangle_singlequbit_gates_df["q_phase"][0]

            if gate_type == "x" or gate_type == "xxx":
                tau = rectangle_singlequbit_gates_df["pulse_time"][0]
            else:
                tau = rectangle_singlequbit_gates_df["pulse_time"][1]

        elif gate_type == "y" or gate_type == "yy" or gate_type == "yy" or gate_type == "myym":
            if IQ_offset:
                I_phase = np.pi/2
                Q_phase = np.pi/2 + IQ_offset
            else:
                I_phase = rectangle_singlequbit_gates_df["i_phase"][0]
                Q_phase = rectangle_singlequbit_gates_df["q_phase"][0]

            if gate_type == "y" or gate_type == "yyy":
                tau = rectangle_singlequbit_gates_df["pulse_time"][4]
            else:
                tau = rectangle_singlequbit_gates_df["pulse_time"][5]

        else:
            I_phase = 0
            Q_phase = 0
            tau = tau_p

        self._awg = awg
        self._gate_type = gate_type
        self._pulse_duration = tau
        self._npoints = int(sample_rate*self._pulse_duration)
        self._IQ_settings = {"I": {"channel": I_channel, "osc": I_osc, "freq": mod_freq, "phase_shift": I_phase, "modulation_channels": I_mod_channel, "wave_out": True, "amp": amp_channel}, "Q": {"channel": Q_channel, "osc": Q_osc, "freq": mod_freq, "phase_shift": Q_phase, "modulation_channels": Q_mod_channel, "wave_out": True , "amp": amp_channel}}

        if gate_type == "wait":
            self._waveform = rectangular(self._npoints,0)
        else:
            self._waveform = rectangular(self._npoints,amp_pulse)

    def set_awg(self, awg):
        try:
            if awg._connection_settings["connection_status"] == 0:
                raise ValueError("'awg' should be connected.")
        except ValueError:
            raise
        self._awg = awg

    def get_awg(self):
        return awg

    def get_gate_type(self):
        return self._gate_type = gate_type

    def get_pulse_duration(self):
        return self._pulse_duration

    def set_sample_rate(self, sample_rate):
        sample_rates = {2.4e9, 1.2e9, 600e6, 300e6, 75e6, 37.5e6, 18.75e6, 9.37e6, 4.68e6, 2.34e6, 1.17e6, 585.93e3, 292.96e3}
        try:
            if type(sample_rate) is not float:
                raise TypeError("sample_rate should be a float.")
        except TypeError:
            raise
        try:
            if sample_rate not in sample_rates:
                raise ValueError("Sample rate should be in sample_rates")
        except ValueError:
            raise
        self._npoints = sample_rate*self._pulse_duration

    def get_sample_rate(self):
        return self._sample_rate

    def set_IQ_settings(self, IQ, setting, value):
        try:
            if IQ != "I" or IQ != "Q":
                raise ValueError("IQ should be 'I' or 'Q'.")
        except ValueError:
            raise
        settings = {"channel", "osc", "freq", "phase_shift", "modulation_channels", "wave_out", "amp"}
        try:
            if setting not in settings:
                raise ValueError("setting should be in IQ settings")
        except ValueError:
            raise

        self._IQ_settings[IQ][setting] = value

    def get_IQ_settings(self, IQ, setting, value):
        try:
            if IQ != "I" or IQ != "Q":
                raise ValueError("IQ should be 'I' or 'Q'.")
        except ValueError:
            raise
        settings = {"channel", "osc", "freq", "phase_shift", "modulation_channels", "wave_out", "amp"}
        try:
            if setting not in settings:
                raise ValueError("setting should be in IQ settings")
        except ValueError:
            raise
        return self._IQ_settings[IQ][setting]

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
