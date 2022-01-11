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
         , "auxout_3": {"channel": self._mfli.nodetree.auxouts[2].demodselect() , "v_min": self._mfli.nodetree.auxouts[2].limitlower(),
           "v_max": self._mfli.nodetree.auxouts[2].limitupper(), "offset": self._mfli.nodetree.auxouts[2].offset(),
           "output_type": self._mfli.nodetree.auxouts[2].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[2].preoffset(),
           "scale":  self._mfli.nodetree.auxouts[2].scale(), "v_value" :  self._mfli.nodetree.auxouts[2].value()}
         , "auxout_4": {"channel": self._mfli.nodetree.auxouts[3].demodselect() , "v_min": self._mfli.nodetree.auxouts[3].limitlower(),
           "v_max": self._mfli.nodetree.auxouts[3].limitupper(), "offset": self._mfli.nodetree.auxouts[3].offset(),
           "output_type": self._mfli.nodetree.auxouts[3].outputselect(), "pre_off":   self._mfli.nodetree.auxouts[3].preoffset(),
           "scale":  self._mfli.nodetree.auxouts[3].scale(), "v_value" :  self._mfli.nodetree.auxouts[3].value()} }

        self._sigin_channel = {"ac_couple": self._mfli.nodetree.sigin.ac(),
        ,"autorange": self._mfli.nodetree.sigin.autorange()
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

        self._currin_channel = {"autorange": self._mfli.nodetree.sigin.autorange(),
        ,"float": self._mfli.nodetree.sigin.float(),
        "max": self._mfli.nodetree.sigin.max(),
        "min": self._mfli.nodetree.sigin.min(),
        "on": self._mfli.nodetree.sigin.on(),
        "range": self._mfli.nodetree.sigouts.range(),
        "scaling": self._mfli.nodetree.sigouts.scaling()}
        self._clock_status = self._mfli.nodetree.clockbase()

        self._demod_settings = {"chan_1": {"adcselect": self._mfli.nodetree.demods[0]. , "bypass": , "freq": , "harmonic": , "order": , "osc_sel":, "phaseadjust":, "phaseshift": , "rate": , "sample": , "sinc": , "timeconstant": } ,
        "chan_2": { }}
        self._extref_settings =
        self._impedance_settings =
        self._modulation_settings =
        self._oscillator_settings =
        self._scope_settings =
        self._system_settings =
        self._trigger_settings =
        self._threshold_settings =
