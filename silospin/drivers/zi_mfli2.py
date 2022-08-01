#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
import numpy as np
import time

class MFLI2:
    def __init__(self, device_id, server_host = "localhost", server_port = 8004, api_level = 1, sigins = None, dmods = None, oscs = None, sigouts = None, trig_settings = None):
        """
         Constructor for MFLI driver.

           Returns
           -------
           None.
        """

        self._connection_settings = {"hdawg_id" : device_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "connection_status" : False}
        (daq, device, _) = zhinst.utils.create_api_session(device_id, api_level, server_host=server_host, server_port=server_port)
        self._daq = daq
        self._device = device
        zhinst.utils.disable_everything(self._daq, self._device)

        ##setting for Signal input (0 refers to channel 0)
        self._sigins = {0: {"ac": 0, "imp50": 0, "range": 1}}
        ##setting  for Signal input
        self._demods = {0: {"enable": 1, "rate": 10e3, "adcselect": 0, "order": 4, "timeconstant": 0.01, "oscselect": 0, "harmonic": 1}}
        ##setting for Signal input
        self._oscs = {0: {"freq": 300e3}}
        ##setting  for Signal input
        self._sigouts = {0: {"on": 1, "enable":  1, "range": 1 , "amplitude": 1}}

        demod_index = 0
        in_channel = 0
        osc_index = 0
        out_channel = 0
        out_mixer_channel = 0
        ##make list of settings to upload to daq
        self._lockin_settings = [
        ["/%s/sigins/%d/ac" % (device, in_channel), self._sigins[0]["ac"]],
        ["/%s/sigins/%d/range" % (device, in_channel), self._sigins[0]["range"]],
        ["/%s/demods/%d/enable" % (device, demod_index), self._demods[0]["enable"]],
        ["/%s/demods/%d/rate" % (device, demod_index), self._demods[0]["rate"]],
        ["/%s/demods/%d/adcselect" % (device, demod_index), 0],
        ["/%s/demods/%d/order" % (device, demod_index), self._demods[0]["order"]],
        ["/%s/demods/%d/timeconstant" % (device, demod_index),  self._demods[0]["timeconstant"]],
        ["/%s/demods/%d/oscselect" % (device, demod_index), 0],
        ["/%s/demods/%d/harmonic" % (device, demod_index), self._demods[0]["harmonic"]],
        ["/%s/oscs/%d/freq" % (device, osc_index), self._oscs[0]["freq"]],
        ["/%s/sigouts/%d/on" % (device, out_channel), self._sigouts[0]["on"]],
        ["/%s/sigouts/%d/enables/%d" % (device, out_channel, out_mixer_channel), self._sigouts[0]["enable"]],
        ["/%s/sigouts/%d/range" % (device, out_channel), self._sigouts[0]["range"]],
        ["/%s/sigouts/%d/amplitudes/%d" % (device, out_channel, out_mixer_channel), self._sigouts[0]["amplitude"],],]

        timeconstant_set = daq.getDouble("/%s/demods/%d/timeconstant" % (device, demod_index))
        time.sleep(10 * timeconstant_set)

        ###Daq setup and triggering
        ##Daq module
        self._daq.sync()
        self._daq_module = daq.dataAcquisitionModule()

        ##Setup Trigger Settings ==> accomodate for HW triggers
        ## type (6 = HW tri. )
        ## Defaut: rising edge with trig levle of 0.8
        trigger_path = "/%s/demods/%d/sample.trigin1" % (self._device, demod_index)
        self._trigger_settings =  {"type": 1, "level": 0.8,  "edge": 1, "n_pulses": 2, "repeats": 1, "trig_path": trigger_path,
        "trig_count": 1, "hold_count": 0, "hold_time": 0, "delay":  0, "gridmode": 4, "trig_duration": 0.8}
        n_samples =  int(self._demods[0]["rate"]*self._trigger_settings["trig_duration"])

        self._daq_module.set("triggernode",self._trigger_settings["trig_path"])
        self._daq_module.set("type", self._trigger_settings["type"])
        self._daq_module.set("edge", self._trigger_settings["edge"])
        self._daq_module.set("level", self._trigger_settings["level"])
        self._daq_module.set("grid/repetitions", self._trigger_settings["repeats"])
        self._daq_module.set("delay", self._trigger_settings["repeats"])
        self._daq_module.set("grid/mode", self._trigger_settings["gridmode"])
        self._daq_module.set("duration", self._trigger_settings["trig_duration"])
        self._daq_module.set("grid/cols", n_samples)
