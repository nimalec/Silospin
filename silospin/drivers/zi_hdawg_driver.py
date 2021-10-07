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
        self._connection_settings = {"hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level , "interface" : interface, "connection_status" : "unconnected"}
        # self._sequencers = 
        # self._waves = []
        # self._markers = []
        # self._triggers = []
        # self._clocks = []
        # self._clocks_status = []
        # self._channel_config  = { }




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
