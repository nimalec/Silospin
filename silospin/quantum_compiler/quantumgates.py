import numpy as np
from silospin.drivers import zi_mfli_v1
from silospin.drivers.math import math_helpers

class SingleQubitGate:

    def __init__(self, gate_type, pulse_type="rectangular", hdawg=None,t_p=0):
        ##set default values for all input parameters...
        gates = {"x", "y", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic"}
        try:
            if type(gate_type) is not str:
                raise TypeError("'gate_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(pulse_type) is not str:
                raise TypeError("'pulse_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(gate_type) not in gates:
                raise TypeError("'gate_type' should be 'x', 'y', or 'wait'.")
        except TypeError:
            raise

        self._gate_type = gate_type
        self._pulse_type = pulse_type
        self._hdawg = hdawg
        self._pulse_type = pulse_type
        self._pulse_envelope = None
        self._IQ_settings = {"I": {"channel": 1, "osc": 1, "freq": 10e6, "phase_shift": 0, "modulation_channels": "sin11", "wave_out": True}, "Q": {"channel": 2, "osc": 2, "freq": 10e6, "phase_shift": np.pi/2,  "modulation_channels": "sin22", "wave_out": True}}


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
        self._pulse_envelope


    #def get_pulse_envelope(self)
    #def make_pulse(self):
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
