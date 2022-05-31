#!/usr/bin/env python
import zhinst
import zhinst.utils
import json
from zhinst.toolkit import Session
#import zhinst.toolkit as tk
import numpy as np

class MFLIDriver:
    """
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
    """

    def __init__(self, dev_id, server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE"):
        ## device.modules.root:
        ##  - auxins
        ##  - auxouts
        ##  - currins
        ##  - demods
        ##-  dios
        ##-  extrefs
        #-   oscs
        #-   sigins
        #-   sigouts
        self._connection_settings = {"mfli_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "interface" : interface, "connection_status" : False}
        self._session = Session(server_host)
        self._mfli = self._session.connect_device(dev_id)

        self._freq = self._mfli.oscs[0].freq()
        self._demods = [
        { "x":  self._mfli.demods[0].sample()["x"][0] , "y": self._mfli.demods[0].sample()["y"][0] , "freq": self._mfli.demods[0].sample()["frequency"][0], "phase":
        self._mfli.demods[0].sample()["phase"][0] , "auxin0": self._mfli.demods[0].sample()["auxin0"][0] , "auxin1": self._mfli.demods[0].sample()["auxin1"][0],
         "rate": self._mfli.demods[0].rate()  , "enable": self._mfli.demods[0].enable(),  "trigger":
        self._mfli.demods[0].trigger()}, {"x":  self._mfli.demods[1].sample()["x"][0] , "y": self._mfli.demods[0].sample()["y"][1] , "freq": self._mfli.demods[1].sample()["frequency"][0], "phase":
          self._mfli.demods[1].sample()["phase"][0] , "auxin0": self._mfli.demods[1].sample()["auxin0"][0] , "auxin1": self._mfli.demods[1].sample()["auxin1"][0],
        "rate": self._mfli.demods[1].rate() , "enable": self._mfli.demods[1].enable(),  "trigger":
        self._mfli.demods[1].trigger()}]

        self._sigins  = {"diff":  , "ac":  , "on": , "trigger": ,  }

        self._sigouts = {"imp50":  , "diff": , "on": , "range": ,"over": , "offset": , "enable": , "amplitude":  }

        self._auxins  = {"average_num": , "val0": , "val1":  }
        self._auxouts = {}

        self._daq = self._session.daq_server



        ## session.modules:
        # - daq
        #- impedence
        #- create_daq_module
        #- create_sweeper_module
        #-device_settings
        #- sweeper
