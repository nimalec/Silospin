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

        self._sigin_channel = {"ac": self._mfli.nodetree.sigin.ac(),
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
        ,"timeconstant": self._mfli.nodetree.demods[0].timeconstant()},
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
        #self._threshold_settings = {}


    def connect_device(self):
        self._mfli = tk.MFLI(self._connection_settings["li_name"], self._connection_settings["li_id"])
        self._mfli.setup()
        self._mfli.connect_device()
        self._connection_settings["connection_status"] = self._mfli.is_connected

    def set_input_channel(self, input_channel, setting, value):
        input_channels = {"auxin_1", "auxin_2", "sigin", "currin"}
        try:
            if type(input_channel) is not str:
                raise TypeError("'input_channel' should be a string.")
        except TypeError:
            raise

        try:
            if input_channel not in input_channels:
                raise ValueError("'input_channel' must be in input_channels.")
        except ValueError:
            raise

        if setting == "auxin_1" or setting == "auxin_2":
            try:
                if setting is not "n_av":
                    raise ValueError("'param' must be n_av")
            except ValueError:
                raise

            if setting == "auxin_1":
                self._mfli.nodetree.auxin.averaging[0](value)
                self._auxin_channels["auxin_1"]["n_av"] = value

            else:
                self._mfli.nodetree.auxin.averaging[1](value)
                self._auxin_channels["auxin_2"]["n_av"] = value

        elif setting == "sigin":
            sigin_settings = {"ac", "autorange", "diff", "float", "imp50", "max", "min", "on", "scaling", "trigger"}
            try:
                if setting not in sigin_settings:
                    raise ValueError("setting not in sigin settings")
            except ValueError:
                raise
            exec("self._mfli.nodetree.sigin."+setting+"("+str(value)+")")
            self._sigin_channel[setting] = value

        else:
            currin_settings = {"autorange", "float", "max", "min",  "on", "range"}
            try:
                if setting is not in currin_settings:
                    raise ValueError("setting not in currin settings")
            except ValueError:
                raise
            exec("self._mfli.nodetree.currin."+setting+"("+str(value)+")")
            self._currin_channel[setting] = value

    def get_input_channel_value(self, input_channel, setting):
          ##check this function again
        input_channels = {"auxin_1", "auxin_2", "sigin", "currin"}
        try:
            if type(setting) is not str:
                raise TypeError("'setting' should be a string.")
        except TypeError:
            raise

        try:
            if input_channel not in input_channels:
                raise ValueError("'setting' must be in input_channels.")
        except ValueError:
            raise

        if setting == "auxin_1":
            value = self._mfli.nodetree.auxin[0].values()
        elif setting == "auxin_2":
            value = self._mfli.nodetree.auxin[1].values()
        elif setting = "sigin":
            value = self._mfli.nodetree.sigin
        else:
            value = self._mfli.nodetree.currin
        return value

    def set_output_channel_setting(self, output_channel, setting, value):
        output_channels = {"auxout_1", "auxout_2", "auxout_3", "auxout_4", "sigout"}
        try:
            if type(output_channel) is not str:
                raise TypeError("'output_channel' should be a string.")
        except TypeError:
            raise
        try:
            if type(setting) is not str:
                raise TypeError("'output_channel' should be a string.")
        except TypeError:
            raise
        try:
            if output_channel not in output_channels:
                raise ValueError("'output_channel' must be in output_channels.")
        except ValueError:
            raise

        if output_channel == "auxout_1" or output_channel == "auxout_2" or output_channel == "auxout_3" or output_channel == "auxout_4":
            auxout_settings = {"demodselect", "limitlower", "limitupper", "offset", "outputselect", "preoffset", "scale"}
            try:
                if input_channel not in output_channels:
                    raise ValueError("'output_channel' must be in output_channels.")
            except ValueError:
                raise
            if output_channel == "auxout_1":
                exec("self._mfli.nodetree.auxouts[0]."+setting+"("+str(value)+")")

            elif output_channel == "auxout_2":
                exec("self._mfli.nodetree.auxouts[1]."+setting+"("+str(value)+")")

            elif output_channel == "auxout_3":
                exec("self._mfli.nodetree.auxouts[2]."+setting+"("+str(value)+")")
            else:
                exec("self._mfli.nodetree.auxouts[3]."+setting+"("+str(value)+")")
        else:
            sigout_settings = {"add", "autorange", "diff", "imp50", "offset", "on", "range", "amplitude", "enables"}
            exec("self._mfli.nodetree.sigouts."+setting+"("+str(value)+")")

    def get_output_channel_value(self, get_output_channel_setting):
        output_channels = {"auxout_1", "auxout_2", "auxout_3", "auxout_4", "sigout"}
        try:
            if type(output_channel) is not str:
                raise TypeError("'output_channel' should be a string.")
        except TypeError:
            raise
        try:
            if type(setting) is not str:
                raise TypeError("'output_channel' should be a string.")
        except TypeError:
            raise
        try:
            if output_channel not in output_channels:
                raise ValueError("'output_channel' must be in output_channels.")
        except ValueError:
            raise

        if output_channel == "auxout_1":
            value = self._mfli.nodetree.auxouts[0].value()
        elif output_channel == "auxout_2":
            value = self._mfli.nodetree.auxouts[1].value()
        elif output_channel == "auxout_3":
            value = self._mfli.nodetree.auxouts[2].value()
        elif output_channel == "auxout_4":
            value = self._mfli.nodetree.auxouts[3].value()
        else:
            value = self._mfli.nodetree.sigouts
        return value

    def set_demodulator(self, channel, demod_setting, value):
        demod_settings = {"adcselect", "bypass", "freq", "harmonic", "order", "osc_sel", "phaseadjust", "phaseshift", "rate", "sample", "sinc", "timeconstant"}
        try:
            if type(channel) is not int:
                raise TypeError("'channel' should be an integer.")
        except TypeError:
            raise
        try:
            if channel != 1 or channel != 2:
                raise ValueError("'channel' should be an integer.")
        except ValueError:
            raise
        try:
            if type(demod_setting) is not str:
                raise TypeError("'demod_setting' should be a string.")
        except TypeError:
            raise
        try:
            if demod_setting not in demod_settings:
                raise ValueError("'output_channel' must be in output_channels.")
        except ValueError:
            raise

        if channel == 1:
            exec("self._mfli.nodetree.demods[0]."+demod_setting+"("+str(value)+")")
        else:
            exec("self._mfli.nodetree.demods[1]."+demod_setting+"("+str(value)+")")

   def get_demodulator_setting(self, channel, demod_setting):
       settings = {"adcselect", "bypass", "freq", "harmonic", "order", "osc_sel", "phaseadjust", "phaseshift", "rate", "sample", "sinc", "timeconstant"}
       try:
           if type(channel) is not int:
               raise TypeError("'channel' should be an integer.")
       except TypeError:
           raise
       try:
           if channel != 1 or channel != 2:
               raise ValueError("'channel' should be an integer.")
       except ValueError:
           raise
       try:
           if type(demod_setting) is not str:
               raise TypeError("'demod_setting' should be a string.")
       except TypeError:
           raise
       try:
           if demod_setting not in demod_settings:
               raise ValueError("'output_channel' must be in output_channels.")
       except ValueError:
           raise

       if channel == 1:
           exec("value = self._mfli.nodetree.demods[0]."+demod_setting+"("+str(value)+")")
       else:
           exec("value = self._mfli.nodetree.demods[1]."+demod_setting+"("+str(value)+")")
       return value

   def set_trigger(self, channel, in_out, trig_setting, value):
       try:
           if channel != 1 or channel != 2:
               raise ValueError("'channel' should be an integer.")
       except ValueError:
           raise
       try:
           if in_out != "in" or in_out != "out" :
               raise ValueError("'in_out' should be 'in' or 'out'.")
       except ValueError:
           raise
       try:
           if trig_setting is not in {"autothreshold", "level", "pulse_width", "source"}:
               raise ValueError("'trig_setting' should be autothreshold , level, pulse_width, source")
       except ValueError:
           raise

       if in_out == "in" and channel == 1:
           exec("self._mfli.nodetree.triggers.in_[0]."+trig_setting+".("+str(value)+")")
       elif in_out == "in" and channel == 2:
           exec("self._mfli.nodetree.triggers.in_[1]."+trig_setting+".("+str(value)+")")
       elif in_out == "out" and channel == 1:
           exec("self._mfli.nodetree.triggers.out[0]."+trig_setting+".("+str(value)+")")
       else:
           exec("self._mfli.nodetree.triggers.out[1]."+trig_setting+".("+str(value)+")")

    def get_trigger(self, channel, in_out, trig_setting):
        try:
            if channel != 1 or channel != 2:
                raise ValueError("'channel' should be an integer.")
        except ValueError:
            raise
        try:
            if in_out != "in" or in_out != "out" :
                raise ValueError("'in_out' should be 'in' or 'out'.")
        except ValueError:
            raise
        try:
            if trig_setting is not in {"autothreshold", "level", "pulse_width", "source"}:
                raise ValueError("'trig_setting' should be autothreshold , level, pulse_width, source")
        except ValueError:
            raise

        if in_out == "in" and channel == 1:
            exec("value = self._mfli.nodetree.triggers.in_[0]."+trig_setting+".()")
        elif in_out == "in" and channel == 2:
            exec("value = self._mfli.nodetree.triggers.in_[1]."+trig_setting+".()")
        elif in_out == "out" and channel == 1:
            exec("value = self._mfli.nodetree.triggers.out[0]."+trig_setting+".()")
        else:
            exec("value = self._mfli.nodetree.triggers.out[1]."+trig_setting+".()")
        return value

    #def set_sweeper(self):

    #def get_sweeper(self):
    #def set_daq(self):
    #def get_daq(self):
    #def start_measurement(self):
    #def stop_measurement(self):
