"""Driver c
Exact equivariance to :math:`E(3)`
version of january 2021
"""

import zhinst
import zhinst.utils
from zhinst import ziPython
import zhinst.toolkit as tk
from zhinst.ziPython import ziListEnum
import matplotlib.pyplot as plt
import numpy as np
import time
from silospin.drivers.driver_helpers import read_data_update_plot, read_data

class MfliDriverChargeStability:
    def __init__(self, dev_id = "dev5759", excluded_devices = ["dev8446", "dev5761"], sig_path="/dev5759/demods/0/sample", timeconstant = 10e-3, demod_freq = 100e3):
        host = 'localhost'
        port = 8004
        self._signal_path = sig_path
        self._daq_1 = zhinst.ziPython.ziDAQServer(host, port, api_level=6)
        self._daq_1.connect()
        self._mfli = MfliDriver(dev_id)
        self._mfli.set_osc_freq(demod_freq)
        self._daq_mod_2 =  MfliDaqModule(self._mfli)
        self._daq_mod_2.set_continuous_numeric_parameters(timeconstant)

    def get_sample_all(self):
        val = self._daq_1.getSample(self._signal_path)
        return val

    def get_sample_r(self):
        val = self._daq_1.getSample(self._signal_path)
        val_r = np.sqrt(val["x"]**2 + val["y"]**2)
        return val_r[0]

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
        self._scope_module = self._daq.scopeModule()
        self._demods_settings = {"enable": self._daq.getInt(f"/{self._device}/demods/0/enable"), "adcselect": self._daq.getInt(f"/{self._device}/demods/0/adcselect") ,
         "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
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
        "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
        "oscselect": self._daq.getInt(f"/{self._device}/demods/0/oscselect"), "phaseshift": self._daq.getDouble(f"/{self._device}/demods/0/phaseshift"),
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
        return {"connection": self._connection_settings, "demods": self._demods_settings, "sigins": self._sigins_settings, "sigouts": self._sigouts_settings, "currins": self._currins_settings , "oscs": self._oscs_settings}

    def get_osc_freq(self):
        return self._daq.getDouble(f"/{self._device}/oscs/0/freq")

    def set_osc_freq(self, value):
        self._daq.set(f"/{self._device}/oscs/0/freq", value)

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
            self._daq.set(f"/{self._device}/demods/0/"+key, value)
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
            self._daq.set(f"/{self._device}/sigins/0/"+key, value)
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
            self._daq.set(f"/{self._device}/sigouts/0/"+key, value)

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
            self._daq.set(f"/{self._device}/currins/0/"+key, value)

    # def enable_data_transfer(self):
    #      self._daq.set(f"/{self._device}/demods/0/enable", 1)
    #      self._demod_settings["enable"] = self._daq.getInt(f"/{self._device}/demods/0/enable")
    #      self._scope_module = self._daq.scopeModule()


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
        self._data = []
        #self._demod_signals_time_domain = {"x": [ ], "y": [], "r": [], "frequency": [], "phase": }
        #self._demod_signals_freq_domain =
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


    # def continuous_data_acquisition_time_domain(self, burst_duration, n_bursts = 1, signal_nodes = ["x", "y"], sample_rate=3000):
    #     ##prepare daq module for cont. data acquisition_time
    #     self._mfli.set_demods_settings("enable", 1)
    #     self._daq_module.set("device", self._dev_id)
    #     self.set_trigger_setting("type", 0)
    #     self.set_grid_setting("mode", 2)
    #
    #     sig_paths = []
    #     for nd in signal_nodes:
    #         signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
    #         sig_paths.append(signal_path)
    #     #flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
    #     #streaming_nodes = self._mfli._daq.listNodes(f"/{self._dev_id}", flags)
    #
    #     demod_path = f"/{self._dev_id}/demods/0/sample"
    #     # if demod_path not in (node.lower() for node in streaming_nodes):
    #     #     raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")
    #
    #     num_cols = int(np.ceil(sample_rate * burst_duration))
    #
    #     self._daq_module.set("count", n_bursts)
    #     self._daq_module.set("duration", burst_duration)
    #     self._daq_module.set("grid/cols",  num_cols)
    #
    #     data = {}
    #     for sig in sig_paths:
    #         data[sig] = []
    #         self._daq_module.subscribe(sig)
    #
    #     #clockbase = float(self._mfli._daq.getInt(f"/{self._dev_id}/clockbase"))
    #     #ts0 = np.nan
    #     #read_count = 0
    #     self.execute()
    #     #t0_measurement = time.time()
    #     #t_update = 0.9 * burst_duration
    #     while not self._daq_module.finished():
    #         #t0_loop = time.time()
    #         data = read_data_update_plot(data, self._daq_module, sig_paths)
    #         #read_count += 1
    #         #time.sleep(max(0, t_update - (time.time() - t0_loop)))
    #     #data, _ = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
    #     #data, _ = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
    #     data =  read_data_update_plot(data, self._daq_module, sig_paths)
    #     #t0 = time.time()
    #     self._data.append(data)
    #     return data

        ##Flags necessary: 1. signal type , 2. time stamp, 3. actual signal
        #self._data.append(data)

    def continuous_data_acquisition_time_domain(self, burst_duration, n_bursts = 1, signal_nodes = ["x", "y"], sample_rate=3000):
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
            raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")

        num_cols = int(np.ceil(sample_rate * burst_duration))

        self._daq_module.set("count", n_bursts)
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
        time.sleep(1)
        t0_measurement = time.time()
        t_update = 0.9 * burst_duration
        while not self._daq_module.finished():
            t0_loop = time.time()
            data, ts0 = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
            read_count += 1
            time.sleep(max(0, t_update - (time.time() - t0_loop)))
        data, _ = read_data_update_plot(data, ts0, self._daq_module, clockbase, sig_paths)
        t0 = time.time()
        self._data.append(data)
        return data

    def set_continuous_numeric_parameters(self, time_constant=10e-3):
        self._mfli.set_demods_settings("timeconstant", time_constant)
        self._mfli.set_demods_settings("enable", 1)
        self._daq_module.set("device", self._dev_id)
        self._daq_module.set("count", 3)
        self.set_trigger_setting("type", 0)
        self.set_grid_setting("mode", 4)
        signal_path = f"/{self._dev_id}/demods/0/sample.r"
        self._daq_module.set("count", 0)
        self._daq_module.set("grid/cols", 1000)
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("refreshrate", 500)
        self._daq_module.subscribe(signal_path)
        self._mfli._daq_module.execute()
        time.sleep(0.6)

    def continuous_numeric(self):
        signal_path = f"/{self._dev_id}/demods/0/sample.r"
        data_read = self._daq_module.read(True)
        return data_read[signal_path]

        # while not self._daq_module.finished():
        #     data_read = self._daq_module.read(True)
        #     returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
        #     if signal_path.lower() in returned_signal_paths:
        #        val = data_read[signal_path.lower()][0]["value"][0]
        #        return val
        #     else:
        #          pass
        #return val

        # while not self._daq_module.finished():
        #     data_read = self._daq_module.read(True)
        #     returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
        #     if signal_path.lower() in returned_signal_paths:
        #         val = data_read[signal_path.lower()][0]["value"][0]
        #     else:
        #         pass
        # return val

    # def continuous_numeric(self, burst_duration = 10e-6, time_constant=10e-3, sample_rate=3000):
    #     self._mfli.set_demods_settings("enable", 1)
    #     self._daq_module.set("device", self._dev_id)
    #     self.set_trigger_setting("type", 0)
    #     self.set_grid_setting("mode", 2)
    #
    #     signal_path = f"/{self._dev_id}/demods/0/sample.r"
    #     flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
    #     streaming_nodes = self._mfli._daq.listNodes(f"/{self._dev_id}", flags)
    #     demod_path = f"/{self._dev_id}/demods/0/sample"
    #     if demod_path not in (node.lower() for node in streaming_nodes):
    #         raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")
    #
    #     num_cols = int(np.ceil(sample_rate * burst_duration))
    #     self._daq_module.set("count", 1)
    #     self._daq_module.set("duration", burst_duration)
    #     self._daq_module.set("grid/cols",  num_cols)
    #     self._daq_module.subscribe(signal_path)
    #     self._daq_module.execute()
    #     data = {}
    #     while not self._daq_module.finished():
    #         data_read = self._daq_module.read(True)
    #         returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
    #         if signal_path.lower() in returned_signal_paths:
    #             for index, signal_burst in enumerate(data_read[signal_path.lower()]):
    #                 data[signal_path].append(signal_burst)
    #         else:
    #             pass
    #
    #     return data

    #     #num_cols = int(np.ceil(sample_rate * burst_duration))
    #     self._daq_module.set("count", 1)
    #     self._daq_module.set("grid/cols",  1)
    #     self._daq_module.subscribe(signal_path)
    #     self._mfli.set_demods_settings("timeconstant", time_constant)
    #     data = {}
    #     data[signal_path] = []
    #     self._daq_module.execute()
    #     time.sleep(1)
    #     data_read = self._daq_module.read(True)
    #     time.sleep(1)
    #     return data_read
        #for index, signal_burst in enumerate(data_read[signal_path.lower()]):
        #    data[signal_path].append(signal_burst)
        #data.append()
        #val = data[signal_path][0]['value'][0]
        #signal_path = f"/{self._dev_id}/demods/0/sample.r"
#        val = data[signal_path][0]['value'][0]


        # self._daq_module.execute()
        # data_read = daq_module.read(True)
        # for signal_path in signal_paths:
        #     if signal_path.lower() in returned_signal_paths:
        #         for index, signal_burst in enumerate(data_read[signal_path.lower()]):
        #             data[signal_path].append(signal_burst)
        #
        # #data = self.continuous_data_acquisition_time_domain(acquisition_time, n_bursts = 1, signal_nodes = ["r"], sample_rate=sample_rate)
        # #return data
        # #time.sleep(0.5)
        # signal_path = f"/{self._dev_id}/demods/0/sample.r"
        # val = data[signal_path][0]['value'][0]
        # return val

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
            raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")

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

class MfliScopeModule:
    ##Goals for implementation: 1. configuraiton, 2. cont. data acquisiiton w/o triggering (time domain), 3. cont. data acquisiiton w/o triggering (freq. domain),
    ##4. get data function (get scope records), 5. triggered measuremnets ...
    def __init__(self, mfli_driver):
        self._mfli = mfli_driver
        self._daq  = self._mfli._daq
        self._dev_id = self._mfli._connection_settings["mfli_id"]
        self._scope_module = self._mfli._scope_module
        self._averager_settings =  {"resamplingmode": self._scope_module.getInt("averager/resamplingmode"), "restart": self._scope_module.getInt("averager/restart"), "weight": self._scope_module.getInt("averager/weight")}
        self._misc_settings = {"externalscaling": self._scope_module.getDouble("externalscaling"), "error": self._scope_module.getInt("error"), "clearhistory": self._scope_module.getInt("clearhistory"), "historylength": self._scope_module.getInt("historylength"), "mode": self._scope_module.getInt("mode"), "records": self._scope_module.getInt("records")}
    #    self._save_settings = {"csvlocale": self._scope_module.getString("csvlocale"), "csvseparator": self._scope_module.getString("csvseparator"), "directory": self._scope_module.getString("directory") , "fileformat": self._scope_module.getInt("fileformat"), "save": self._scope_module.getInt("save"), "saveonread": self._scope_module.getInt("saveonread")}
        self._fft_settings = {"power": self._scope_module.getInt("fft/power"), "spectraldensity": self._scope_module.getInt("fft/spectraldensity"), "window": self._scope_module.getInt("fft/window")}

    def get_all_scope_settings(self):
        self._averager_settings =  {"resamplingmode": self._scope_module.getInt("averager/resamplingmode"), "restart": self._scope_module.getInt("averager/restart"), "weight": self._scope_module.getInt("averager/weight")}
        self._misc_settings = {"externalscaling": self._scope_module.getDouble("externalscaling"), "error": self._scope_module.getInt("error"), "clearhistory": self._scope_module.getInt("clearhistory"), "historylength": self._scope_module.getInt("historylength"), "mode": self._scope_module.getInt("mode"), "records": self._scope_module.getInt("records")}
        #self._save_settings = {"csvlocale": self._scope_module.getString("csvlocale"), "csvseparator": self._scope_module.getString("csvseparator"), "directory": self._scope_module.getString("directory") , "fileformat": self._scope_module.getInt("fileformat"), "save": self._scope_module.getInt("save"), "saveonread": self._scope_module.getInt("saveonread")}
        self._fft_settings = {"power": self._scope_module.getInt("fft/power"), "spectraldensity": self._scope_module.getInt("fft/spectraldensity"), "window": self._scope_module.getInt("fft/window")}
    #    return {"averager": self._averager_settings, "misc": self._misc_settings , "save": self._save_settings, "fft": self._fft_settings}
        return {"averager": self._averager_settings, "misc": self._misc_settings , "fft": self._fft_settings}

    #def continuous_scope_time_domain(self):
    # daq.setInt("/%s/scopes/0/length" % device, scope_length)
    # daq.setInt("/%s/scopes/0/channel" % device, 1)
    # daq.setInt("/%s/scopes/0/channels/%d/bwlimit" % (device, scope_in_channel), 1)
    # daq.setInt("/%s/scopes/0/channels/%d/inputselect" % (device, scope_in_channel), inputselect)
    # scope_time = 0
    # daq.setInt("/%s/scopes/0/time" % device, scope_time)
    # daq.setInt("/%s/scopes/0/single" % device, 0)
    # daq.setInt("/%s/scopes/0/trigenable" % device, 0)
    # daq.setDouble("/%s/scopes/0/trigholdoff" % device, trigholdoff)
    # daq.sync()
    # scopeModule = daq.scopeModule()
    # scopeModule.set("mode", 1)
    # scopeModule.set("averager/weight", averager_weight)
    # scopeModule.set("historylength", historylength)
    # wave_nodepath = f"/{device}/scopes/0/wave"
    # scopeModule.subscribe(wave_nodepath)
    # data_no_trig = get_scope_records(device, daq, scopeModule, min_num_records)

    #def continuous_scope_freq_domain(self):

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
class MfliScopeModulePoint:
##Goals for implementation: 1. configuraiton, 2. cont. data acquisiiton w/o triggering (time domain), 3. cont. data acquisiiton w/o triggering (freq. domain),
##4. get data function (get scope records), 5. triggered measurements ...
    def __init__(self, mfli_driver):
        self._mfli = mfli_driver
        self._daq  = self._mfli._daq
        self._dev_id = self._mfli._connection_settings["mfli_id"]
        self._scope_module = self._mfli._scope_module

        self._counter = 0



    def averaged_point(self, duration,  trace_num = float('inf'), sig_port = 'Aux_in_1'):

        sig_source = { 'sig_in_1': 0 , 'Aux_in_1': 8   }

        sampling_rate_dict = {0: 60e6, 1: 30e6  , 2: 15e6, 3: 7.5e6, 4: 3.75e6, 5: 1.88e6, 6: 938e3, 7: 469e3,  8: 234e3, 9: 117e3,
                              10:58.6e3, 11:29.3e3, 12: 14.6e3, 13: 7.32e3, 14: 3.66e3, 15: 1.83e3, 16: 916   }

        #without this, execute() does not take in data

        #by calling the read function here, it clears whatever data may have been left in the earlier run, allowing us to
        #change the length of each trace and plotting it. Otherwise, there's clash between the size set for the figure and some of
        #the earlier data being fed
        self._scope_module.read()

        sampling_rate_key = self._daq.getInt(f'/{self._dev_id}/scopes/0/time')
        sampling_rate = sampling_rate_dict[sampling_rate_key]

        columns = np.ceil(duration * sampling_rate)


        #set the number of points per trace
        self._daq.setDouble(f'/{self._dev_id}/scopes/0/length', columns)


        self._scope_module.subscribe(f'/{self._dev_id}/scopes/0/wave')

        #you have to give it some time for the proper number of pts per trace to be registered and read back
        time.sleep(0.5)

        #see what was actually accepted for the number of points per trace
        num_of_points_per_trace = self._daq.getInt(f'/{self._dev_id}/scopes/0/length')
        # print(num_of_points_per_trace)


        length_in_sec = num_of_points_per_trace/sampling_rate_dict[sampling_rate_key]

        time_axis = np.linspace(0, length_in_sec,  num_of_points_per_trace)
        # time_axis = np.linspace(0, num_of_points_per_trace,  num_of_points_per_trace)
        v_outputs = np.zeros(num_of_points_per_trace)


        #for some reason, when starting a scope module, 'averager/weight' is set to 10, so you want to set it to 0 for no averaging
        self._scope_module.set('averager/weight', 0)  #"Specify the averaging behaviour. weight=0: Averaging disabled. weight>1: Moving average, updating last history entry.",

        # print()
        # print('trace length', num_of_points_per_trace, 'sampling rate', sampling_rate_dict[sampling_rate_key], 'length in sec', length_in_sec)

        #ratio of the plot size -> figsize=(80, 6), dpi=80

        # centers = [-0.3, 0.3, 0,  length_in_sec]  #this is where you change the scale label

        v_outputs = np.zeros(num_of_points_per_trace)

        #scope turned on
        self._daq.setInt(f'/{self._dev_id}/scopes/0/enable', 1)
        self._daq.setInt(f'/{self._dev_id}/scopes/0/trigenable', 0)    #disable trigger (just in case it was enabled before)

        self._daq.setInt(f'/{self._dev_id}/scopes/0/stream/enables/0', 0)  #disable the continuous streaming
        self._daq.setInt(f'/{self._dev_id}/scopes/0/stream/enables/1', 0)

        self._scope_module.execute()

        # self._daq.setInt(f'/{self._dev_id}/scopes/0/channels/0/inputselect', 0)  #assume we are measuring signal in 1
        self._daq.setInt(f'/{self._dev_id}/scopes/0/channels/0/inputselect', sig_source[sig_port])  #assume we are measuring Aux in 1

        counter = 0    #keeping track of the num of traces being stored.  only for testing
        sample_data = []
        result = {}

        #if set to infinite, keep running the scope module

        if trace_num == float('inf'):

            while not self._scope_module.finished() and len(sample_data)< trace_num:
                result = self._scope_module.read()
                if len(result) != 0 and self._dev_id in result.keys():  #the read function is much faster than how often data get transferred from the module
                    # print(len(result[self._dev_id]['scopes']['0']['wave']), 'this is the number?')  #how many traces is each call returning?
                    counter += len(result[self._dev_id]['scopes']['0']['wave'])

        else:
            #keep in mind that the data stream is uncontrolled, so sample_data being returned may end up with more than
            while not self._scope_module.finished() and len(sample_data)< trace_num:

                result = self._scope_module.read()

                if len(result) != 0 and self._dev_id in result.keys():  #the read function is much faster than how often data get transferred from the module
                    for each_trace_index in range(len(result[self._dev_id]['scopes']['0']['wave'])):

                        sample_data.append( result[self._dev_id]['scopes']['0']['wave'][each_trace_index][0]['wave'][0]  )

                    # print(len(result[self._dev_id]['scopes']['0']['wave']), 'this is the number?')  #how many traces is each call returning?
                    counter += len(result[self._dev_id]['scopes']['0']['wave'])


            #scope turned off
            self._daq.setInt(f'/{self._dev_id}/scopes/0/enable', 0)

            #in case there's some leftover data collected before exiting the conditional statements, we will append them to the 'sample_data'
            if self._dev_id in result.keys():
                for each_trace_index in range(len(result[self._dev_id]['scopes']['0']['wave'])):

                    sample_data.append( result[self._dev_id]['scopes']['0']['wave'][each_trace_index][0]['wave'][0]  )

            # print(len(result['dev6541']['scopes']['0']['wave']), 'num of traces of leftover data')

            # print(self._scope_module.getInt("records"), 'this is the final number before closing',   len(sample_data), 'length of the sample data')


            #this block of code here is being used to have a well defined stop to the data acquisition
            self._daq.setInt(f'/{self._dev_id}/scopes/0/enable', 0)
            self._scope_module.finish()
            self._scope_module.unsubscribe('*')
            self._scope_module.unsubscribe('*')
            self._scope_module.subscribe(f'/{self._dev_id}/scopes/0/wave')


            return np.mean(sample_data)
