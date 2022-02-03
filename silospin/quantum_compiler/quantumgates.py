import numpy as np
import pandas as pd
from silospin.drivers import zi_mfli_v1
from silospin.drivers.math.math_helpers import gauss, rectangular

class SingleQubitGate:
    ##hdawg = HdawgDriver(dev_id = "1234")
    ## X_gate = SingleQubitGate(gate_type="x", pulse_type="rectangular", awg=hdawg)
    ## X_gate.make_queue_pulse()
    ## X_gate.play_pulse()

    def __init__(self, gate_type, pulse_type, awg, I_channel=1, I_osc=1, I_mod_channel="sin11", Q_channel=2, Q_osc=2, Q_mod_channel="sin22", mod_freq=None, IQ_offset=None, tau_p = 10e-6, channel_amp=1, amp_pulse=1):
        ##set default values for all input parameters...
        gates = {"x", "xx", "xxx", "mxxm", "y", "yy", "yyy", "myym", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic", "wait"}
        rectangular_gate_df = pd.read_csv("rectangle_singlequbit_gates.csv")

        ##Assertions for input values

        try:
            if type(gate_type) is not str:
                raise TypeError("'gate_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(gate_type) not in gates:
                raise ValueError("'gate_type' should be in list of gate types.")
        except ValueError:
            raise

        try:
            if type(pulse_type) is not str:
                raise TypeError("'pulse_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(pulse_type) not in pulses:
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
           if type(I_mod_channel) not in {"sin11", "sin22", "sin12", "sin21"}:
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
           if type(Q_mod_channel) not in {"sin11", "sin22", "sin12", "sin21"}:
               raise TypeError("'Q_mod_channel should be in list of 'sin11', 'sin22', 'sin12', 'sin21'")
       except TypeError:
           raise

       try:
           if type(Q_mod_channel) not in {"sin11", "sin22", "sin12", "sin21"}:
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
           if type(channel_amp) is not float or type(channel_amp) is not int:
               raise TypeError("Channel amplitude should be type int or float")
       except TypeError:
           raise

       try:
           if type(amp_pulse) is not float or type(amp_pulse) is not int:
               raise TypeError("Pulse amplitude should be type int or float.")
       except TypeError:
           raise

       # try:
       #     if awg._connection_settings["connection_status"] == 0:
       #         raise ValueError("'awg' should be connected.")
       # except ValueError:
       #     raise







        # if mod_freq:
        #     self._mod_freq = mod_freq
        # else:
        #     self._mod_freq = rectangular_gate_df["mod_freq"][0]

        # try:
        #     if type(awg) is not str:
        #         #check if type AWG
        #         raise TypeError("'awg' should be type hdawg.")
        # except TypeError:
        #     raise

       try:
           if awg.connection_settings["connection_status"] != 1
               #check if type AWG
               raise ValueError("'awg' should be connected.")
       except TypeError:
           raise

        ### set single qubit gate parameters
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

        self._pulse_duration = tau
        self._I_phase = I_phase
        self._Q_phase = Q_phase
        self._IQ_settings = {"I": {"channel": I_channel, "osc": I_osc, "freq": self._mod_freq, "phase_shift": self._I_phase, "modulation_channels": I_mod_channel, "wave_out": True, "amp": amp}, "Q": {"channel": Q_channel, "osc": Q_osc, "freq": self._mod_freq, "phase_shift": self._Q_phase, "modulation_channels": Q_mod_channel, "wave_out": True , "amp": amp}}

        ##Implement funciton to generate waveform
        t_start =  0
        t_end = self._pulse_duration
        self._amplitude = amp
        waveform = rectangular(npoints, t_start, t_end, npoints, amp_wvfrm)
        self._waveform = waveform
        #waveform = make_pulse_envelope(pulse_type="rectangular", npoints, t_start, t_end, amp_wvfrm)
        # self._pulse_type = pulse_type
        # self._hdawg = hdawg
        # self._pulse_envelope = envelope
        # self._IQ_settings = {"I": {"channel": I_channel, "osc": I_osc, "freq": mod_freq, "phase_shift": 0, "modulation_channels": I_mod_channel, "wave_out": True}, "Q": {"channel": Q_channel, "osc": Q_osc, "freq": mod_freq, "phase_shift": np.pi/2+IQ_offset, "modulation_channels": Q_mod_channel, "wave_out": True}}

    #def set_awg()

    def make_pulse_envelope(self, pulse_type, npoints, t_start, t_end, amplitude, t_p=None, mu=None, sig=None):
        pulses  = {"rectangular", "gaussian", "adiabatic", "chirped"}
        if pulse_type == "rectangular":
            wave = recatangular_wave(amplitude, t_p, npoints)
        elif pulse_type == "gaussian":
            wave = gaussian_wave(amplitude, mu, sig, npoints)
        elif pulse_type == "chriped":
            pass
        else:
            pass
        self._pulse_envelope = wave

    def get_pulse_envelope(self):
        return make_pulse
#    def make_pulse(self, gate_type):
        ##add assertiion that pulse envelope exists
    #def get_pulse(self):
    #def get_IQ_settings(self):
    #def set_IQ_settings(self):
    #def queue_wave(self):
    #def play_wave(self):








# def MakeIQWave(gate, pulse_shape, t_p, delta_phi, omega_s, amp, osc_1, osc_2)
# ##Input:
# ## gate (X, Y, H, Z)
# ## Omega_s (sample rate)
# ## omega (modulation freq)
# ## delta_phi (phase offset)
# ## rot_angle
# ## pm
# ## osc_I
# ## osc_Q
# ## trigger
# ## channel_mod (sin11, sin22, etc.)
# ## AWG_channel
#     gates = {"x", "y", "wait"}
#     pulse_shapes = {"rectangular", "gaussian", "chirped", "adiabatic"}
