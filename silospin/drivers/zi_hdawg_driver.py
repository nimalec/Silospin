#!/usr/bin/env python
import zhinst
import zhinst.utils

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

    def __init__(self, dev_id, server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE", **kwargs):
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

        ##Should add exception handeling here
        self._connection_settings = {"hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level , "interface" : interface, "connection_status" : 0}
        ## Channel groupings (int): 0- 4x2 , 1- 2x4 , 2- 1x8
        self._sequencers = {"channel_grouping":  }
        self._oscillators = {"osc1": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc2": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc3": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc4":{"freq": 10e6, "harmonic": 1 , "phase": 0.0 } ,
        "osc5": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc6": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 } , "osc7": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }, "osc8": {"freq": 10e6, "harmonic": 1 , "phase": 0.0 }}
        self._sin_out_amps = {"wav1": {"oscA": "osc1", "oscB": "osc2", "oscA_V": 1,  "oscB_V": 1 } , "wav2": {"oscA": "osc1", "oscB": "osc2", "oscA_V": 1,  "oscB_V": 1 }  , "wav3": {"oscA": "osc3", "oscB": "osc4", "oscA_V": 1,  "oscB_V": 1 } , "wav4": {"oscA": "osc3", "oscB": "osc4", "oscA_V": 1,  "oscB_V": 1 }  ,
        "wav5": {"oscA": "osc5", "oscB": "osc6", "oscA_V": 1,  "oscB_V": 1 }  , "wav6": {"oscA": "osc5", "oscB": "osc6", "oscA_V": 1,  "oscB_V": 1 } , "wav7": {"oscA": "osc7", "oscB": "osc8", "oscA_V": 1,  "oscB_V": 1 }, "wav8": {"oscA": "osc7", "oscB": "osc8", "oscA_V": 1,  "oscB_V": 1 } }
        ## Channel groupings (int): 0- 4x2 , 1- 2x4 , 2- 1x8
        self._waves_out_amps = {"wav1": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav2": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav3": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav4": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1},
         "wav5": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1} , "wav6": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav7": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}, "wav8": {"mod1": "off", "mod2": "off", "mod1_V": 1, "mod2_V": 1}}
        # self._markers = []
        # self._triggers = []
        # self._clocks = []
        # self._clocks_status = []
        # self._channel_config  = { }
        #  - channel config
        #  - oscillators
        # - signal outputs
         # - sine generators
        #  -
        #  -
        #
         #
        #  - channel config
        #  -
        #
         #




    def open_connection(self):
     """
        Prints the person's name and age.

        If the argument 'additional' is passed, then it is appended after the main info.

        Parameters
        ----------
        additional : str, optional
            More info to be displayed (default is None)

        Returns
        -------
        None
      """
      d = 1

    def close_connection(self):
       d= 1
    #
    # def init_config(self):
    #     d=1
    #
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
