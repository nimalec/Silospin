#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
import numpy as np
import time

class MfliDriver:
    def __init__(self, device_id, server_host = "localhost", server_port = 8004, api_level = 6, sigins = None, dmods = None, oscs = None, sigouts = None, trig_settings = None):
        """
         Constructor for MFLI driver.

           Returns
           -------
           None.

        """
        (daq, device, _) = zhinst.utils.create_api_session(device_id, api_level, server_host=server_host, server_port=server_port)
        self._connection_settings = {"mfli_id" : device, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "connection_status" : False}
        self._daq = daq
        self._device = device
        zhinst.utils.api_server_version_check(self._daq)
        self._daq.set(f"/{self._device}/demods/0/enable",1)
        self._daq_module = self._daq.dataAcquisitionModule()

        self._scope_module = self._daq.scopeModule()

        self._daq_module.set("device", self._device)
        self._daq_module.set("grid/mode", 2)
        self._daq_sample_rate = 857000
        self._daq_data = []

        ##setting for Signal input (0 refers to channel 0)
        # self._sigins = {0: {"ac": 0, "imp50": 0, "range": 1}}
        # ##setting  for Signal input
        # self._demods = {0: {"enable": 1, "rate": 10e3, "adcselect": 0, "order": 4, "timeconstant": 0.01, "oscselect": 0, "harmonic": 1}}
        # ##setting for Signal input
        # self._oscs = {0: {"freq": 300e3}}
        # ##setting  for Signal input
        # self._sigouts = {0: {"on": 1, "enable":  1, "range": 1 , "amplitude": 1}}
        #
        # demod_index = 0
        # in_channel = 0
        # osc_index = 0
        # out_channel = 0
        # out_mixer_channel = 0
        # ##make list of settings to upload to daq
        # self._lockin_settings = [
        # ["/%s/sigins/%d/ac" % (device, in_channel), self._sigins[0]["ac"]],
        # ["/%s/sigins/%d/range" % (device, in_channel), self._sigins[0]["range"]],
        # ["/%s/demods/%d/enable" % (device, demod_index), self._demods[0]["enable"]],
        # ["/%s/demods/%d/rate" % (device, demod_index), self._demods[0]["rate"]],
        # ["/%s/demods/%d/adcselect" % (device, demod_index), 0],
        # ["/%s/demods/%d/order" % (device, demod_index), self._demods[0]["order"]],
        # ["/%s/demods/%d/timeconstant" % (device, demod_index),  self._demods[0]["timeconstant"]],
        # ["/%s/demods/%d/oscselect" % (device, demod_index), 0],
        # ["/%s/demods/%d/harmonic" % (device, demod_index), self._demods[0]["harmonic"]],
        # ["/%s/oscs/%d/freq" % (device, osc_index), self._oscs[0]["freq"]],
        # ["/%s/sigouts/%d/on" % (device, out_channel), self._sigouts[0]["on"]],
        # ["/%s/sigouts/%d/enables/%d" % (device, out_channel, out_mixer_channel), self._sigouts[0]["enable"]],
        # ["/%s/sigouts/%d/range" % (device, out_channel), self._sigouts[0]["range"]],
        # ["/%s/sigouts/%d/amplitudes/%d" % (device, out_channel, out_mixer_channel), self._sigouts[0]["amplitude"],],]
        #
        # timeconstant_set = daq.getDouble("/%s/demods/%d/timeconstant" % (device, demod_index))
        # time.sleep(10 * timeconstant_set)
        #
        # ###Daq setup and triggering
        # ##Daq module
        # self._daq.sync()
        # self._daq_module = daq.dataAcquisitionModule()
        #
        # ##Setup Trigger Settings ==> accomodate for HW triggers
        # ## type (6 = HW tri. )
        # ## Defaut: rising edge with trig levle of 0.8
        # trigger_path = "/%s/demods/%d/sample.trigin1" % (self._device, demod_index)
        # self._trigger_settings =  {"type": 6, "level": 0.8,  "edge": 1, "n_pulses": 2, "repeats": 1, "trig_path": trigger_path,
        # "trig_count": 1, "hold_count": 0, "hold_time": 0, "delay":  0, "gridmode": 4, "trig_duration": 0.8}
        # n_samples =  int(self._demods[0]["rate"]*self._trigger_settings["trig_duration"])
        #
        # self._daq_module.set("triggernode",self._trigger_settings["trig_path"])
        # self._daq_module.set("type", self._trigger_settings["type"])
        # self._daq_module.set("edge", self._trigger_settings["edge"])
        # self._daq_module.set("level", self._trigger_settings["level"])
        # self._daq_module.set("grid/repetitions", self._trigger_settings["repeats"])
        # self._daq_module.set("delay", self._trigger_settings["repeats"])
        # self._daq_module.set("grid/mode", self._trigger_settings["gridmode"])
        # self._daq_module.set("duration", self._trigger_settings["trig_duration"])
        # self._daq_module.set("grid/cols", n_samples)
        #
        # buffer_size = self._daq_module.getInt("buffersize")
        # self._signal_path = "/%s/demods/%d/sample.r" % (device, demod_index)
        # if self._trigger_settings["repeats"] > 1:
        #     self._signal_path += ".avg"
        # self._daq_module.subscribe(self._signal_path)
        # return_flat_data_dict = True
        # data = self._daq_module.read(return_flat_data_dict)
        # self._data = data
        #self._samples = data[self._signal_path]

    def record_data_daq_continuous(self, total_duration, burst_duration):
        ##Signal paths among: demods/0/sample (".x", ".y"), Aux, Scope modules
        ##Acquisiton time in seconds
        ## Trig type: 0 (cont. triggering), 6 (HW triggering), etc.
        n_cols = int(np.ceil(self._daq_sample_rate*burst_duration))
        n_bursts = int(np.ceil(total_duration/burst_duration))
        self._daq_module.set("type", 0)
        self._daq_module.set("count", n_bursts)
        self._daq_module.set("duration", burst_duration)
        self._daq_module.set("grid/cols", n_cols)
        device = self._connection_settings["mfli_id"]

        signal_paths = []
        demod_path = f"/{device}/demods/0/sample"
        signal_paths.append(demod_path+".x")
        self._demod_path = signal_paths[0]

        ##make signal paths
        data = {}
        for pth in signal_paths:
            self._daq_module.subscribe(pth)
            data[pth] = []
        clockbase = float(self._daq.getInt(f"/{device}/clockbase"))
        ts0 = np.nan

        def read_data_update(data, timestamp0):
           data_read = self._daq_module.read(True)
           returned_signal_paths = [
            signal_path.lower() for signal_path in data_read.keys()
            ]

           for signal_path in signal_paths:
               if signal_path.lower() in returned_signal_paths:
                   for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                       if np.any(np.isnan(timestamp0)):
                           timestamp0 = signal_burst["timestamp"][0, 0]
                       t = (signal_burst["timestamp"][0, :] - timestamp0) / clockbase
                       value = signal_burst["value"][0, :]
                       num_samples = len(signal_burst["value"][0, :])
                       dt = (
                           signal_burst["timestamp"][0, -1]
                           - signal_burst["timestamp"][0, 0]
                       ) / clockbase
                       data[signal_path].append(signal_burst)
               else:
                   pass

           return data, timestamp0

        self._daq_module.execute()
        t_update = 0.9*burst_duration
        while not self._daq_module.finished():
           t0_loop = time.time()
           data, ts0 = read_data_update(data, ts0)
           time.sleep(max(0, t_update - (time.time() - t0_loop)))
        data, _ = read_data_update_plot(data, ts0)
        data_daq = []
        t_grid = np.linspace(0,burst_duration,n_cols)
        for dat in data[self._demod_path]:
            data_daq.append([t_grid, dat["value"][0]])
        self._daq_data.append(data_daq)
        return data_daq

    #def record_data_daq_continuous(self, total_duration, burst_duration):

    #def record_data_scope_continuous(self, total_duration, burst_duration):
