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

    def __init__(self, dev_id, name = "hdawg_1", server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE"):
       #  '''
      #  Constructs all the necessary attributes for the person object.

       # Parameters
      #  ----------
      #      dev_id : str
      #          Device ID for AWG.
      #      server_host : str
      #          Server  host name (default = "localhost").
      #      server_port : int
      #          Port number for the host server (default = 8004).
      #      api_level : int
      #          API level of instrument (default = 6, for HDAWG).
      #      interface : str
      #          Interface used to connect to server (default = "1GbE" for ethernet connection).
      #  '''

        ##Part 1: connect to instrument
        # ##Should add exception handeling here
        self._connection_settings = {"hdawg_name": name, "hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level , "interface" : interface, "connection_status" : False}
        self._hdawg = tk.HDAWG(self._connection_settings["hdawg_name"],self._connection_settings["hdawg_id"])
        self._hdawg.setup()
        self._hdawg.connect_device()
        ##check if connected: (1) yes ==> move forward, (2) no ==> throw exception
        self._oscillator_freq = {"osc1" :self._hdawg.nodetree.oscs[0].freq(), "osc2" :self._hdawg.nodetree.oscs[1].freq(), "osc3" :self._hdawg.nodetree.oscs[2].freq(), "osc4" :self._hdawg.nodetree.oscs[3].freq(), "osc5" :self._hdawg.nodetree.oscs[4].freq(), "osc6" :self._hdawg.nodetree.oscs[5].freq(), "osc7" :self._hdawg.nodetree.oscs[6].freq(), "osc8" :self._hdawg.nodetree.oscs[7].freq(), "osc9" :self._hdawg.nodetree.oscs[8].freq(), "osc10" :self._hdawg.nodetree.oscs[9].freq(), "osc11" :self._hdawg.nodetree.oscs[10].freq(), "osc12" :self._hdawg.nodetree.oscs[11].freq(), "osc13" :self._hdawg.nodetree.oscs[12].freq(), "osc13" :self._hdawg.nodetree.oscs[12].freq(), "osc14" :self._hdawg.nodetree.oscs[13].freq(), "osc15" :self._hdawg.nodetree.oscs[14].freq(), "osc16" :self._hdawg.nodetree.oscs[15].freq()}

        self._sines = {"sin1" : {"osc" : self._hdawg.nodetree.sines[0].oscselect(), "phaseshift": self._hdawg.nodetree.sines[0].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[0].harmonic(), "amp1" : self._hdawg.nodetree.sines[0].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[0].amplitudes[1]}, "sin2" : {"osc" : self._hdawg.nodetree.sines[1].oscselect(), "phaseshift": self._hdawg.nodetree.sines[1].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[1].harmonic(), "amp1" : self._hdawg.nodetree.sines[1].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[1].amplitudes[1]}, "sin3" : {"osc" : self._hdawg.nodetree.sines[2].oscselect(), "phaseshift": self._hdawg.nodetree.sines[2].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[2].harmonic(), "amp1" : self._hdawg.nodetree.sines[2].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[2].amplitudes[1]}, "sin4" : {"osc" : self._hdawg.nodetree.sines[3].oscselect(), "phaseshift": self._hdawg.nodetree.sines[3].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[3].harmonic(), "amp1" : self._hdawg.nodetree.sines[3].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[3].amplitudes[1]}, "sin5" : {"osc" : self._hdawg.nodetree.sines[4].oscselect(), "phaseshift": self._hdawg.nodetree.sines[4].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[4].harmonic(), "amp1" : self._hdawg.nodetree.sines[4].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[4].amplitudes[1]}, "sin6" : {"osc" : self._hdawg.nodetree.sines[5].oscselect(), "phaseshift": self._hdawg.nodetree.sines[5].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[5].harmonic(), "amp1" : self._hdawg.nodetree.sines[5].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[5].amplitudes[1]}, "sin7" : {"osc" : self._hdawg.nodetree.sines[6].oscselect(), "phaseshift": self._hdawg.nodetree.sines[6].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[6].harmonic(), "amp1" : self._hdawg.nodetree.sines[6].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[6].amplitudes[1]}, "sin8" : {"osc" : self._hdawg.nodetree.sines[7].oscselect(), "phaseshift": self._hdawg.nodetree.sines[7].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[0].harmonic(), "amp1" : self._hdawg.nodetree.sines[7].amplitudes[0] , "amp2" :self._hdawg.nodetree.sines[7].amplitudes[1]}}
        self._awgs = {"awg1" : self._hdawg.nodetree.awgs[0], "awg2" : self._hdawg.nodetree.awgs[1], "awg3" : self._hdawg.nodetree.awgs[2], "awg4" : self._hdawg.nodetree.awgs[3]}
        self._output_amps = {"awg1" : {"out1" : self._awgs["awg1"].outputs[0].amplitude, "out2" : self._awgs["awg1"].outputs[1].amplitude}, "awg2" : {"out1" : self._awgs["awg2"].outputs[0].amplitude, "out2" : self._awgs["awg2"].outputs[1].amplitude}, "awg3" : {"out1" : self._awgs["awg3"].outputs[0].amplitude, "out2" : self._awgs["awg3"].outputs[1].amplitude}, "awg4" : {"out1" : self._awgs["awg4"].outputs[0].amplitude, "out2" : self._awgs["awg4"].outputs[1].amplitude}}
        self._sequencers = {"awg1" : {"positions" : self._awgs["awg1"].sequencer.pc, "status" :self._awgs["awg1"].sequencer.status , "memoryusage" : self._awgs["awg1"].sequencer.memoryusage, "triggered" : self._awgs["awg1"].sequencer.triggered, "program" :  self._awgs["awg1"].sequencer.program}, "awg2" : {"positions" : self._awgs["awg2"].sequencer.pc, "status" :self._awgs["awg2"].sequencer.status , "memoryusage" : self._awgs["awg2"].sequencer.memoryusage, "triggered" : self._awgs["awg2"].sequencer.triggered, "program" :  self._awgs["awg2"].sequencer.program}, "awg3" : {"positions" : self._awgs["awg3"].sequencer.pc, "status" :self._awgs["awg3"].sequencer.status , "memoryusage" : self._awgs["awg3"].sequencer.memoryusage, "triggered" : self._awgs["awg3"].sequencer.triggered, "program" :  self._awgs["awg3"].sequencer.program}, "awg4" : {"positions" : self._awgs["awg4"].sequencer.pc, "status" :self._awgs["awg4"].sequencer.status , "memoryusage" : self._awgs["awg4"].sequencer.memoryusage, "triggered" : self._awgs["awg4"].sequencer.triggered, "program" :  self._awgs["awg4"].sequencer.program}}

        self._ref_clock_status = self._hdawg.ref_clock_status()
        self._output_status = {"awg1" : {"out1" : self._hdawg.awgs[0].output1(), "out2" : self._hdawg.awgs[0].output1()}, "awg2" : {"out1" : self._hdawg.awgs[1].output1(), "out2" : self._hdawg.awgs[1].output1()},  "awg3" : {"out1" : self._hdawg.awgs[2].output1(), "out2" : self._hdawg.awgs[2].output1()}, "awg4" : {"out1" : self._hdawg.awgs[3].output1(), "out2" : self._hdawg.awgs[3].output1()}}
        self._modulation_freqs = {"awg1": self._hdawg.awgs[0].modulation_freq(), "awg2": self._hdawg.awgs[1].modulation_freq(), "awg3": self._hdawg.awgs[2].modulation_freq(), "awg4": self._hdawg.awgs[3].modulation_freq()}
        self._modulation_phase_shifts = {"awg1": self._hdawg.awgs[0].modulation_phase_shift(), "awg2": self._hdawg.awgs[1].modulation_phase_shift(), "awg3": self._hdawg.awgs[2].modulation_phase_shift(), "awg4": self._hdawg.awgs[3].modulation_phase_shift()}
        self._gains = {"awg1": {"gain1" : self._hdawg.awgs[0].gain1() , "gain2" : self._hdawg.awgs[0].gain2()}, "awg2": {"gain1" : self._hdawg.awgs[1].gain1() , "gain2" : self._hdawg.awgs[1].gain2()}, "awg3": {"gain1" : self._hdawg.awgs[2].gain1() , "gain2" : self._hdawg.awgs[2].gain2()}, "awg4": {"gain1" : self._hdawg.awgs[3].gain1() , "gain2" : self._hdawg.awgs[3].gain2()}}
        # self._markers = [# self._triggers = []
        # self._clocks = []
        # self._clocks_status = []
        # self._channel_config  = { }
        #  - channel config
        #  - oscillators
        # - signal outputs
        #  - channel config
        #  -

   #  def open_connection(self):
   #   # """
   #   #  Initializes connection with HDAWG instrument via server.
   #   #
   #   #    First...
   #   #
   #   #    Parameters
   #   #    ----------
   #   #    additional : str, optional
   #   #        More info to be displayed (default is None)
   #   #
   #   #    Returns
   #   #    -------
   #   #    None
   #   #  """
   #
   #    self._hdawg.setup()
   #     self._hdawg.connect_device()
   #     self._connection_settings["connection_status"] = True
   #      ## add message of succeessful connection for each
   #      ## add try, catch for exception handeling
   #
   #  def set_osc_freq(self, osc_freqs, phaseshift, ):
   #      ## exception for osc_freqs type: dict
   #      ##add exception for type real and bounded for each frequency
   #
   #     for key in osc_freqs:
   #        self._oscillator_freqs[key] = oscs_freq[key]
   #        osc_idx = int(key[3])-1
   #        self._hdawg.nodetree.oscs[osc_idx].freq(self._oscillator_freqs[key])
   #
   # def get_osc_freq(self, oscs):
   #      ## exception for oscs type: list or str ==> check that format is 'osc' + int
   #    osc_freqs = {}
   #    for osc in oscs:
   #       osc_idx = int(osc[3])-1
   #       oscs_freqs[osc] = self._hdawg.nodetree.oscs[osc_idx]
   #    return osc_freqs
   #
   # def set_sine_wave(self, sinewave, osc, harmonic, amp1, amp2):
   #    self._sines[sinewave]["osc"] = osc
   #    self._sines[sinewave]["harmonic"] = harmonic
   #    self._sines[sinewave]["amp1"] = amp1
   #    self._sines[sinewave]["amp2"] = amp2
   #    self._hdawg.nodetree.sines[1].oscselect(osc)
   #    self._hdawg.nodetree.sines[1].harmonic(harmonic)
   #    self._hdawg.nodetree.sines[1].amplitudes[0]  = amp1
   #    self._hdawg.nodetree.sines[1].amplitudes[1]  = amp2
   #
   # def get_sine_wave(self, sinewave):
   #    ## sinewave: label for sinewave
   # return self._sines[sinewave]
   #
   # def get_awgcore(self, core_id):
   #    return self._awgs[core_id]














    # def open_connection(self):
    #  """
    #     Initializes connection with HDAWG instrument via server.
    #
    #     First...
    #
    #
    #
    #     Parameters
    #     ----------
    #     additional : str, optional
    #         More info to be displayed (default is None)
    #
    #     Returns
    #     -------
    #     None
    #   """
    #
    # ## add exception handeling
    # self._hdawg.setup()
    # self._hdawg.connect_device()
    # connect_status = self._hdawg.is_connected()
    # self._connection_settings["connection_status"] = connect_status
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

    #def set_channel_grouping(self, value):
        # """
        # Sets channel grouping for AWG. Cases:
        #
        # - value = 0: 4 AWG cores, assigns awgModule/index = [0,1,2,3] to AWG cores [1,2,3,4]
        # - value = 1: 2 AWG cores, assigns awgModule/index = [0,1] to AWG cores [1,2]
        # - value = 2: 1 AWG cores, assigns awgModule/index = [0] to AWG core [1]
        #
        # Parameters
        # ----------
        # additional : str, optional
        # More info to be displayed (default is None)
        #
        # Returns
        # -------
        # None
        # """
        # ## add exception here
        # self._channel_grouping = value
        # self._daq.setInt(f"/{device}/system/awg/channelgrouping", self._channel_grouping)
        #



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
