#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk

class HdawgDriver:
    '''
    Driver class for ZI-HDAWG (Zurich arbitrary waveform generator) instrument.

    >>> hd = HdawgDriver("hdawg_name", "dev8030")
    >>> hd.setup()

    ...

    Attributes
    - - - - - - -
    hdawg_id : str
        ID number for ZI-HDAWG.

    sequence :

    triggers :

    clock :

    clock_status :



    Methods
    - - - - - - -
    example (additional=" "):
        Print ...
    '''

    def __init__(self, dev_id, name = "hdawg_1", server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE", **kwargs):
       """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            dev_id : str
                Device ID for AWG.
            server_host : str
                Server  host name (default = "localhost").
            server_port : int
                Port number for the host server (default = 8004).
            api_level : int
                API level of instrument (default = 6, for HDAWG).
            interface : str
                Interface used to connect to server (default = "1GbE" for ethernet connection).
        """

        # ##Should add exception handeling here
        self._connection_settings = {"hdawg_name": name, "hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level , "interface" : interface, "connection_status" : False}
        self._hdawg = HDAWG(self._connection_settings["hdawg_name"],self._connection_settings["hdawg_id"])
        #self._

        # ## Channel groupings (int): 0- 4x2 , 1- 2x4 , 2- 1x8
        # self._channel_grouping = 0
        # #self._sequencers = {"channel_grouping": , "sequence" }
        # self._oscillators = {"osc1": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc2": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc3": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc4":{"freq": 10e6, "harmonic": 1 , "phase": 0.0 } ,
        # "osc5": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc6": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc7": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc8": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }}
        # self._sin_out_amps = {"wav1": {"oscA": "osc1", "oscB": "osc2", "oscA_V": 1,  "oscB_V": 1 } , "wav2": {"oscA": "osc1", "oscB": "osc2", "oscA_V": 1,  "oscB_V": 1 }  , "wav3": {"oscA": "osc3", "oscB": "osc4", "oscA_V": 1,  "oscB_V": 1 } , "wav4": {"oscA": "osc3", "oscB": "osc4", "oscA_V": 1,  "oscB_V": 1 }  ,
        # "wav5": {"oscA": "osc5", "oscB": "osc6", "oscA_V": 1,  "oscB_V": 1 }  , "wav6": {"oscA": "osc5", "oscB": "osc6", "oscA_V": 1,  "oscB_V": 1 } , "wav7": {"oscA": "osc7", "oscB": "osc8", "oscA_V": 1,  "oscB_V": 1 }, "wav8": {"oscA": "osc7", "oscB": "osc8", "oscA_V": 1,  "oscB_V": 1 } }
        # self._waves_out_amps = {"wav1": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav2": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav3": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav4": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1},
        #  "wav5": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1} , "wav6": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav7": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav8": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}}
        # self._device = None
        # self._daq = None
        #self._awgmodule  =
        # self._markers = []
        # self._triggers = []
        # self._clocks = []
        # self._clocks_status = []
        # self._channel_config  = { }
        #  - channel config
        #  - oscillators
        # - signal outputs
        #  - channel config
        #  -

    def open_connection(self):
     """
        Initializes connection with HDAWG instrument via server.

        First...



        Parameters
        ----------
        additional : str, optional
            More info to be displayed (default is None)

        Returns
        -------
        None
      """

    ## add exception handeling
    self._hdawg.setup()
    self._hdawg.connect_device()
    connect_status = self._hdawg.is_connected()
    self._connection_settings["connection_status"] = connect_status
    # dev_id = self._connection_settings["hdawg_id"]
    # api_level = self._connection_settings["api_level"]
    # server_host = self._connection_settings["server_host"]
    # server_port = self._connection_settings["server_port"]
    # self._daq, self._device, _ = zhinst.utils.create_api_session(dev_id, api_level, server_host=server_host, server_port=server_port)
    # zhinst.utils.api_server_version_check(self._daq)
    # zhinst.utils.disable_everything(self._daq, self._device)


    # def close_connection(self):
    #    d= 1
    #

    def set_channel_grouping(self, value):
        """
        Sets channel grouping for AWG. Cases:

        - value = 0: 4 AWG cores, assigns awgModule/index = [0,1,2,3] to AWG cores [1,2,3,4]
        - value = 1: 2 AWG cores, assigns awgModule/index = [0,1] to AWG cores [1,2]
        - value = 2: 1 AWG cores, assigns awgModule/index = [0] to AWG core [1]

        Parameters
        ----------
        additional : str, optional
        More info to be displayed (default is None)

        Returns
        -------
        None
        """
        ## add exception here
        self._channel_grouping = value
        self._daq.setInt(f"/{device}/system/awg/channelgrouping", self._channel_grouping)




    #def init_config(self):
    #    d=1


    # def value_setter(self):
    #     d=1
    #
    # def value_getter(self):
    #     d=1
    #
    # def awg_start_stop(self):
    #     d=1
    #
    # def queue_waveforms(self):
    #     d=1
    #
    # def sequence_getter(self):
    #     d=1
    #
    # def sequence_compiler(self):
    #     d=1

    ## def enable
