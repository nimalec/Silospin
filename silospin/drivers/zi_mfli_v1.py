#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
import numpy as np

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

        self._auxin_channels = {"auxin_1": {"n_av": self._mfli.nodetree.auxin.averaging[0](), "v_av": self._mfli.nodetree.auxin.sample[0]() , "v_value": self._mfli.nodetree.auxin.values[0]()},
        "auxin_2": {"n_av": self._mfli.nodetree.auxin.averaging[1](), "v_av": self._mfli.nodetree.auxin.sample[1](), "v_value": self._mfli.nodetree.auxin.values[1]()}}
        self._auxout_channels = {"auxout_1": {"channel": self._mfli.nodetree.auxouts[0].demodselect() , "v_min": self._mfli.nodetree.auxouts[0].limitlower(),
        "v_max": self._mfli.nodetree.auxouts[0].limitupper(), "offset": self._mfli.nodetree.auxouts[0].offset(),
        "output_type": self._mfli.nodetree.auxouts[0].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[0].preoffset(),
        "scale":  self._mfli.nodetree.auxouts[0].scale(), "v_value" :  self._mfli.nodetree.auxouts[0].value()},
        "auxout_2": {"channel": self._mfli.nodetree.auxouts[1].demodselect() , "v_min": self._mfli.nodetree.auxouts[1].limitlower(),
        "v_max": self._mfli.nodetree.auxouts[1].limitupper(), "offset": self._mfli.nodetree.auxouts[1].offset(),
        "output_type": self._mfli.nodetree.auxouts[1].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[1].preoffset(),
        "scale":  self._mfli.nodetree.auxouts[1].scale(), "v_value" :  self._mfli.nodetree.auxouts[1].value()}
        ,"auxout_3": {"channel": self._mfli.nodetree.auxouts[2].demodselect() , "v_min": self._mfli.nodetree.auxouts[2].limitlower(),
         "v_max": self._mfli.nodetree.auxouts[2].limitupper(), "offset": self._mfli.nodetree.auxouts[2].offset(),
        "output_type": self._mfli.nodetree.auxouts[2].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[2].preoffset(),
        "scale":  self._mfli.nodetree.auxouts[2].scale(), "v_value" :  self._mfli.nodetree.auxouts[2].value()}
        ,"auxout_4": {"channel": self._mfli.nodetree.auxouts[3].demodselect() , "v_min": self._mfli.nodetree.auxouts[3].limitlower(),
        "v_max": self._mfli.nodetree.auxouts[3].limitupper(), "offset": self._mfli.nodetree.auxouts[3].offset(),
        "output_type": self._mfli.nodetree.auxouts[3].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[3].preoffset(),
        "scale":  self._mfli.nodetree.auxouts[3].scale(), "v_value" :  self._mfli.nodetree.auxouts[3].value()} }

        self._sigin_channel = {"ac_couple": self._mfli.nodetree.sigin.ac(),
        "autorange": self._mfli.nodetree.sigin.autorange()
        ,"diff": self._mfli.nodetree.sigin.autorange()
        ,"float": self._mfli.nodetree.sigin.float(),
        "imp50": self._mfli.nodetree.sigin.imp50(),
        "max": self._mfli.nodetree.sigin.max(),
        "min": self._mfli.nodetree.sigin.min(),
        "on": self._mfli.nodetree.sigin.on()}

        self._sigout_channel = {"add": self._mfli.nodetree.sigouts.add(),
        "autorange": self._mfli.nodetree.sigouts.autorange(),
        "diff": self._mfli.nodetree.sigouts.diff(),
        "add": self._mfli.nodetree.sigouts.add(),
        "imp50": self._mfli.nodetree.sigouts.imp50(),
        "offset": self._mfli.nodetree.sigouts.offset(),
        "range": self._mfli.nodetree.sigouts.range(),
        "amp": self._mfli.nodetree.sigouts.amplitudes(),
        "enables": self._mfli.nodetree.sigouts.enables()}

        self._currin_channel = {"autorange": self._mfli.nodetree.currin.autorange(),
        "float": self._mfli.nodetree.currin.float(),
        "max": self._mfli.nodetree.currin.max(),
        "min": self._mfli.nodetree.currin.min(),
        "on": self._mfli.nodetree.currin.on(),
        "range": self._mfli.nodetree.currin.range(),
        "scaling": self._mfli.nodetree.currin.scaling()}
        self._clock_status = self._mfli.nodetree.clockbase()

        self._demod_settings = {"chan_1": {"adcselect": self._mfli.nodetree.demods[0].adcselect(),
        "bypass": self._mfli.nodetree.demods[0].bypass(),
        "freq": self._mfli.nodetree.demods[0].freq(),
         "harmonic": self._mfli.nodetree.demods[0].harmonic()
         ,"order": self._mfli.nodetree.demods[0].order()
         ,"osc_sel": self._mfli.nodetree.demods[0].oscselect()
          ,"phaseadjust": self._mfli.nodetree.demods[0].phaseadjust()
          ,"phaseshift":  self._mfli.nodetree.demods[0].phaseshift()
         ,"rate":  self._mfli.nodetree.demods[0].rate()
         ,"sample": self._mfli.nodetree.demods[0].sample()
        ,"sinc":  self._mfli.nodetree.demods[0].sinc()
        ,"timeconstant": self._mfli.nodetree.demods[0].timeconstant() } ,
        "chan_2": {"adcselect": self._mfli.nodetree.demods[1].adcselect(),
        "bypass": self._mfli.nodetree.demods[1].bypass(),
        "freq": self._mfli.nodetree.demods[1].freq(),
        "harmonic": self._mfli.nodetree.demods[1].harmonic()
         ,"order": self._mfli.nodetree.demods[1].order()
        ,"osc_sel": self._mfli.nodetree.demods[1].oscselect()
        ,"phaseadjust": self._mfli.nodetree.demods[1].phaseadjust()
        ,"phaseshift":  self._mfli.nodetree.demods[1].phaseshift()
        , "rate":  self._mfli.nodetree.demods[1].rate()
        , "sample": self._mfli.nodetree.demods[1].sample()
        , "sinc":  self._mfli.nodetree.demods[1].sinc()
        , "timeconstant": self._mfli.nodetree.demods[1].timeconstant()}}

        self._extref_settings = {"enable": self._mfli.nodetree.extref.enable(), "automode": self._mfli.nodetree.extref.automode(),
         "adcselect": self._mfli.nodetree.extref.adcselect(), "demodselect": self._mfli.nodetree.extref.demodselect(),
         "oscselect": self._mfli.nodetree.extref.oscselect(), "locked": self._mfli.nodetree.extref.locked()}

        self._oscillator_freq = self._mfli.nodetree.osc.freq()
        self._trigger_settings = {"in":  {"1": {"auto_thresh": self._mfli.nodetree.triggers.in_[0].autothreshold(), "level": self._mfli.nodetree.triggers.in_[0].level()},
        "2": {"auto_thresh": self._mfli.nodetree.triggers.in_[1].autothreshold() , "level": self._mfli.nodetree.triggers.in_[1].level()}}, "out": {"1": {"pulse_width": self._mfli.nodetree.triggers.out[0].pulsewidth(), "source":self._mfli.nodetree.triggers.out[0].source()},
        "2": {"pulse_width": self._mfli.nodetree.triggers.out[1].pulsewidth(), "source":self._mfli.nodetree.triggers.out[1].source()}}}

        self._daq =  self._mfli.daq() #implement daq from previously implemented class
        self._sweeper = self._mfli.sweeper() #implement daq from previously implemented class
        #self._threshold_settings = { }

    #def connect_device(self):
    #def set_input_channel(self):
    #def set_output_channel_setting(self):
    #def get_input_channel(self):
    #def get_output_channel_setting(self):
    #def set_demodulator(self):
    #def get_demodulator_setting(self):
    #def set_modulator(self):
    #def get_modulator_setting(self):
    #def set_trigger(self):
    #def get_trigger(self):
     
