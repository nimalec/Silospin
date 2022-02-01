import numpy as np
from silospin.drivers import zi_mfli_v1
from silospin.drivers.math.math_helpers import gauss, rectangular

class SingleQubitGate:
    ##hdawg = HdawgDriver(dev_id = "1234")
    ## X_gate = SingleQubitGate(gate_type="x", pulse_type="rectangular", awg=hdawg)
    ## X_gate.make_queue_pulse()
    ## X_gate.play_pulse()

    def __init__(self, gate_type, pulse_type="rectangular", awg=None, I_channel=1, I_osc=1, I_mod_channel="sin11", mod_freq=10e6, Q_channel=2, Q_osc=2, Q_mod_channel="sin22", IQ_offset=0):
        ##set default values for all input parameters...
        gates = {"x", "y", "h", "wait"}
        pulses = {"rectangular", "gaussian", "chirped", "adiabatic", "wait"}
        ## ensure connection with AWG

        try:
            if type(gate_type) is not str:
                raise TypeError("'gate_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(gate_type) not in gates:
                raise ValueError("'gate_type' should be 'x', 'y', or 'wait'.")
        except ValueError:
            raise

        try:
            if type(pulse_type) is not str:
                raise TypeError("'pulse_type' should be a string.")
        except TypeError:
            raise
        try:
            if type(gate_type) not in gates:
                raise ValueError("'pulse_type' should be 'rectangular', 'gaussian', 'chirped', 'adiabatic', 'wait'.")
        except ValueError:
            raise

        if gate_type == "x":
            I_phase = 0
            Q_phase =

        elif gate_type == "y":

        else:

        self._gate_type = gate_type
        self._pulse_type = pulse_type
        self._hdawg = hdawg
        self._pulse_envelope = envelope
        self._IQ_settings = {"I": {"channel": I_channel, "osc": I_osc, "freq": mod_freq, "phase_shift": 0, "modulation_channels": I_mod_channel, "wave_out": True}, "Q": {"channel": Q_channel, "osc": Q_osc, "freq": mod_freq, "phase_shift": np.pi/2+IQ_offset, "modulation_channels": Q_mod_channel, "wave_out": True}}

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
