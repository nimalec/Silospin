#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk
from zhinst.ziPython import ziListEnum
import matplotlib.pyplot as plt
import numpy as np
import time
from silospin.drivers.driver_helpers import read_data_update_plot

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
        self._scope_module = self._daq.ScopeModule()
        self._demods_settings = {"enable": self._daq.getInt(f"/{self._device}/demods/0/enable"), "adcselect": self._daq.getInt(f"/{self._device}/demods/0/adcselect") ,
        "bypass": self._daq.getInt(f"/{self._device}/demods/0/bypass"), "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "harmonic":
        self._daq.getInt(f"/{self._device}/demods/0/bypass"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
        "oscselect": self._daq.getInt(f"/{self._device}/demods/0/oscselect"),   "phaseshift": self._daq.getDouble(f"/{self._device}/demods/0/phaseshift"),
        "phaseadjust":  self._daq.getInt(f"/{self._device}/demods/0/phaseadjust"), "rate" : self._daq.getDouble(f"/{self._device}/demods/0/rate"),
        "sinc": self._daq.getInt(f"/{self._device}/demods/0/sinc"), "timeconstant": self._daq.getDouble(f"/{self._device}/demods/0/timeconstant")
        , "trigger": self._daq.getInt(f"/{self._device}/demods/0/trigger")}
        self._sigins_settings = {"ac": self._daq.getInt(f"/{self._device}/sigins/0/ac"), "autorange": self._daq.getInt(f"/{self._device}/sigins/0/autorange")
        , "diff": self._daq.getInt(f"/{self._device}/sigins/0/diff"),
        "float": self._daq.getInt(f"/{self._device}/sigins/0/float"), "impt50": self._daq.getInt(f"/{self._device}/sigins/0/imp50"),
         "max": self._daq.getDouble(f"/{self._device}/sigins/0/max"), "min": self._daq.getDouble(f"/{self._device}/sigins/0/min"),
        "on": self._daq.getInt(f"/{self._device}/sigins/0/on"), "range": self._daq.getInt(f"/{self._device}/sigins/0/range"), "scaling": self._daq.getInt(f"/{self._device}/sigins/0/scaling")}
        self._sigouts_settings = {"add": self._daq.getInt(f"/{self._device}/sigouts/0/add"),
        "autorange": self._daq.getInt(f"/{self._device}/sigouts/0/autorange"),
        "diff": self._daq.getInt(f"/{self._device}/sigouts/0/diff"),
        "imp50": self._daq.getInt(f"/{self._device}/sigouts/0/imp50"),
        "offset": self._daq.getDouble(f"/{self._device}/sigouts/0/offset"),
        "on": self._daq.getDouble(f"/{self._device}/sigouts/0/on"),
        "over": self._daq.getDouble(f"/{self._device}/sigouts/0/over") ,
        "range": self._daq.getDouble(f"/{self._device}/sigouts/0/range")}
        self._currins_settings = {"autorange": self._daq.getInt(f"/{self._device}/currins/0/autorange"), "float": self._daq.getInt(f"/{self._device}/currins/0/float"), "max": self._daq.getDouble(f"/{self._device}/currins/0/max"), "min": self._daq.getDouble(f"/{self._device}/currins/0/min"),
          "on": self._daq.getInt(f"/{self._device}/currins/0/on") , "range": self._daq.getInt(f"/{self._device}/currins/0/range"), "scaling": self._daq.getDouble(f"/{self._device}/currins/0/scaling")}
        self._oscs_settings = {"freq": self._daq.getDouble(f"/{self._device}/oscs/0/freq")}

    def get_all_mfli_settings(self):
        self._demods_settings = {"enable": self._daq.getInt(f"/{self._device}/demods/0/enable"), "adcselect": self._daq.getInt(f"/{self._device}/demods/0/adcselect") ,
        "bypass": self._daq.getInt(f"/{self._device}/demods/0/bypass"), "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "harmonic":
        self._daq.getInt(f"/{self._device}/demods/0/bypass"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
        "oscselect": self._daq.getInt(f"/{self._device}/demods/0/oscselect"),   "phaseshift": self._daq.getDouble(f"/{self._device}/demods/0/phaseshift"),
        "phaseadjust":  self._daq.getInt(f"/{self._device}/demods/0/phaseadjust"), "rate" : self._daq.getDouble(f"/{self._device}/demods/0/rate"),
        "sinc": self._daq.getInt(f"/{self._device}/demods/0/sinc"), "timeconstant": self._daq.getDouble(f"/{self._device}/demods/0/timeconstant")
        , "trigger": self._daq.getInt(f"/{self._device}/demods/0/trigger")}
        self._sigins_settings = {"ac": self._daq.getInt(f"/{self._device}/sigins/0/ac"), "autorange": self._daq.getInt(f"/{self._device}/sigins/0/autorange")
        , "diff": self._daq.getInt(f"/{self._device}/sigins/0/diff"),
        "float": self._daq.getInt(f"/{self._device}/sigins/0/float"), "imp50": self._daq.getInt(f"/{self._device}/sigins/0/imp50"),
         "max": self._daq.getDouble(f"/{self._device}/sigins/0/max"), "min": self._daq.getDouble(f"/{self._device}/sigins/0/min"),
        "on": self._daq.getInt(f"/{self._device}/sigins/0/on"), "range": self._daq.getInt(f"/{self._device}/sigins/0/range"), "scaling": self._daq.getInt(f"/{self._device}/sigins/0/scaling")}
        self._sigouts_settings = {
        "autorange": self._daq.getInt(f"/{self._device}/sigouts/0/autorange"),
        "diff": self._daq.getInt(f"/{self._device}/sigouts/0/diff"),
        "imp50": self._daq.getInt(f"/{self._device}/sigouts/0/imp50"),
        "offset": self._daq.getDouble(f"/{self._device}/sigouts/0/offset"),
        "on": self._daq.getDouble(f"/{self._device}/sigouts/0/on"),
        "over": self._daq.getDouble(f"/{self._device}/sigouts/0/over") ,
        "range": self._daq.getDouble(f"/{self._device}/sigouts/0/range")}
        self._currins_settings = {"autorange": self._daq.getInt(f"/{self._device}/currins/0/autorange"), "float": self._daq.getInt(f"/{self._device}/currins/0/float"), "max": self._daq.getDouble(f"/{self._device}/currins/0/max"), "min": self._daq.getDouble(f"/{self._device}/currins/0/min"),
          "on": self._daq.getInt(f"/{self._device}/currins/0/on") , "range": self._daq.getInt(f"/{self._device}/currins/0/range"), "scaling": self._daq.getDouble(f"/{self._device}/currins/0/scaling")}
        self._oscs_settings = {"freq": self._daq.getDouble(f"/{self._device}/oscs/0/freq")}
        return {"demods": self._demods_settings, "sigins": self._sigins_settings, "sigouts": self._sigouts_settings, "currins": self._currins_settings , "oscs": self._oscs_settings}

    def get_demods_settings(self, key):
        settings_1 = {"enable", "adcselect","bypass", "harmonic", "order", "oscselect", "phaseadjust",  "sinc", "trigger"}
        settings_2 = {"freq", "phaseshift", "rate", "timeconstant", "rate"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/demods/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/demods/0/"+key)
        return value

    def set_demods_settings(self, key, value):
        settings_1 = {"enable", "adcselect","bypass", "harmonic", "order", "oscselect", "phaseadjust",  "sinc", "trigger"}
        settings_2 = {"freq", "phaseshift", "rate", "timeconstant", "rate"}
        if key in settings_1:
            self._daq.set(f"/{self._device}/demods/0/"+key, value)
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/demods/0/"+key)
        elif key in settings_2:
            self._daq.set(f"/{self._device}/demods/0/"+key)
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/demods/0/"+key)

    def get_sigins_settings(self, key):
        settings_1 = {"ac", "autorange", "diff", "float","imp50", "on", "range"}
        settings_2 = {"max", "min"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/sigins/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/sigins/0/"+key)
        return value

    def set_sigins_settings(self, key, value):
        settings_1 = {"ac", "autorange", "diff", "float","imp50", "on", "range"}
        settings_2 = {"max", "min"}
        if key in settings_1:
            self._daq.set(f"/{self._device}/sigins/0/"+key, value)
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/sigins/0/"+key)
        elif key in settings_2:
            self._daq.set(f"/{self._device}/sigins/0/"+key)
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/sigins/0/"+key)

    def get_sigouts_settings(self, key):
        settings_1 = {"add","autorange", "diff", "imp50", "on", "over", "range"}
        settings_2 = {"offset"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/sigouts/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/sigouts/0/"+key)
        return value

    def set_sigouts_settings(self, key, value):
        settings_1 = {"add","autorange", "diff", "imp50", "on", "over", "range"}
        settings_2 = {"offset"}
        if key in settings_1:
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/sigouts/0/"+key)
            self._daq.set(f"/{self._device}/sigouts/0/"+key, value)
        elif key in settings_2:
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/sigouts/0/"+key)
            self._daq.set(f"/{self._device}/sigouts/0/"+key)

    def get_currins_settings(self, key):
        settings_1 = {"autorange", "float", "range"}
        settings_2 = {"max", "min", "scaling"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/currins/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/currins/0/"+key)
        return value

    def set_currins_settings(self, key, value):
        settings_1 = {"autorange","float","range"}
        settings_2 = {"max","min","scaling"}
        if key in settings_1:
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/currins/0/"+key)
            self._daq.set(f"/{self._device}/currins/0/"+key, value)
        elif key in settings_2:
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/currins/0/"+key)
            self._daq.set(f"/{self._device}/currins/0/"+key)

    # def enable_data_transfer(self):
    #      self._daq.set(f"/{self._device}/demods/0/enable", 1)
    #      self._demod_settings["enable"] = self._daq.getInt(f"/{self._device}/demods/0/enable")
    #      self._scope_module = self._daq.scopeModule()

    #def get_sigins_settings(self, key):


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

    def get_osc_setting(self, key):
        self._grid_settings[key] = self._daq_module.getDouble("grid/"+key)

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

    def continuous_data_acquisition_time_domain(self, total_duration, burst_duration, signal_nodes = ["x", "y"]):
        ##prepare daq module for cont. data acquisition_time
        self._mfli.set_demods_settings("enable", 1)
        self._daq_module.set("device", self._dev_id)
        self.set_trigger_setting("type", 0)
        self.set_grid_setting("mode", 2)

        sig_paths = []
        for nd in signal_nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            sig_paths.append(signal_path)
        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = self._mfli._daq.listNodes(f"/{self._dev_id}", flags)
        demod_path = f"/{self._dev_id}/demods/0/sample"
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

        data = {}
        for sig in sig_paths:
            data[sig] = []
            self._daq_module.subscribe(sig)

        clockbase = float(self._mfli._daq.getInt(f"/{self._dev_id}/clockbase"))
        ts0 = np.nan
        read_count = 0
        self.execute()

        timeout = 1.5 * total_duration
        t0_measurement = time.time()
        t_update = 0.9 * burst_duration
        while not self._daq_module.finished():
            t0_loop = time.time()
            if time.time() - t0_measurement > timeout:
                raise Exception(f"Timeout after {timeout} s - recording not complete." "Are the streaming nodes enabled?")
            data, ts0 = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
            read_count += 1
            time.sleep(max(0, t_update - (time.time() - t0_loop)))
        data, _ = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
        timeout = 1.5 * total_duration
        t0 = time.time()
        self._data = data

    def continuous_data_acquisition_spectrum(self, freq_span, n_cols, signal_nodes = ["x", "y"]):
        ##prepare daq module for cont. data acquisition_time
        ## FFT settings (note: currently uses freq_span as standard)
        time_constant = 1/(2*freq_span)
        self.set_fft_setting("spectrumautobw", 1) #Subscribes  automatic bandwidth
        self.set_fft_setting("absolute",1) #Centers wrt demod freq
        self.set_fft_setting("spectrumenable",1) #Enables FFT mode of scope
        signal_path = f"/{self._dev_id}/demods/0/sample.xiy.fft.abs" #Defines signal path for PSD
        self.set_fft_setting("spectrumfrequencyspan", time_constant )

        ##Demod settings
        self._mfli.set_demods_settings("enable", 1) #Enables demodulator
        self._mfli.set_demods_settings("rate", 1e6) #Sets demod rate to 1 MSa/s
        self._mfli.set_demods_settings("freq", 0.0) #Sets demod freq. to 0
        self._mfli.set_demods_settings("timeconstant", 2e-6) #Sets demod freq. to 0
        time.sleep(10 * time_constant)

        ##Sigins settings
        self._mfli.set_sigins_settings("ac", 1)
        self._mfli.set_sigins_settings("imp50", 0)
        self._daq_module.set("device", self._dev_id)

        ## Trigger and grid settings
        self.set_trigger_setting("type", 0) #continuous
        self.set_grid_setting("mode", 4)
        self.set_grid_setting("cols", n_cols)


        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = self._mfli._daq.listNodes(f"/{self._dev_id}", flags)
        demod_path = f"/{self._dev_id}/demods/0/sample"
        if demod_path not in (node.lower() for node in streaming_nodes):
            print(
            f"Device {device} does not have demodulators. Please modify the example to specify",
            "a valid signal_path based on one or more of the following streaming nodes: ",
            "\n".join(streaming_nodes),
            )
            raise Exception(
                "Demodulator streaming nodes unavailable - see the message above for more information."
            )
        num_cols = int(np.ceil(sample_rate * burst_duration))
        num_bursts = int(np.ceil(total_duration / burst_duration))
        self._daq_module.subscribe(signal_path)
        data = {}
        data[signal_path] = []

        clockbase = float(self._mfli._daq.getInt(f"/{self._dev_id}/clockbase"))
        ts0 = np.nan
        read_count = 0
        self.execute()
        buffer_size = self._daq_module.getInt("buffersize")
        time.sleep(2 * buffer_size)
        data = daq_module.read(return_flat_data_dict)
        self._data = data

    # def hw_trig_data_acquisition_time_domain(self, acquisition_time, signal_nodes = ["x", "y"], trig_level = 1):
    #     self._mfli.set_demods_settings("enable", 1)
    #     self._daq_module.set("device", self._dev_id)
    #     self.set_trigger_setting("type", 6)
    #     self.set_grid_setting("mode", 4)
    #     self._daq_module.set("grid/cols",  num_cols)
    #     sig_paths = []
    #     for nd in signal_nodes:
    #         signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
    #         sig_paths.append(signal_path)
    #
    #     self._daq_module.set("level", trig_level)
    #     trigger_duration = 0.18
    #     ##need to specify demod rate somewhere...
    #     self._daq_module.set("duration", trigger_duration)
    #     sample_count = int(demod_rate * trigger_duration)
    #     trigger_duration = daq_module.getDouble("duration")
    #
    #     ##Replace with actual trigger path here
    #     trigger_path = "/%s/demods/%d/sample.r" % (device, demod_index)
    #     self._daq_module.execute()
    #     if self._daq_module.finished():
    #         break
    #     else:
    #         pass
    #     time.sleep(1.2 * buffer_size)
    #     data = daq_module.read(True)
    #     clockbase = float(daq.getInt("/%s/clockbase" % device))
    #     dt_seconds = (samples[0]["timestamp"][0][-1] - samples[0]["timestamp"][0][0]) / clockbase
    #     self._data = data

        ## Figure out sampling rate ...

# class MfliScopeModule(self,mfli_driver):
#     def __init__(self, mfli_driver):
#         self._mfli = mfli_driver
#         self._dev_id = self._mfli._connection_settings["mfli_id"]
#         self._scope_module = self._mfli._scope_module
#         self._averager_settings =  {"resamplingmode": self._scope_module.getInt("averager/resamplingmode"), "restart": self._scope_module.getInt("averager/restart"), "weight": self._scope_module.getInt("averager/weight")}
#         self._misc_settings = {"externalscaling": self._scope_module.getDouble("externalscaling"), "error": self._scope_module.getInt("error"), "clearhistory": self._scope_module.getInt("clearhistory"), "historylength": self._scope_module.getInt("historylength"), "mode": self._scope_module.getInt("mode"), "records": self._scope_module.getInt("records")}
#         self._save_settings = {"csvlocale": self._scope_module.getString("csvlocale"), "csvseparator": self._scope_module.getString("csvseparator"), "directory": self._scope_module.getString("directory") , "fileformat": self._scope_module.getInt("fileformat"), "save": self._scope_module.getInt("save"), "saveonread": self._scope_module.getInt("saveonread")}
#         self._fft_settings = {"power": self._scope_module.getInt("fft/power"), "spectraldensity": self._scope_module.getInt("fft/spectraldensity"), "window": self._scope_module.getInt("fft/window")}
#
#     def get_all_scope_settings(self):
#         self._averager_settings =  {"resamplingmode": self._scope_module.getInt("averager/resamplingmode"), "restart": self._scope_module.getInt("averager/restart"), "weight": self._scope_module.getInt("averager/weight")}
#         self._misc_settings = {"externalscaling": self._scope_module.getDouble("externalscaling"), "error": self._scope_module.getInt("error"), "clearhistory": self._scope_module.getInt("clearhistory"), "historylength": self._scope_module.getInt("historylength"), "mode": self._scope_module.getInt("mode"), "records": self._scope_module.getInt("records")}
#         self._save_settings = {"csvlocale": self._scope_module.getString("csvlocale"), "csvseparator": self._scope_module.getString("csvseparator"), "directory": self._scope_module.getString("directory") , "fileformat": self._scope_module.getInt("fileformat"), "save": self._scope_module.getInt("save"), "saveonread": self._scope_module.getInt("saveonread")}
#         self._fft_settings = {"power": self._scope_module.getInt("fft/power"), "spectraldensity": self._scope_module.getInt("fft/spectraldensity"), "window": self._scope_module.getInt("fft/window")}
#         return {"averager": self._averager_settings, "misc": self._misc_settings , "save": self._save_settings, "fft": self._fft_settings}
#
#    def get_averager_settings(self, key):
#        self._averager_settings[key] = self._scope_module.getInt("averager/"+key)
#        return self._averager_settings[key]
#
#    def set_averager_settings(self, key, value):
#        self._scope_module.setInt("averager/"+key, value)
#        self._averager_settings[key] = self._scope_module.getInt("averager/"+key)
#
#    def get_fft_settings(self, key):
#        self._fft_settings[key] = self._scope_module.getInt("fft/"+key)
#        return self._fft_settings[key]
#
#    def set_fft_settings(self, key, value):
#        self._scope_module.setInt("fft/"+key, value)
#        self._fft_settings[key] = self._scope_module.getInt("fft/"+key)
#
#     ## def set_save_settings
#     ## def get_save_settings
#     ## def set_misc_settings
#     ## def get_misc_settings
#
#    def clear(self):
#        self._scope_module.clear()
#
#    def execute(self):
#        self._scope_module.execute()
#
#    def finish(self):
#         self._scope_module.finish()
#
#    # def listNodes(self, paths):
#    #     self._scope_module.listNodes()
#    #def progress()
#
#    def read(self):
#        self._scope_module.read(True)
#
#    def subscribe_stream_node(self, nodes=["x", "y"]):
#         ##add assert to ensure that correct node is used (inccldue fft settings here)
#         node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
#         for nd in nodes:
#             signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
#             self._signal_paths.add(signal_path)
#             self._scope_module.subscribe(signal_path)
#
#    def unsubscribe_stream_node(self, nodes=["x", "y"]):
#         ##add assert to ensure that correct node is used (inccldue fft settings here)
#         node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
#         for nd in nodes:
#             signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
#             self._signal_paths.add(signal_path)
#             self._scope_module.unsubscribe(signal_path)
#
#

   #def save()
   #def subscribe()

#class MfliSweeperModule:
