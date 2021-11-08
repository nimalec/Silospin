#!/usr/bin/env python
import zhinst
import zhinst.utils
import zhinst.toolkit as tk

class HdawgDriver:
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

    def __init__(self, dev_id, name = "hdawg_1", server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE"):
        """
         Constructor for HDAWG Driver.

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

           Returns
           -------
           None.
        """
        ##Part 1: connect to instrument
        # ##Should add exception handeling here
        self._connection_settings = {"hdawg_name": name, "hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "interface" : interface, "connection_status" : False}
        self._hdawg = tk.HDAWG(self._connection_settings["hdawg_name"],self._connection_settings["hdawg_id"])
        self._hdawg.setup()
        self._hdawg.connect_device()
        self._connection_settings["connection_status"] = self._hdawg.is_connected
        self._oscillator_freq = {"osc1" :self._hdawg.nodetree.oscs[0].freq(), "osc2" :self._hdawg.nodetree.oscs[1].freq(), "osc3" :self._hdawg.nodetree.oscs[2].freq(), "osc4" :self._hdawg.nodetree.oscs[3].freq(), "osc5" :self._hdawg.nodetree.oscs[4].freq(), "osc6" :self._hdawg.nodetree.oscs[5].freq(), "osc7" :self._hdawg.nodetree.oscs[6].freq(), "osc8" :self._hdawg.nodetree.oscs[7].freq(), "osc9" :self._hdawg.nodetree.oscs[8].freq(), "osc10" :self._hdawg.nodetree.oscs[9].freq(), "osc11" :self._hdawg.nodetree.oscs[10].freq(), "osc12" :self._hdawg.nodetree.oscs[11].freq(), "osc13" :self._hdawg.nodetree.oscs[12].freq(), "osc13" :self._hdawg.nodetree.oscs[12].freq(), "osc14" :self._hdawg.nodetree.oscs[13].freq(), "osc15" :self._hdawg.nodetree.oscs[14].freq(), "osc16" :self._hdawg.nodetree.oscs[15].freq()}
        self._sines = {"sin1" : {"osc" : self._hdawg.nodetree.sines[0].oscselect(), "phaseshift": self._hdawg.nodetree.sines[0].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[0].harmonic(), "amp1" : self._hdawg.nodetree.sines[0].amplitudes[0]() , "amp2" :self._hdawg.nodetree.sines[0].amplitudes[1]()}, "sin2" : {"osc" : self._hdawg.nodetree.sines[1].oscselect(), "phaseshift": self._hdawg.nodetree.sines[1].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[1].harmonic(), "amp1" : self._hdawg.nodetree.sines[1].amplitudes[0](), "amp2" :self._hdawg.nodetree.sines[1].amplitudes[1]()}, "sin3" : {"osc" : self._hdawg.nodetree.sines[2].oscselect(), "phaseshift": self._hdawg.nodetree.sines[2].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[2].harmonic(), "amp1" : self._hdawg.nodetree.sines[2].amplitudes[0](), "amp2" :self._hdawg.nodetree.sines[2].amplitudes[1]()}, "sin4" : {"osc" : self._hdawg.nodetree.sines[3].oscselect(), "phaseshift": self._hdawg.nodetree.sines[3].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[3].harmonic(), "amp1" : self._hdawg.nodetree.sines[3].amplitudes[0]() , "amp2" :self._hdawg.nodetree.sines[3].amplitudes[1]()}, "sin5" : {"osc" : self._hdawg.nodetree.sines[4].oscselect(), "phaseshift": self._hdawg.nodetree.sines[4].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[4].harmonic(), "amp1" : self._hdawg.nodetree.sines[4].amplitudes[0](), "amp2" :self._hdawg.nodetree.sines[4].amplitudes[1]()}, "sin6" : {"osc" : self._hdawg.nodetree.sines[5].oscselect(), "phaseshift": self._hdawg.nodetree.sines[5].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[5].harmonic(), "amp1" : self._hdawg.nodetree.sines[5].amplitudes[0]() , "amp2" :self._hdawg.nodetree.sines[5].amplitudes[1]()}, "sin7" : {"osc" : self._hdawg.nodetree.sines[6].oscselect(), "phaseshift": self._hdawg.nodetree.sines[6].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[6].harmonic(), "amp1" : self._hdawg.nodetree.sines[6].amplitudes[0]() , "amp2" :self._hdawg.nodetree.sines[6].amplitudes[1]()}, "sin8" : {"osc" : self._hdawg.nodetree.sines[7].oscselect(), "phaseshift": self._hdawg.nodetree.sines[7].phaseshift(), "harmonic" : self._hdawg.nodetree.sines[0].harmonic(), "amp1" : self._hdawg.nodetree.sines[7].amplitudes[0]() , "amp2" :self._hdawg.nodetree.sines[7].amplitudes[1]()}}
        self._awgs = {"awg1" : self._hdawg.nodetree.awgs[0], "awg2" : self._hdawg.nodetree.awgs[1], "awg3" : self._hdawg.nodetree.awgs[2], "awg4" : self._hdawg.nodetree.awgs[3]}
        self._output_amps = {"awg1" : {"out1" : self._awgs["awg1"].outputs[0].amplitude(), "out2" : self._awgs["awg1"].outputs[1].amplitude()}, "awg2" : {"out1" : self._awgs["awg2"].outputs[0].amplitude(), "out2" : self._awgs["awg2"].outputs[1].amplitude()}, "awg3" : {"out1" : self._awgs["awg3"].outputs[0].amplitude(), "out2" : self._awgs["awg3"].outputs[1].amplitude()}, "awg4" : {"out1" : self._awgs["awg4"].outputs[0].amplitude(), "out2" : self._awgs["awg4"].outputs[1].amplitude()}}
        self._sequencers = {"awg1" : {"positions" : self._awgs["awg1"].sequencer.pc, "status" :self._awgs["awg1"].sequencer.status , "memoryusage" : self._awgs["awg1"].sequencer.memoryusage, "triggered" : self._awgs["awg1"].sequencer.triggered, "program" :  self._awgs["awg1"].sequencer.program}, "awg2" : {"positions" : self._awgs["awg2"].sequencer.pc, "status" :self._awgs["awg2"].sequencer.status , "memoryusage" : self._awgs["awg2"].sequencer.memoryusage, "triggered" : self._awgs["awg2"].sequencer.triggered, "program" :  self._awgs["awg2"].sequencer.program}, "awg3" : {"positions" : self._awgs["awg3"].sequencer.pc, "status" :self._awgs["awg3"].sequencer.status , "memoryusage" : self._awgs["awg3"].sequencer.memoryusage, "triggered" : self._awgs["awg3"].sequencer.triggered, "program" :  self._awgs["awg3"].sequencer.program}, "awg4" : {"positions" : self._awgs["awg4"].sequencer.pc, "status" :self._awgs["awg4"].sequencer.status , "memoryusage" : self._awgs["awg4"].sequencer.memoryusage, "triggered" : self._awgs["awg4"].sequencer.triggered, "program" :  self._awgs["awg4"].sequencer.program}}
        self._ref_clock_status = self._hdawg.ref_clock_status()
        self._output_status = {"awg1" : {"out1" : self._hdawg.awgs[0].output1(), "out2" : self._hdawg.awgs[0].output1()}, "awg2" : {"out1" : self._hdawg.awgs[1].output1(), "out2" : self._hdawg.awgs[1].output1()},  "awg3" : {"out1" : self._hdawg.awgs[2].output1(), "out2" : self._hdawg.awgs[2].output1()}, "awg4" : {"out1" : self._hdawg.awgs[3].output1(), "out2" : self._hdawg.awgs[3].output1()}}
        self._modulation_freqs = {"awg1": self._hdawg.awgs[0].modulation_freq(), "awg2": self._hdawg.awgs[1].modulation_freq(), "awg3": self._hdawg.awgs[2].modulation_freq(), "awg4": self._hdawg.awgs[3].modulation_freq()}
        self._modulation_phase_shifts = {"awg1": self._hdawg.awgs[0].modulation_phase_shift(), "awg2": self._hdawg.awgs[1].modulation_phase_shift(), "awg3": self._hdawg.awgs[2].modulation_phase_shift(), "awg4": self._hdawg.awgs[3].modulation_phase_shift()}
        self._gains = {"awg1": {"gain1" : self._hdawg.awgs[0].gain1() , "gain2" : self._hdawg.awgs[0].gain2()}, "awg2": {"gain1" : self._hdawg.awgs[1].gain1() , "gain2" : self._hdawg.awgs[1].gain2()}, "awg3": {"gain1" : self._hdawg.awgs[2].gain1() , "gain2" : self._hdawg.awgs[2].gain2()}, "awg4": {"gain1" : self._hdawg.awgs[3].gain1() , "gain2" : self._hdawg.awgs[3].gain2()}}
        self._single = {"awg1": self._hdawg.awgs[0].single(), "awg2": self._hdawg.awgs[1].single(), "awg3": self._hdawg.awgs[2].single(), "awg4": self._hdawg.awgs[3].single()}
        self._waveforms = {"awg1": self._hdawg.awgs[0].waveforms, "awg2": self._hdawg.awgs[1].waveforms, "awg3": self._hdawg.awgs[2].waveforms, "awg4": self._hdawg.awgs[3].waveforms}
        self._run_status = {"awg1": self._hdawg.awgs[0].is_running, "awg2": self._hdawg.awgs[1].is_running, "awg3": self._hdawg.awgs[2].is_running, "awg4": self._hdawg.awgs[3].is_running}

    def get_connection_settings(self, param):
      """
        Getter function for HDAWG connection settings.

        Parameters
        ----------
        param : str
            Connection paramater. Must be "hdawg_name" (str), "hdawg_id" (str), "server_host" (str), "server_port" (int), "api_level" (int), "interface" (str), "connection_status" (bool).

        Returns
        -------
        Corresponding paramaeter value in connection setttings dictionary.
      """

      params = {"hdawg_name", "hdawg_id",  "server_host", "server_port",  "api_level", "interface",  "connection_status"}

      try:
         if type(param) is not str:
            raise TypeError("'param' should be a string.")
      except TypeError:
         raise
      try:
         if param not in params:
            raise ValueError("'param' must be a connection setting parameters.")
      except ValueError:
         raise

      return self._connection_settings[param]

    def get_osc_freq(self, osc_num):
      """
        Getter function for oscillator frequency.

        Parameters
        ----------
        osc_num : int
            Oscillator number between 1-16.


        Returns
        -------
        Oscillator frequency in Hz (double).
      """
      try:
         if type(osc_num) is not int:
            raise TypeError("'osc_num' should be an integer.")
      except TypeError:
         raise
      try:
         if osc_num < 1 or osc_num > 16:
            raise ValueError("'osc_num' should be between 1 and 16.")
      except ValueError:
         raise

      return self._oscillator_freq["osc"+str(osc_num)]

    def set_osc_freq(self, osc_num, freq):
      """
        Setter function for oscillator frequency.

        Parameters
        ----------
        osc_num : int
            Oscillator number between 1-16.
        freq : double
            Oscillator frequency in Hz.

        Returns
        -------
        None.
      """
      try:
         if type(osc_num) is not int:
            raise TypeError("'osc_num' should be an integer.")
      except TypeError:
         raise
      try:
         if osc_num < 1 or osc_num > 16:
            raise ValueError("'osc_num' should be between 1 and 16.")
      except ValueError:
         raise
      try:
         if type(freq) is not float:
            raise TypeError("'freq' should be a double.")
      except TypeError:
         raise

      self._oscillator_freq["osc"+str(osc_num)] = freq
      self._hdawg.nodetree.oscs[osc_num-1] = freq
      print("Oscillator frequency (Hz) set to : ",freq)

    def get_sine(self, sin_num):
      """
        Getter function for sines.

        Parameters
        ----------
        sin_num : int
            Sine index number between 1-8.

        Returns
        -------
        Dictionary of paramaeters defining sine wave in AWG (dict).
      """
      try:
         if type(sin_num) is not int:
            raise TypeError("'sin_num' should be an integer.")
      except TypeError:
         raise
      try:
         if sin_num < 1 or sin_num > 8:
            raise ValueError("'sin_num' should be between 1 and 8.")
      except ValueError:
         raise
      return self._sines["sin"+str(sin_num)]

    def set_sine(self, sin_num, osc_num, phase=0.0, harmonic=1, amp1=1.0, amp2=1.0):
       """
        Setter function for sines.

        Parameters
        ----------
        sin_num : int
            Sine index number between 1-8.
        osc_num : int
            Oscillator index number between 1-16.
        phase : double
            Phase shift of sine wave in degrees. Default set to 0.0.
        harmonic : int
            Harmonic of sine waves reference signal (integer factor of frequency). Default set to 1
        amp1 : double
            Amplitude of wave output 1 in Volts. Default set to 1.0.
        amp2 : double
            Amplitude of wave output 1 in Volts. Default set to 1.0.

        Returns
        -------
        None.
       """

       try:
          if type(sin_num) is not int:
             raise TypeError("'sin_num' should be an integer.")
       except TypeError:
          raise
       try:
          if sin_num < 1 or sin_num > 8:
             raise ValueError("'sin_num' should be between 1 and 8.")
       except ValueError:
          raise
       try:
          if type(osc_num) is not int:
             raise TypeError("'osc_num' should be an integer.")
       except TypeError:
          raise
       try:
          if osc_num < 1 or osc_num > 16:
             raise ValueError("'osc_num' should be between 1 and 16.")
       except ValueError:
          raise
       try:
          if type(phase) is not float:
             raise TypeError("'phase' should be a float.")
       except TypeError:
          raise
       try:
          if type(harmonic) is not int:
             raise TypeError("'harmonic' should be an int.")
       except TypeError:
          raise
       try:
          if type(amp1) is not float:
             raise TypeError("'amp1' should be a float.")
       except TypeError:
          raise
       try:
          if type(amp2) is not float:
             raise TypeError("'amp2' should be a float.")
       except TypeError:
          raise

       self._sines["sin"+str(sin_num)] = {"osc" : osc_num, "phaseshift": phase, "harmonic" : harmonic, "amp1" : amp1, "amp2" : amp2}
       self._hdawg.nodetree.sines[sin_num-1].oscselect(osc_num)
       self._hdawg.nodetree.sines[sin_num-1].phaseshift(phase)
       self._hdawg.nodetree.sines[sin_num-1].harmonic(harmonic)
       self._hdawg.nodetree.sines[sin_num-1].amplitudes[0](amp1)
       self._hdawg.nodetree.sines[sin_num-1].amplitudes[1](amp2)
       print("Sine wave set to: ", self._sines["sin"+str(sin_num)])

    def get_awg(self, awg_num):
       """
        Getter function for AWG core.

        Parameters
        ----------
        AWG core index : int
            Sine index number between 1-4.

        Returns
        -------
        AWG core (<zhinst.toolkit.control.node_tree.Node> object).
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise
       return self._awgs["awg"+str(awg_num)]

    def get_out_amp(self, awg_num):
       """
        Getter function for AWG core amplitudes.

        Parameters
        ----------
        awg_num: int
            Sine index number between 1-4.

        Returns
        -------
        List of AWG amplitudes in Volts: [amp1, amp1]. (list)
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise
       return [self._output_amps["awg"+str(awg_num)]["out1"], self._output_amps["awg"+str(awg_num)]["out2"]]

    def set_out_amp(self, awg_num, channel_num, amp):
       """
        Setter function for AWG core amplitudes.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.
        channel_num: int
            Channel index number between 1-2.
        amp: double
            Amplitude for corresponding channel.

        Returns
        -------
        None.
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise
       try:
          if type(channel_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if channel_num !=1 or channel_num != 2 :
             raise ValueError("'channel_num' should be 1 or 2.")
       except ValueError:
          raise
       try:
          if type(amp) is not float:
             raise TypeError("'amp' should be a float.")
       except TypeError:
          raise

       if channel_num == 1:
          self._output_amps["awg"+str(awg_num)]["out1"] = amp
          self._awgs["awg"+str(awg_num)].outputs[0].amplitude(amp)
       else:
          self._output_amps["awg"+str(awg_num)]["out2"] = amp
          self._awgs["awg"+str(awg_num)].outputs[1].amplitude(amp)

    # def get_seq(self):
    #    """
    #     Getter function for AWG sequence.
    #
    #     Parameters
    #     ----------
    #     awg_num: int
    #         Sine index number between 1-4.
    #
    #     Returns
    #     -------
    #     List of AWG amplitudes in Volts: [amp1, amp1]. (list)
    #    """
    #
    #
    # def set_seq(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_seq_param(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    def get_clock_status(self):
       """
        Gets status of internal clock.

        Parameters
        ----------
        None.

        Returns
        -------
        Status of internal clock. (str)
       """
       return self._hdawg.ref_clock_status()

    # def get_out_status(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_out_status(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def get_mod_freq(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_mod_freq(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def get_mod_phase(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_mod_phase(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def get_gain(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_gain(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    def get_waveform(self, awg_num):
       """
        Getter function for waveforms for specified AWG core in 'simple' status.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.

        Returns
        -------
        List of waveforms for AWG core (list of numpy arrays). (list)
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise

       return self._waveforms["awg"+str(awg_num)]

    def get_run_status(self, awg_num):
       """
        Getter function for run status of selected AWG core.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.

        Returns
        -------
        Run status for selected AWG core [bool].
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise

       self._run_status["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].is_running
       return self._run_status["awg"+str(awg_num)]


    def compile_core(self, awg_num):
       """
        Compiles sequence currently on AWG core.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.

        Returns
        -------
        None.
       """
       try:
          if type(awg_num) is not int:
             raise TypeError("'awg_num' should be an integer.")
       except TypeError:
          raise
       try:
          if awg_num < 1 or awg_num > 4:
             raise ValueError("'awg_num' should be between 1 and 4.")
       except ValueError:
          raise
       self._hdawg.awgs[awg_num-1].compile()
       self._run_status["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].is_running 
    #
    # def compile_core_upload_seq(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def set_output(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def queue_waveform(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def replace_waveform(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def empty_queue(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def run_core(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def stop_core(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def upload_waveform(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
    #
    # def wait_core(self):
    #  # """
    #  #  Initializes connection with HDAWG instrument via server.
    #  #
    #  #    First...
    #  #
    #  #    Parameters
    #  #    ----------
    #  #    additional : str, optional
    #  #        More info to be displayed (default is None)
    #  #
    #  #    Returns
    #  #    -------
    #  #    None
    #  #  """
    #  test = 1
