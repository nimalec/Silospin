#!/usr/bin/env python
import zhinst
import zhinst.utils
import json
from zhinst.toolkit import Session
import numpy as np

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

    def __init__(self, dev_id, server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE"):
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
        self._connection_settings = {"hdawg_id" : dev_id, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level, "interface" : interface, "connection_status" : False}
        session = Session(server_host)
        self._session = session
        self._hdawg = self._session.connect_device(dev_id)
        self._daq = self._session.daq_server

        if self._session.server_port:
            self._connection_settings["connection_status"] = True
        else:
            self._connection_settings["connection_status"] = False

        self._oscillator_freq = {"osc1" : self._hdawg.oscs[0].freq(), "osc2" :self._hdawg.oscs[1].freq(), "osc3" :self._hdawg.oscs[2].freq(), "osc4" :self._hdawg.oscs[3].freq(), "osc5" :self._hdawg.oscs[4].freq(), "osc6" :self._hdawg.oscs[5].freq(), "osc7" :self._hdawg.oscs[6].freq(), "osc8" :self._hdawg.oscs[7].freq(), "osc9" :self._hdawg.oscs[8].freq(), "osc10" :self._hdawg.oscs[9].freq(), "osc11" :self._hdawg.oscs[10].freq(), "osc12" :self._hdawg.oscs[11].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc14" :self._hdawg.oscs[13].freq(), "osc15" :self._hdawg.oscs[14].freq(), "osc16" :self._hdawg.oscs[15].freq()}

        ##Add modulation here ... (change modulation frequency )
        self._sines = {"sin1" : {"osc" : self._hdawg.sines[0].oscselect(), "phaseshift": self._hdawg.sines[0].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[0].amplitudes[0]() , "amp2" :self._hdawg.sines[0].amplitudes[1]()}
        , "sin2" : {"osc" : self._hdawg.sines[1].oscselect(), "phaseshift": self._hdawg.sines[1].phaseshift(), "harmonic" : self._hdawg.sines[1].harmonic(), "amp1" : self._hdawg.sines[1].amplitudes[0](), "amp2" :self._hdawg.sines[1].amplitudes[1]()},
        "sin3" : {"osc" : self._hdawg.sines[2].oscselect(), "phaseshift": self._hdawg.sines[2].phaseshift(), "harmonic" : self._hdawg.sines[2].harmonic(), "amp1" : self._hdawg.sines[2].amplitudes[0](), "amp2" :self._hdawg.sines[2].amplitudes[1]()},
         "sin4" : {"osc" : self._hdawg.sines[3].oscselect(), "phaseshift": self._hdawg.sines[3].phaseshift(), "harmonic" : self._hdawg.sines[3].harmonic(), "amp1" : self._hdawg.sines[3].amplitudes[0]() , "amp2" :self._hdawg.sines[3].amplitudes[1]()},
         "sin5" : {"osc" : self._hdawg.sines[4].oscselect(), "phaseshift": self._hdawg.sines[4].phaseshift(), "harmonic" : self._hdawg.sines[4].harmonic(), "amp1" : self._hdawg.sines[4].amplitudes[0](), "amp2" :self._hdawg.sines[4].amplitudes[1]()},
         "sin6" : {"osc" : self._hdawg.sines[5].oscselect(), "phaseshift": self._hdawg.sines[5].phaseshift(), "harmonic" : self._hdawg.sines[5].harmonic(), "amp1" : self._hdawg.sines[5].amplitudes[0]() , "amp2" :self._hdawg.sines[5].amplitudes[1]()},
         "sin7" : {"osc" : self._hdawg.sines[6].oscselect(), "phaseshift": self._hdawg.sines[6].phaseshift(), "harmonic" : self._hdawg.sines[6].harmonic(), "amp1" : self._hdawg.sines[6].amplitudes[0]() , "amp2" :self._hdawg.sines[6].amplitudes[1]()},
          "sin8" : {"osc" : self._hdawg.sines[7].oscselect(), "phaseshift": self._hdawg.sines[7].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[7].amplitudes[0]() , "amp2" :self._hdawg.sines[7].amplitudes[1]()}}

        self._awgs = {"awg1" : self._hdawg.awgs[0], "awg2" : self._hdawg.awgs[1], "awg3" : self._hdawg.awgs[2], "awg4" : self._hdawg.awgs[3]}

        self._command_tables =  {"awg1": self._hdawg.awgs[0].commandtable(), "awg2": self._hdawg.awgs[1].commandtable(), "awg3": self._hdawg.awgs[2].commandtable(), "awg4": self._hdawg.awgs[3].commandtable()}
        self._sequences =  {"awg1": self._hdawg.awgs[0].sequencer(), "awg2": self._hdawg.awgs[0].sequencer(), "awg3": self._hdawg.awgs[0].sequencer(), "awg4": self._hdawg.awgs[0].sequencer()}
        self._waveforms =  {"awg1": self._hdawg.awgs[0].waveform(), "awg2": self._hdawg.awgs[0].waveform(), "awg3": self._hdawg.awgs[0].waveform(), "awg4": self._hdawg.awgs[0].waveform()}

        ##Obtain run status for each sequencer
        self._run_status = {}
        for idx in range(4):
            status = self._daq.getInt(f"/{dev_id}/awgs/{idx}/sequencer/status")
            if status == 0:
                self._run_status["awg"+str(idx+1)] = False
            else:
                self._run_status["awg"+str(idx+1)] = True

    def get_all_awg_parameters(self):
        dev_id = self._connection_settings["hdawg_id"]
        self._oscillator_freq = {"osc1" : self._hdawg.oscs[0].freq(), "osc2" :self._hdawg.oscs[1].freq(), "osc3" :self._hdawg.oscs[2].freq(), "osc4" :self._hdawg.oscs[3].freq(), "osc5" :self._hdawg.oscs[4].freq(), "osc6" :self._hdawg.oscs[5].freq(), "osc7" :self._hdawg.oscs[6].freq(), "osc8" :self._hdawg.oscs[7].freq(), "osc9" :self._hdawg.oscs[8].freq(), "osc10" :self._hdawg.oscs[9].freq(), "osc11" :self._hdawg.oscs[10].freq(), "osc12" :self._hdawg.oscs[11].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc14" :self._hdawg.oscs[13].freq(), "osc15" :self._hdawg.oscs[14].freq(), "osc16" :self._hdawg.oscs[15].freq()}
        self._sines = {"sin1" : {"osc" : self._hdawg.sines[0].oscselect(), "phaseshift": self._hdawg.sines[0].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[0].amplitudes[0]() , "amp2" :self._hdawg.sines[0].amplitudes[1]()}, "sin2" : {"osc" : self._hdawg.sines[1].oscselect(), "phaseshift": self._hdawg.sines[1].phaseshift(), "harmonic" : self._hdawg.sines[1].harmonic(), "amp1" : self._hdawg.sines[1].amplitudes[0](), "amp2" :self._hdawg.sines[1].amplitudes[1]()}, "sin3" : {"osc" : self._hdawg.sines[2].oscselect(), "phaseshift": self._hdawg.sines[2].phaseshift(), "harmonic" : self._hdawg.sines[2].harmonic(), "amp1" : self._hdawg.sines[2].amplitudes[0](), "amp2" :self._hdawg.sines[2].amplitudes[1]()}, "sin4" : {"osc" : self._hdawg.sines[3].oscselect(), "phaseshift": self._hdawg.sines[3].phaseshift(), "harmonic" : self._hdawg.sines[3].harmonic(), "amp1" : self._hdawg.sines[3].amplitudes[0]() , "amp2" :self._hdawg.sines[3].amplitudes[1]()}, "sin5" : {"osc" : self._hdawg.sines[4].oscselect(), "phaseshift": self._hdawg.sines[4].phaseshift(), "harmonic" : self._hdawg.sines[4].harmonic(), "amp1" : self._hdawg.sines[4].amplitudes[0](), "amp2" :self._hdawg.sines[4].amplitudes[1]()}, "sin6" : {"osc" : self._hdawg.sines[5].oscselect(), "phaseshift": self._hdawg.sines[5].phaseshift(), "harmonic" : self._hdawg.sines[5].harmonic(), "amp1" : self._hdawg.sines[5].amplitudes[0]() , "amp2" :self._hdawg.sines[5].amplitudes[1]()}, "sin7" : {"osc" : self._hdawg.sines[6].oscselect(), "phaseshift": self._hdawg.sines[6].phaseshift(), "harmonic" : self._hdawg.sines[6].harmonic(), "amp1" : self._hdawg.sines[6].amplitudes[0]() , "amp2" :self._hdawg.sines[6].amplitudes[1]()}, "sin8" : {"osc" : self._hdawg.sines[7].oscselect(), "phaseshift": self._hdawg.sines[7].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[7].amplitudes[0]() , "amp2" :self._hdawg.sines[7].amplitudes[1]()}}
        self._command_tables =  {"awg1": self._hdawg.awgs[0].commandtable(), "awg2": self._hdawg.awgs[1].commandtable(), "awg3": self._hdawg.awgs[2].commandtable(), "awg4": self._hdawg.awgs[3].commandtable()}
        self._sequences =  {"awg1": self._hdawg.awgs[0].sequencer(), "awg2": self._hdawg.awgs[0].sequencer(), "awg3": self._hdawg.awgs[0].sequencer(), "awg4": self._hdawg.awgs[0].sequencer()}
        self._waveforms =  {"awg1": self._hdawg.awgs[0].waveform(), "awg2": self._hdawg.awgs[0].waveform(), "awg3": self._hdawg.awgs[0].waveform(), "awg4": self._hdawg.awgs[0].waveform()}
        for idx in range(4):
            status = self._daq.getInt(f"/{dev_id}/awgs/{idx}/sequencer/status")
            if status == 0:
                self._run_status["awg"+str(idx+1)] = False
            else:
                self._run_status["awg"+str(idx+1)] = True

        return {"connection": self._connection_settings, "oscillators": self._oscillator_freq,
        "sines": self._sines, "command_tables": self._command_tables , "sequences": self._sequences,
        "waveforms": self._waveforms , "run_status": self._run_status}

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

      # try:
      #    if type(param) is not str:
      #       raise TypeError("'param' should be a string.")
      # except TypeError:
      #    raise
      # try:
      #    if param not in params:
      #       raise ValueError("'param' must be a connection setting parameters.")
      # except ValueError:
      #    raise

      if param == "connection_status":
          if self._session.server_port:
              self._connection_settings[param] = True
          else:
               self._connection_settings[param] = False
      else:
          pass

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
      # try:
      #    if type(osc_num) is not int:
      #       raise TypeError("'osc_num' should be an integer.")
      # except TypeError:
      #    raise
      # try:
      #    if osc_num < 1 or osc_num > 16:
      #       raise ValueError("'osc_num' should be between 1 and 16.")
      # except ValueError:
      #    raise
      self._oscillator_freq["osc"+str(osc_num)] = self._hdawg.oscs[osc_num-1].freq()
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
      # try:
      #    if type(osc_num) is not int:
      #       raise TypeError("'osc_num' should be an integer.")
      # except TypeError:
      #    raise
      # try:
      #    if osc_num < 1 or osc_num > 16:
      #       raise ValueError("'osc_num' should be between 1 and 16.")
      # except ValueError:
      #    raise

      self._oscillator_freq["osc"+str(osc_num)] = freq
      self._hdawg.oscs[osc_num-1].freq(freq)

    def get_phase(self, sin_num):
      """
        Getter function for phase.

        Parameters
        ----------
        sin_num : int
            Oscillator number between 1-8.


        Returns
        -------
        Oscillator phase in degrees (double).
      """
      # try:
      #    if type(sin_num) is not int:
      #       raise TypeError("'sin_num' should be an integer.")
      # except TypeError:
      #    raise
      # try:
      #    if sin_num < 1 or sin_num > 8:
      #       raise ValueError("'sin_num' should be between 1 and 8.")
      # except ValueError:
      #    raise

      return self._hdawg.sines[sin_num-1].phaseshift()

    def set_phase(self, sin_num, phase):
      """
        Setter function for phase.

        Parameters
        ----------
        sin_num : int
            Oscillator number between 1-8.
        phase : float
            Phase assigned to sine generator.

        Returns
        -------
        None.
      """

      cores = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 7: 4, 8: 4, 8: 4}
      if self.get_updated_run_status(cores[sin_num]) == True:
         print("Core currently running, cannot change phase.")
      else:
          self._hdawg.sines[sin_num-1].phaseshift(phase)
          self._sines["sin"+str(sin_num)]["phaseshift"] = phase

    def get_modulation_mode(self, sin_num):
        dev_id = self._connection_settings["hdawg_id"]
        cores = {1: [0,0], 2: [1,0], 3: [0,1], 4: [1,1], 5: [0,2], 6: [1,2], 7: [0,3], 8: [1,3]}
        ch_idx = cores[sin_num][0]
        awg_idx = cores[sin_num][1]
        return self._daq.getInt(f"/{dev_id}/awgs/{awg_idx}/outputs/{ch_idx}/modulation/mode")

    def set_modulation_mode(self, sin_num, mode):
        dev_id = self._connection_settings["hdawg_id"]
        core_map = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 7: 4, 8: 4, 8: 4}
        if self.get_updated_run_status(core_map[sin_num]) == True:
           print("Core currently running, cannot change modulation mode.")
        else:
         cores = {1: [0,0], 2: [1,0], 3: [0,1], 4: [1,1], 5: [0,2], 6: [1,2], 7: [0,3], 8: [1,3]}
         ch_idx = cores[sin_num][0]
         awg_idx = cores[sin_num][1]
         self._daq.setInt(f"/{dev_id}/awgs/{awg_idx}/outputs/{ch_idx}/modulation/mode", mode)

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
      # try:
      #    if type(sin_num) is not int:
      #       raise TypeError("'sin_num' should be an integer.")
      # except TypeError:
      #    raise
      # try:
      #    if sin_num < 1 or sin_num > 8:
      #       raise ValueError("'sin_num' should be between 1 and 8.")
      # except ValueError:
      #    raise
      sine = {"osc" : self._hdawg.sines[sin_num-1].oscselect(), "phaseshift": self._hdawg.sines[sin_num-1].phaseshift(), "harmonic" : self._hdawg.sines[sin_num-1].harmonic(), "amp1" : self._hdawg.sines[sin_num-1].amplitudes[0]() , "amp2" :self._hdawg.sines[sin_num-1].amplitudes[1]()}
      return sine



    def assign_osc(self, sin_num, osc_num):
       # try:
       #    if type(sin_num) is not int:
       #       raise TypeError("'sin_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if sin_num < 1 or sin_num > 8:
       #       raise ValueError("'sin_num' should be between 1 and 8.")
       # except ValueError:
       #    raise
       # try:
       #    if type(osc_num) is not int:
       #       raise TypeError("'osc_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if osc_num < 1 or osc_num > 16:
       #       raise ValueError("'osc_num' should be between 1 and 16.")
       # except ValueError:
       #    raise

       cores = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 7: 4, 8: 4, 8: 4}
       if self.get_updated_run_status(cores[sin_num]) == True:
          print("Core currently running, cannot change phase.")
       else:
          self._sines["sin"+str(sin_num)]["osc_num"] = osc_num
          self._hdawg.sines[sin_num-1].oscselect(osc_num-1)


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

       # try:
       #    if sin_num < 1 or sin_num > 8:
       #       raise ValueError("'sin_num' should be between 1 and 8.")
       # except ValueError:
       #    raise
       # try:
       #    if type(osc_num) is not int:
       #       raise TypeError("'osc_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if osc_num < 1 or osc_num > 16:
       #       raise ValueError("'osc_num' should be between 1 and 16.")
       # except ValueError:
       #    raise
       # try:
       #    if type(phase) is not float:
       #       raise TypeError("'phase' should be a float.")
       # except TypeError:
       #    raise
       # try:
       #    if type(harmonic) is not int:
       #       raise TypeError("'harmonic' should be an int.")
       # except TypeError:
       #    raise



       cores = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 7: 4, 8: 4, 8: 4}
       if self.get_updated_run_status(cores[sin_num]) == True:
          print("Core currently running, cannot change phase.")
       else:
          self._sines["sin"+str(sin_num)]["osc_num"] = osc_num
          self._hdawg.sines[sin_num-1].oscselect(osc_num-1)
          self._sines["sin"+str(sin_num)] = {"osc" : osc_num, "phaseshift": phase, "harmonic" : harmonic, "amp1" : amp1, "amp2" : amp2}
          self._hdawg.sines[sin_num-1].oscselect(osc_num-1)
          self._hdawg.sines[sin_num-1].phaseshift(phase)
          self._hdawg.sines[sin_num-1].harmonic(harmonic)
          self._hdawg.sines[sin_num-1].amplitudes[0](amp1)
          self._hdawg.sines[sin_num-1].amplitudes[1](amp2)

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
       # """
       # try:
       #    if type(awg_num) is not int:
       #       raise TypeError("'awg_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if awg_num < 1 or awg_num > 4:
       #       raise ValueError("'awg_num' should be between 1 and 4.")
       # except ValueError:
       #    raise
       return self._awgs["awg"+str(awg_num)]

    def get_out_amp(self, sin_num, wave_num):
       """
        Getter function for AWG core amplitudes. .

        Parameters
        ----------
        sin_num: int
            Sine index number between 1-8.

        wave_num: int
            Wave index number between 1-2.

        Returns
        -------
        Returns output amplitude in volts.
       """

       # try:
       #    if type(sin_num) is not int:
       #       raise TypeError("'sin_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if sin_num < 1 or sin_num > 8:
       #       raise ValueError("'sin_num' should be between 1 and 8.")
       # except ValueError:
       #    raise
       #
       # try:
       #    if type(wave_num) is not int:
       #       raise TypeError("'wave_num' should be an integer.")
       # except TypeError:
       #    raise


       self._sines["sin"+str(sin_num)]["amp"+str(wave_num-1)] = self._hdawg.sines[sin_num-1].amplitudes[wave_num-1]()

       return self._sines["sin"+str(sin_num)]["amp"+str(wave_num-1)]

    def set_out_amp(self, sin_num, wave_num, amp):
       """
        Setter function for awg output amplitudes.

        Parameters
        ----------
        sines_num: int
            AWG index number between 1-8.
        wave_num: int
            Channel index number between 1-2.
        amp: double
            Amplitude for corresponding channel.

        Returns
        -------
        None.
       """

       # try:
       #    if type(sin_num) is not int:
       #       raise TypeError("'sin_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if sin_num < 1 or sin_num > 8:
       #       raise ValueError("'sin_num' should be between 1 and 8.")
       # except ValueError:
       #    raise
       # try:
       #    if type(wave_num) is not int:
       #       raise TypeError("'wave_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if type(amp) is not float:
       #       raise TypeError("'amp' should be a float.")
       # except TypeError:
       #    raise
       #
       # try:
       #    if amp > 1.0:
       #       raise ValueError("Output amplitude should not exceed 0.9 volts")
       # except ValueError:
       #    raise

       self._hdawg.sines[sin_num-1].amplitudes[wave_num-1](amp)
       self._sines["sin"+str(sin_num)]["amp"+str(wave_num)] = amp

       cores = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 7: 4, 8: 4, 8: 4}
       if self.get_updated_run_status(cores[sin_num]) == True:
          print("Core currently running, cannot change amplitude.")
       else:
          self._hdawg.sines[sin_num-1].amplitudes[wave_num-1](amp)
          self._sines["sin"+str(sin_num)]["amp"+str(wave_num)] = amp

    def get_sequence(self, awg_idx):
       """
        Getter function for AWG sequence.

        Parameters
        ----------
        None.

        Returns
        -------
        Python sequence program (str).
       """
       self._sequences["awg"+str(awg_idx+1)] = self._hdawg.awgs[awg_idx].sequencer(),
       return self._sequences["awg"+str(awg_idx+1)]

    # def load_sequence(self, seq):
    #    """
    #     Getter function for AWG sequence.
    #
    #     Parameters
    #     ----------
    #     Sequence: str
    #
    #     Returns
    #     -------
    #     None.
    #    """
    #
    #    self._hdawg.awgs[0].load_sequencer_program(seq)
    #

    # def get_clock_status(self):
    #    """
    #     Gets status of internal clock.
    #
    #     Parameters
    #     ----------
    #     None.
    #
    #     Returns
    #     -------
    #     Status of internal clock. (str)
    #    """
    #
    #    self._ref_clock_status = self._hdawg.clockbase()
    #    return self._ref_clock_status

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
       # try:
       #    if type(awg_num) is not int:
       #       raise TypeError("'awg_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if awg_num < 1 or awg_num > 4:
       #       raise ValueError("'awg_num' should be between 1 and 4.")
       # except ValueError:
       #    raise

       #self._waveforms["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].waveform()
       return self._hdawg.awgs[awg_num-1].waveform()

    def get_updated_run_status(self, awg_num):
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
       dev_id = self._connection_settings["hdawg_id"]
       for idx in range(4):
           status = self._daq.getInt(f"/{dev_id}/awgs/{idx}/sequencer/status")
           if status == 0:
               self._run_status["awg"+str(idx+1)] = False
           else:
               self._run_status["awg"+str(idx+1)] = True

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
       # try:
       #    if type(awg_num) is not int:
       #       raise TypeError("'awg_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if awg_num < 1 or awg_num > 4:
       #       raise ValueError("'awg_num' should be between 1 and 4.")
       # except ValueError:
       #    raise
       self._hdawg.awgs[awg_num-1].single(True)

    def load_sequence(self, program, awg_idx=0):
        self._awgs["awg"+str(awg_idx+1)].load_sequencer_program(program)
        self._sequences["awg"+str(awg_idx+1)] = program


    def compile_run_core(self, awg_num):
       """
        Resets queue for current AWG core.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.

        Returns
        -------
        None.
       """
       # try:
       #    if type(awg_num) is not int:
       #       raise TypeError("'awg_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if awg_num < 1 or awg_num > 4:
       #       raise ValueError("'awg_num' should be between 1 and 4.")
       # except ValueError:
       #    raise
       # #self._hdawg.awgs[awg_num-1].run()
       self._hdawg.awgs[awg_num-1].single(True)
       self._hdawg.awgs[awg_num-1].enable(True)
       #self._run_status["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].is_running


    def stop_core(self, awg_num):
       """
        Stops running for current AWG core.

        Parameters
        ----------
        awg_num: int
            AWG index number between 1-4.

        Returns
        -------
        None.
       """
       # try:
       #    if type(awg_num) is not int:
       #       raise TypeError("'awg_num' should be an integer.")
       # except TypeError:
       #    raise
       # try:
       #    if awg_num < 1 or awg_num > 4:
       #       raise ValueError("'awg_num' should be between 1 and 4.")
       # except ValueError:
       #    raise
       # self._hdawg.awgs[awg_num-1].stop()
       self._hdawg.awgs[awg_num-1].enable(False)
      # self._run_status["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].is_running

    def set_command_table(self, ct, awg_index):
        dev = self._connection_settings["hdawg_id"]
        self._daq.setVector(f"/{dev}/awgs/{awg_index}/commandtable/data", json.dumps(ct))
        self._command_tables["awg"+str(awg_index+1)] = ct
