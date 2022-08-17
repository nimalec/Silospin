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
        self._currins = {"autorange": self._daq.getInt(f"/{self._device}/currins/0/autorange"), "float": self._daq.getInt(f"/{self._device}/currins/0/float"), "max": self._daq.getDouble(f"/{self._device}/currins/0/max"), "min": self._daq.getDouble(f"/{self._device}/currins/0/min"),
          "on": self._daq.getInt(f"/{self._device}/currins/0/on") , "range": self._daq.getInt(f"/{self._device}/currins/0/range"), "scaling": self._daq.getDouble(f"/{self._device}/currins/0/scaling")}
        self._oscs = {"freq": self._daq.getDouble(f"/{self._device}/oscs/0/freq")}

    def enable_data_transfer(self):
         self._daq.set(f"/{self._device}/demods/0/enable", 1)
         self._demod_settings["enable"] = self._daq.getInt(f"/{self._device}/demods/0/enable")
         self._scope_module = self._daq.scopeModule()

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
