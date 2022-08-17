#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
import numpy as np
import time

class MfliDriver:
    def __init__(self, device_id, server_host = "localhost", server_port = 8004, api_level = 6):
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
        self._daq_module = self._daq.dataAcquisitionModule()
        self._demods = {"enable": self._daq.getInt(f"/{self._device}/demods/0/enable"), "adcselect": self._daq.getInt(f"/{self._device}/demods/0/adcselect") ,
        "bypass": self._daq.getInt(f"/{self._device}/demods/0/bypass"), "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "harmonic":
        self._daq.getInt(f"/{self._device}/demods/0/bypass"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
        "oscselect": self._daq.getInt(f"/{self._device}/demods/0/oscselect"),   "phaseshift": self._daq.getDouble(f"/{self._device}/demods/0/phaseshift"),
        "phaseadjust":  self._daq.getInt(f"/{self._device}/demods/0/phaseadjust"), "rate" : self._daq.getDouble(f"/{self._device}/demods/0/rate"),
        "sinc": self._daq.getInt(f"/{self._device}/demods/0/sinc"), "timeconstant": self._daq.getDouble(f"/{self._device}/demods/0/timeconstant")
        , "trigger": self._daq.getInt(f"/{self._device}/demods/0/trigger")}

        self._sigins = {"ac": self._daq.getInt(f"/{self._device}/sigins/0/ac"), "autorange": self._daq.getInt(f"/{self._device}/sigins/0/autorange")
        , "diff": self._daq.getInt(f"/{self._device}/sigins/0/diff"),
        "float": self._daq.getInt(f"/{self._device}/sigins/0/float"), "impt50": self._daq.getInt(f"/{self._device}/sigins/0/imp50"),
         "max": self._daq.getDouble(f"/{self._device}/sigins/0/max"), "min": self._daq.getDouble(f"/{self._device}/sigins/0/min"),
        "on": self._daq.getInt(f"/{self._device}/sigins/0/on"), "range": self._daq.getInt(f"/{self._device}/sigins/0/range"), "scaling": self._daq.getInt(f"/{self._device}/sigins/0/scaling")}

        self._sigouts = {"add": self._daq.getInt(f"/{self._device}/sigouts/0/add"),
        "autorange": self._daq.getInt(f"/{self._device}/sigouts/0/autorange"),
        "diff": self._daq.getInt(f"/{self._device}/sigouts/0/diff"),
        "imp50": self._daq.getInt(f"/{self._device}/sigouts/0/imp50"),
        "offset": self._daq.getDouble(f"/{self._device}/sigouts/0/offset"),
        "on": self._daq.getDouble(f"/{self._device}/sigouts/0/on"),
        "over": self._daq.getDouble(f"/{self._device}/sigouts/0/over") ,
        "range": self._daq.getDouble(f"/{self._device}/sigouts/0/range")}
        #self._auxins =
        #self._auxouts =
        #self._currins
        #self._demods
        #self._demods =
        #self._dios =
        #self._extrefs
        #self._oscs =
        #self._sigouts =


    def enable_data_transfer(self):
         self._daq.set(f"/{self._device}/demods/0/enable", 1)
         self._demod_settings["enable"] = self._daq.getInt(f"/{self._device}/demods/0/enable")
        # self._scope_module = self._daq.scopeModule()
        #
        # self._daq_module.set("device", self._device)
        # self._daq_module.set("grid/mode", 2)
        # self._daq_sample_rate = 857000
        # self._daq_data = []

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

    # def record_data_daq_continuous(self, total_duration, burst_duration):
    #     ##Signal paths among: demods/0/sample (".x", ".y"), Aux, Scope modules
    #     ##Acquisiton time in seconds
    #     ## Trig type: 0 (cont. triggering), 6 (HW triggering), etc.
    #     n_cols = int(np.ceil(self._daq_sample_rate*burst_duration))
    #     n_bursts = int(np.ceil(total_duration/burst_duration))
    #     self._daq_module.set("type", 0)
    #     self._daq_module.set("count", n_bursts)
    #     self._daq_module.set("duration", burst_duration)
    #     self._daq_module.set("grid/cols", n_cols)
    #     device = self._connection_settings["mfli_id"]
    #
    #     signal_paths = []
    #     demod_path = f"/{device}/demods/0/sample"
    #     signal_paths.append(demod_path+".x")
    #     self._demod_path = signal_paths[0]
    #
    #     ##make signal paths
    #     data = {}
    #     for pth in signal_paths:
    #         self._daq_module.subscribe(pth)
    #         data[pth] = []
    #     clockbase = float(self._daq.getInt(f"/{device}/clockbase"))
    #     ts0 = np.nan
    #
    #     def read_data_update(data, timestamp0):
    #        data_read = self._daq_module.read(True)
    #        returned_signal_paths = [
    #         signal_path.lower() for signal_path in data_read.keys()
    #         ]
    #
    #        for signal_path in signal_paths:
    #            if signal_path.lower() in returned_signal_paths:
    #                for index, signal_burst in enumerate(data_read[signal_path.lower()]):
    #                    if np.any(np.isnan(timestamp0)):
    #                        timestamp0 = signal_burst["timestamp"][0, 0]
    #                    t = (signal_burst["timestamp"][0, :] - timestamp0) / clockbase
    #                    value = signal_burst["value"][0, :]
    #                    num_samples = len(signal_burst["value"][0, :])
    #                    dt = (
    #                        signal_burst["timestamp"][0, -1]
    #                        - signal_burst["timestamp"][0, 0]
    #                    ) / clockbase
    #                    data[signal_path].append(signal_burst)
    #            else:
    #                pass
    #
    #        return data, timestamp0
    #
    #     self._daq_module.execute()
    #     t_update = 0.9*burst_duration
    #     while not self._daq_module.finished():
    #        t0_loop = time.time()
    #        data, ts0 = read_data_update(data, ts0)
    #        time.sleep(max(0, t_update - (time.time() - t0_loop)))
    #     data, _ = read_data_update_plot(data, ts0)
    #     data_daq = []
    #     t_grid = np.linspace(0,burst_duration,n_cols)
    #     for dat in data[self._demod_path]:
    #         data_daq.append([t_grid, dat["value"][0]])
    #     self._daq_data.append(data_daq)
    #     return data_daq

    #def record_data_daq_continuous(self, total_duration, burst_duration):

    #def record_data_scope_continuous(self, total_duration, burst_duration):


class MfliDaqModule:
    def __init__(self, mfli_driver):
        self._mfli = mfli_driver
        self._dev_id = self._mfli._connection_settings["mfli_id"]
        self._daq_module = self._mfli._daq_module
        self._history_settings = {"clearhistory": self._daq_module.getInt("clearhistory") , "duration": self._daq_module.getDouble("duration")}
        self._trigger_settings = {"forcetrigger": self._daq_module.getInt("forcetrigger"), "bitmask": self._daq_module.getInt("bitmask"),
        "bandwidth": self._daq_module.getDouble("bandwidth"), "bits": self._daq_module.getInt("bits"), "count":  self._daq_module.getInt("count"),
        "delay": self._daq_module.getDouble("delay"), "edge": self._daq_module.getInt("edge"),
        "eventcountmode": self._daq_module.getInt("eventcount/mode"), "holdoffcount": self._daq_module.getInt("holdoff/count"),
         "holdofftime": self._daq_module.getDouble("holdoff/time"), "level": self._daq_module.getDouble("level"),
         "pulsemax": self._daq_module.getDouble("pulse/max"), "pulsemin": self._daq_module.getDouble("pulse/min"),
         "triggernode": self._daq_module.getString("triggernode"), "type": self._daq_module.getInt("type"), "triggered": self._daq_module.getInt("triggered")}

        self._grid_settings = {"cols": self._daq_module.getInt("grid/cols"), "direction": self._daq_module.getInt("grid/direction"),
        "mode": self._daq_module.getInt("grid/mode"),  "overwrite": self._daq_module.getInt("grid/overwrite"),
        "mode": self._daq_module.getInt("grid/mode"),  "rowrepetitions": self._daq_module.getInt("grid/rowrepetition"),
        "rows": self._daq_module.getInt("grid/rows"),  "waterfall": self._daq_module.getInt("grid/waterfall")}

        self._fft_settings = {"spectrumautobw": self._daq_module.getInt("spectrum/autobandwidth"), "absolute": self._daq_module.getInt("fft/absolute"),
         "window": self._daq_module.getInt("fft/window"),  "spectrumenable": self._daq_module.getInt("spectrum/enable"),
         "spectrumoverlapped": self._daq_module.getInt("spectrum/overlapped"), "spectrumfrequencyspan": self._daq_module.getDouble("spectrum/frequencyspan")}

        #self._data_streaming = { }
        self._signal_paths = set()

        #self._recorded_data

    def get_all_daq_settings(self):
        self._history_settings = {"clearhistory": self._daq_module.getInt("clearhistory") , "duration": self._daq_module.getDouble("duration")}

        self._trigger_settings = {"forcetrigger": self._daq_module.getInt("forcetrigger"), "bitmask": self._daq_module.getInt("bitmask"),
        "bandwidth": self._daq_module.getDouble("bandwidth"), "bits": self._daq_module.getInt("bits"), "count":  self._daq_module.getInt("count"),
        "delay": self._daq_module.getDouble("delay"), "edge": self._daq_module.getInt("edge"),
        "eventcountmode": self._daq_module.getInt("eventcount/mode"), "holdoffcount": self._daq_module.getInt("holdoff/count"),
         "holdofftime": self._daq_module.getDouble("holdoff/time"), "level": self._daq_module.getDouble("level"),
         "pulsemax": self._daq_module.getDouble("pulse/max"), "pulsemin": self._daq_module.getDouble("pulse/min"),
         "triggernode": self._daq_module.getString("triggernode"), "type": self._daq_module.getInt("type"), "triggered": self._daq_module.getInt("triggered")}

        self._grid_settings = {"cols": self._daq_module.getInt("grid/cols"), "direction": self._daq_module.getInt("grid/direction"),
        "mode": self._daq_module.getInt("grid/mode"),  "overwrite": self._daq_module.getInt("grid/overwrite"), "rowrepetitions": self._daq_module.getInt("grid/rowrepetition"), "rows": self._daq_module.getInt("grid/rows"),  "waterfall": self._daq_module.getInt("grid/waterfall")}

        self._fft_settings = {"spectrumautobw": self._daq_module.getInt("spectrum/autobandwidth"), "absolute": self._daq_module.getInt("fft/absolute"),
         "window": self._daq_module.getInt("fft/window"),  "spectrumenable": self._daq_module.getInt("spectrum/enable"),
         "spectrumoverlapped": self._daq_module.getInt("spectrum/overlapped"), "spectrumfrequencyspan": self._daq_module.getDouble("spectrum/frequencyspan")}
        return {"history": self._history_settings, "trigger": self._trigger_settings, "grid": self._grid_settings, "fft": self._fft_settings}

    def get_history_setting(self, key):
        if key == "clearhistory":
            self._history_settings[key] = self._daq_module.getInt("clearhistory")
        elif key == "duration":
            self._history_settings[key] = self._daq_module.getDouble("duration")
        else:
            pass
        return self._history_settings[key]

    def get_trigger_setting(self, key):
        setings_1 = {"forcetrigger", "bitmask" , "bits", "count",  "edge" , "type", "triggered"}
        setings_2 = {"bandwidth", "delay", "level"}
        if key in setings_1:
            self._trigger_settings[key] = self._daq_module.getInt(key)
        elif key in setings_2:
            self._trigger_settings[key] = self._daq_module.getDouble(key)
        elif key == "eventcountmode":
            self._trigger_settings[key] = self._daq_module.getInt("eventcount/mode")
        elif key == "holdoffcount":
            self._trigger_settings[key] = self._daq_module.getInt("holdoff/count")
        elif key == "holdofftime":
            self._trigger_settings[key] = self._daq_module.getDouble("holdoff/time")
        elif key == "pulsemax":
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/max")
        elif key == "pulsemin":
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/min")
        elif key == "triggernode":
            self._trigger_settings[key] = self._daq_module.getString("triggernode")
        else:
            pass
        return self._trigger_settings[key]

    def get_grid_setting(self, key):
        self._grid_settings[key] = self._daq_module.getInt("grid/"+key)
        return self._grid_settings[key]

    def get_fft_setting(self, key):
        settings_1 = {"window", "absolute"}
        if key == "spectrumautobw":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/autobandwidth")
        elif key == "spectrumenable":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/enable")
        elif key == "spectrumoverlapped":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/overlapped")
        elif key == "spectrumfrequencyspan":
            self._fft_settings[key] = self._daq_module.getDouble("spectrum/frequencyspan")
        elif key in settings_1:
            self._fft_settings[key] = self._daq_module.getInt("fft/"+key)
        else:
            pass
        return self._fft_settings[key]


    def set_history_setting(self, key, value):
        if key == "clearhistory":
            self._daq_module.set("clearhistory", value)
            self._history_settings[key] = self._daq_module.getInt("clearhistory")
        elif key == "duration":
            self._daq_module.set("duration", value)
            self._history_settings[key] = self._daq_module.getDouble("duration")
        else:
            pass

    def set_trigger_setting(self, key, value):
        setings_1 = {"forcetrigger", "bitmask" , "bits", "count",  "edge" , "type", "triggered"}
        setings_2 = {"bandwidth", "delay", "level"}
        if key in setings_1:
            self._daq_module.set(key, value)
            self._trigger_settings[key] = self._daq_module.getInt(key)
        elif key in setings_2:
            self._daq_module.set(key, value)
            self._trigger_settings[key] = self._daq_module.getDouble(key)
        elif key == "eventcountmode":
            self._daq_module.set("eventcount/mode", value)
            self._trigger_settings[key] = self._daq_module.getInt("eventcount/mode")
        elif key == "holdoffcount":
            self._daq_module.set("holdoff/count", value)
            self._trigger_settings[key] = self._daq_module.getInt("holdoff/count")
        elif key == "holdofftime":
            self._daq_module.set("holdoff/time", value)
            self._trigger_settings[key] = self._daq_module.getDouble("holdoff/time")
        elif key == "pulsemax":
            self._daq_module.set("pulse/max", value)
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/max")
        elif key == "pulsemin":
            self._daq_module.set("pulse/min", value)
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/min")
        elif key == "triggernode":
            self._daq_module.set("triggernode", value)
            self._trigger_settings[key] = self._daq_module.getString("triggernode")
        else:
            pass

    def set_grid_setting(self, key, value):
        self._daq_module.set("grid/"+key, value)
        self._grid_settings[key] = self._daq_module.getInt("grid/"+key)

    def set_fft_setting(self, key, value):
        settings_1 = {"window", "absolute"}
        if key == "spectrumautobw":
            self._daq_module.set("spectrum/autobandwidth", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/autobandwidth")
        elif key == "spectrumenable":
            self._daq_module.set("spectrum/enable", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/enable")

        elif key == "spectrumoverlapped":
            self._daq_module.set("spectrum/overlapped", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/overlapped")
        elif key == "spectrumfrequencyspan":
            self._daq_module.set("spectrum/frequencyspan", value)
            self._fft_settings[key] = self._daq_module.getDouble("spectrum/frequencyspan")
        elif key in settings_1:
            self._daq_module.set("fft/"+key, value)
            self._fft_settings[key] = self._daq_module.getInt("fft/"+key)
        else:
            pass

    def execute(self):
        self._daq_module.execute()

    def read(self, read=False, clck_rate=6e7):
        self._daq_module.read(read,clck_rate)

    def subscribe_stream_node(self, nodes=["x", "y"]):
        ##add assert to ensure that correct node is used
        node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
        for nd in nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            self._signal_paths.add(signal_path)
            self._daq_module.subscribe(signal_path)

    def unsubscribe_stream_node(self, nodes=["x", "y"]):
        node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
        for nd in nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            self._signal_paths.remove(signal_path)
            self._daq_module.unsubscribe(signal_path)

    def continuous_data_acquisition(self, total_duration, burst_duration, signal_nodes = ["x", "y"]):
        ##prepare daq module for cont. data acuisit
        self._mfli.enable_data_transfer()
        self._daq_module.set("device", self._dev_id)
        self._daq_module.set("type", 0)
        self._daq_module.set("grid/mode", 2)

        sig_paths = []
        for nd in signal_nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            sig_paths.append(signal_path)
        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = daq.listNodes(f"/{self._dev_id}", flags)
        if demod_path not in (node.lower() for node in streaming_nodes):
            print(
            f"Device {device} does not have demodulators. Please modify the example to specify",
            "a valid signal_path based on one or more of the following streaming nodes: ",
            "\n".join(streaming_nodes),
            )
            raise Exception(
                "Demodulator streaming nodes unavailable - see the message above for more information."
            )
        sample_rate = 3000
        num_cols = int(np.ceil(sample_rate * burst_duration))
        num_bursts = int(np.ceil(total_duration / burst_duration))
        self._daq_module.set("count", num_bursts)
        self._daq_module.set("duration", burst_duration)
        self._daq_module.set("grid/cols",  num_cols)





        #self._daq_module.set("device", self._dev_id)




# class MfliScopeModule:
#
# class MfliSweeperModule:
