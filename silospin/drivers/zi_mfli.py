#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
import numpy as np



#class MFLIDAQ:
#class MFLISWEEPER:

class MFLI:

    def __init__(self, dev_id, name = "mfli_1", server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE"):
        """
         Constructor for HDAWG Driver.

           Returns
           -------
           None.
        """
        self._connection_settings = {"li_name": name, "li_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "interface" : interface, "connection_status" : False}
        self._mfli = tk.MFLI(self._connection_settings["li_name"],self._connection_settings["li_id"])
        self._mfli.setup()
        self._mfli.connect_device()
        self._connection_settings["connection_status"] = self._mfli.is_connected

        self._oscillator_freq = self._mfli.nodetree.osc.freq()

        self._demod_channel = [self._mfli.demods[0].adcselect(), self._mfli.demods[1].adcselect()]
        self._filter_order = [self._mfli.demods[0].order(), self._mfli.demods[1].order()]
        self._sample_rate = [self._mfli.demods[0].rate(), self._mfli.demods[1].rate()]
        self._oscillator = [self._mfli.demods[0].oscselect(), self._mfli.demods[1].oscselect()]
        self._harmonic = [self._mfli.demods[0].harmonic(), self._mfli.demods[1].harmonic()]
        self._phase = [self._mfli.demods[0].phaseshift(), self._mfli.demods[1].phaseshift()]
        self._sinc = [self._mfli.demods[0].sinc(), self._mfli.demods[1].sinc()]
        self._bypass = [self._mfli.demods[0].bypass(), self._mfli.demods[1].bypass()]
        self._cutoff_tau = [self._mfli.demods[0].timeconstant(), self._mfli.demods[1].timeconstant()]
        self._enable_daq = [self._mfli.demods[0].enable(), self._mfli.demods[1].enable()]
        self._trigger = [self._mfli.demods[0].trigger(), self._mfli.demods[1].trigger()]
        self._phase_adjust = [self._mfli.demods[0].phaseadjust(), self._mfli.demods[1].phaseadjust()]
        self._sample = [self._mfli.demods[0].sample(), self._mfli.demods[1].sample()]
        self._extref = {"enable": self._mfli.nodetree.extref.enable(), "automode": self._mfli.nodetree.extref.automode(),
         "adcselect": self._mfli.nodetree.extref.adcselect(), "demodselect": self._mfli.nodetree.extref.demodselect(),
         "oscselect": self._mfli.nodetree.extref.oscselect(), "locked": self._mfli.nodetree.extref.locked()}
        self._trigger_in = {"1": {"level": self._mfli.nodetree.triggers.in_[0].level(), "autothreshold": self._mfli.nodetree.triggers.in_[0].autothreshold()},
        "2": {"level": self._mfli.nodetree.triggers.in_[1].level(), "autothreshold": self._mfli.nodetree.triggers.in_[1].autothreshold()}}
        self._trigger_out = {"1": {"source": self._mfli.nodetree.triggers.out[0].source(), "pulsewidth": self._mfli.nodetree.triggers.out[0].pulsewidth()},
        "2": {"source": self._mfli.nodetree.triggers.out[1].source(), "pulsewidth": self._mfli.nodetree.triggers.out[1].pulsewidth()}}
        self._li_channels = {"auxin_1": self._mfli.nodetree.auxin.values[0](), "auxin_2": , "auxout_1": , "auxout_2":   , "auxout_3": ,  "auxout_4": ,
        "sigin": , "sigout": , "currin": }

        self._auxin = {"auxin_1": self._mfli.nodetree.auxin.values[0](), "auxin_2": self._mfli.nodetree.auxin.values[1]()}
        self._auxout = {"auxout_1": self._mfli.nodetree.auxouts[0].value(), "auxout_2": self._mfli.nodetree.auxouts[1].value(),
        "auxout_3": self._mfli.nodetree.auxouts[2].value(), "auxout_4": self._mfli.nodetree.auxouts[3].value()}
        self._sigin = {"diff": self._mfli.nodetree.sigin.diff(), "ac": self._mfli.nodetree.sigin.ac(), "imp": self._mfli.nodetree.sigin.imp50(), "float": self._mfli.nodetree.sigin.float(),  "on": self._mfli.nodetree.sigin.on(), "gain":  self._mfli.nodetree.sigin.range(), "scale": self._mfli.nodetree.sigin.scaling()}
        self._sigout = {"imp": self._mfli.nodetree.sigout.imp50(), "diff": self._mfli.nodetree.sigout.diff() , "gain": self._mfli.nodetree.sigout.range(), "over": self._mfli.nodetree.sigout.over() , "offset": self._mfli.nodetree.sigout.offset() , "add":  self._mfli.nodetree.sigout.add() ,  "enable": self._mfli.nodetree.sigout.enable() , "amp": self._mfli.nodetree.sigout.amplitude()}
        self._currin = {"gain": self._mfli.nodetree.currin.range(), "float": self._mfli.nodetree.currin.float(), "on": self._mfli.nodetree.currin.on(), "scale": self._mfli.nodetree.currin.scale()}


    # def connect_lockin(self)
    # def frequency_sweep(self, freq_range)
    # def amplitude_sweep(self, amp_range)
    # def output_amplitude(self)
    # def output_phase(self)
    # def output_impedance(self)
    # def data_acquisition(self):
