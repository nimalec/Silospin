"""Driver module used to connect and control Zurich HDAWG arbitrary waveform generators.

For initial device connection, run as
>> from silospin.drivers.zi_hdawg_driver import HdawgDriver
>> dev_id = "dev8446"
>> awg = HdawgDriver(dev_id)

Version from November 2022.
"""
import zhinst
import zhinst.utils
import json
from zhinst.toolkit import Session
from silospin.quantum_compiler.quantum_compiler_helpers import channel_mapper
import numpy as np

class HdawgDriver:
    """
    Driver class for Zurich HDAWG (Zurich arbitrary waveform generator) instrument. Configured for 4 AWG cores.

    Attributes
    - - - - - - -
    _connection_settings : 'dict'
        Dictionary of connection settings. Keys/values: "hdawg_id" (str), "server_host" (str), "server_port" (int),  "api_level" (int), "interface" (str), "connection_status" (bool).

    _session : zhinst.toolkit.session.Session
        Instance of Zurich session for established connection.

    _hdawg : zhinst.toolkit.driver.devices.hdawg.HDAWG
        Instance of Zurich HDAWG driver.

    _daq :  zhinst.core.ziDAQServer
        Instance of Zurich driver DAQ module.

    _oscillator_freq : dict
        Dictionary of 16 HDAWG oscillator frequencies. Keys: "osc1"..."osc16" (str). Values: corresponding oscillator frequencies in Hz (float).

    _sines : dict
        Dictionary of 8 HDAWG sine generator properties. Outer keys correspond to the sine wave ("sine1"..."sine8"), with dictionary values as separate dictionaries.
        Inner dictionary for each sine generator describes propertie of sine generator. Keys/Values: "osc" (int) [oscillator index from 0-15], "phaseshift" (float) [phase shift for oscillator in degrees], "harmonic" (int) [harmonic of sine wave], "amp1" (float) [amplitude on output 1], "amp2" (float) [amplitude on output 2].

    _awgs : dict
        Dictionary for 4 AWG cores. Keys correspond to each AWG ("awg1"..."awg4"), values are Zurich AWG core objects.

    _command_tables : dict
       Dictionary of command tables uploaded to each AWG core, pulled dicectly from the instrument.

    _sequences : dict
        Dictionary of sequencer code uploaded to each AWG core (keys correspond to each core "awg1"..."awg4").

    _run_status : dict
        Dictionary of run status for each core ("awg1"..."awg4"), True if running and False if not.

    _channel_mapping : dict
        Channel mapping for AWG. Takes in RF core and DC channel groupings, returns mapping from AWG core indices to gate indices and channels.
    """

    def __init__(self, dev_id, server_host = "localhost", server_port = 8004, api_level = 6, interface = "1GbE", rf_cores=[1,2,3], plunger_channels = {"p12": 7, "p21": 8}):
        """
         Constructor for HDAWG Driver.

           Parameters
           ----------
           dev_id : str
              Device ID for AWG (e.g 'dev8446').
           server_host : str
              Server host name (default = "localhost").
           server_port : int
              Port number for the host server (default = 8004).
           api_level : int
              API level of instrument (default = 6, for HDAWG).
           interface : str
              Interface used to connect to server (default = "1GbE" for ethernet connection).
           rf_cores : list
               List of HDAWG cores dedicated for microwave or RF control, with core indices indexing from 1. Values must range between 1-4 (default set to [1,2,3]).
           plunger_channels : dict
               Dictionary specifying the mapping from plunger (DC) gates to their corresponding channels. Keys of dictionary represent gate type (e.g. "p12") and values are corresponding channels ranging from 1-8 (default set to {"p12": 7, "p21": 8}).

           Returns
           -------
           None.
        """
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

        self._sines = {"sin1" : {"osc" : self._hdawg.sines[0].oscselect(), "phaseshift": self._hdawg.sines[0].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[0].amplitudes[0]() , "amp2" :self._hdawg.sines[0].amplitudes[1]()}
        , "sin2" : {"osc" : self._hdawg.sines[1].oscselect(), "phaseshift": self._hdawg.sines[1].phaseshift(), "harmonic" : self._hdawg.sines[1].harmonic(), "amp1" : self._hdawg.sines[1].amplitudes[0](), "amp2" :self._hdawg.sines[1].amplitudes[1]()},
        "sin3" : {"osc" : self._hdawg.sines[2].oscselect(), "phaseshift": self._hdawg.sines[2].phaseshift(), "harmonic" : self._hdawg.sines[2].harmonic(), "amp1" : self._hdawg.sines[2].amplitudes[0](), "amp2" :self._hdawg.sines[2].amplitudes[1]()},
         "sin4" : {"osc" : self._hdawg.sines[3].oscselect(), "phaseshift": self._hdawg.sines[3].phaseshift(), "harmonic" : self._hdawg.sines[3].harmonic(), "amp1" : self._hdawg.sines[3].amplitudes[0]() , "amp2" :self._hdawg.sines[3].amplitudes[1]()},
         "sin5" : {"osc" : self._hdawg.sines[4].oscselect(), "phaseshift": self._hdawg.sines[4].phaseshift(), "harmonic" : self._hdawg.sines[4].harmonic(), "amp1" : self._hdawg.sines[4].amplitudes[0](), "amp2" :self._hdawg.sines[4].amplitudes[1]()},
         "sin6" : {"osc" : self._hdawg.sines[5].oscselect(), "phaseshift": self._hdawg.sines[5].phaseshift(), "harmonic" : self._hdawg.sines[5].harmonic(), "amp1" : self._hdawg.sines[5].amplitudes[0]() , "amp2" :self._hdawg.sines[5].amplitudes[1]()},
         "sin7" : {"osc" : self._hdawg.sines[6].oscselect(), "phaseshift": self._hdawg.sines[6].phaseshift(), "harmonic" : self._hdawg.sines[6].harmonic(), "amp1" : self._hdawg.sines[6].amplitudes[0]() , "amp2" :self._hdawg.sines[6].amplitudes[1]()},
          "sin8" : {"osc" : self._hdawg.sines[7].oscselect(), "phaseshift": self._hdawg.sines[7].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[7].amplitudes[0]() , "amp2" :self._hdawg.sines[7].amplitudes[1]()}}

        self._awgs = {"awg1" : self._hdawg.awgs[0], "awg2" : self._hdawg.awgs[1], "awg3" : self._hdawg.awgs[2], "awg4" : self._hdawg.awgs[3]}
        self._command_tables = {"awg1": self._hdawg.awgs[0].commandtable(), "awg2": self._hdawg.awgs[1].commandtable(), "awg3": self._hdawg.awgs[2].commandtable(), "awg4": self._hdawg.awgs[3].commandtable()}
        self._sequences =  {"awg1": self._hdawg.awgs[0].sequencer(), "awg2": self._hdawg.awgs[0].sequencer(), "awg3": self._hdawg.awgs[0].sequencer(), "awg4": self._hdawg.awgs[0].sequencer()}

        self._run_status = {}
        for idx in range(4):
            status = self._daq.getInt(f"/{dev_id}/awgs/{idx}/sequencer/status")
            if status == 0:
                self._run_status["awg"+str(idx+1)] = False
            else:
                self._run_status["awg"+str(idx+1)] = True

        self._channel_mapping = channel_mapper(rf_cores, plunger_channels)
        for idx in self._channel_mapping:
            ch_1 = self._channel_mapping[idx]['ch']['index'][0]
            ch_2 = self._channel_mapping[idx]['ch']['index'][1]
            if self._channel_mapping[idx]['rf'] == 1:
                self.set_modulation_mode(ch_1, 1)
                self.set_modulation_mode(ch_2, 2)
            elif self._channel_mapping[idx]['rf'] == 0:
                self.set_modulation_mode(ch_1, 0)
                self.set_modulation_mode(ch_2, 0)
            else:
                pass

    def get_all_awg_parameters(self):
        """
        No input parameters. Returns dictionary current state of the instrument.

        Parameters dictionaries are described below:\n
        - "connection", dictionary of connection settings\n
        - "oscillators", dictionary of oscillator frequencies\n
        - "sines", dictionary of sine generator parameters\n
        - "command_tables", dictionary of uploaded command tables\n
        - "sequences", dictionary of uploaded sequencer code \n
        - "run_status", dictionary of run statuses for each core\n
        - "channel_map", channel mapping dictonary

        Parameters
        ----------
        None

        Returns
        -------
        all_awg_parameters : 'dict'
        """
        dev_id = self._connection_settings["hdawg_id"]
        self._oscillator_freq = {"osc1" : self._hdawg.oscs[0].freq(), "osc2" :self._hdawg.oscs[1].freq(), "osc3" :self._hdawg.oscs[2].freq(), "osc4" :self._hdawg.oscs[3].freq(), "osc5" :self._hdawg.oscs[4].freq(), "osc6" :self._hdawg.oscs[5].freq(), "osc7" :self._hdawg.oscs[6].freq(), "osc8" :self._hdawg.oscs[7].freq(), "osc9" :self._hdawg.oscs[8].freq(), "osc10" :self._hdawg.oscs[9].freq(), "osc11" :self._hdawg.oscs[10].freq(), "osc12" :self._hdawg.oscs[11].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc13" :self._hdawg.oscs[12].freq(), "osc14" :self._hdawg.oscs[13].freq(), "osc15" :self._hdawg.oscs[14].freq(), "osc16" :self._hdawg.oscs[15].freq()}
        self._sines = {"sin1" : {"osc" : self._hdawg.sines[0].oscselect(), "phaseshift": self._hdawg.sines[0].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[0].amplitudes[0]() , "amp2" :self._hdawg.sines[0].amplitudes[1]()}, "sin2" : {"osc" : self._hdawg.sines[1].oscselect(), "phaseshift": self._hdawg.sines[1].phaseshift(), "harmonic" : self._hdawg.sines[1].harmonic(), "amp1" : self._hdawg.sines[1].amplitudes[0](), "amp2" :self._hdawg.sines[1].amplitudes[1]()}, "sin3" : {"osc" : self._hdawg.sines[2].oscselect(), "phaseshift": self._hdawg.sines[2].phaseshift(), "harmonic" : self._hdawg.sines[2].harmonic(), "amp1" : self._hdawg.sines[2].amplitudes[0](), "amp2" :self._hdawg.sines[2].amplitudes[1]()}, "sin4" : {"osc" : self._hdawg.sines[3].oscselect(), "phaseshift": self._hdawg.sines[3].phaseshift(), "harmonic" : self._hdawg.sines[3].harmonic(), "amp1" : self._hdawg.sines[3].amplitudes[0]() , "amp2" :self._hdawg.sines[3].amplitudes[1]()}, "sin5" : {"osc" : self._hdawg.sines[4].oscselect(), "phaseshift": self._hdawg.sines[4].phaseshift(), "harmonic" : self._hdawg.sines[4].harmonic(), "amp1" : self._hdawg.sines[4].amplitudes[0](), "amp2" :self._hdawg.sines[4].amplitudes[1]()}, "sin6" : {"osc" : self._hdawg.sines[5].oscselect(), "phaseshift": self._hdawg.sines[5].phaseshift(), "harmonic" : self._hdawg.sines[5].harmonic(), "amp1" : self._hdawg.sines[5].amplitudes[0]() , "amp2" :self._hdawg.sines[5].amplitudes[1]()}, "sin7" : {"osc" : self._hdawg.sines[6].oscselect(), "phaseshift": self._hdawg.sines[6].phaseshift(), "harmonic" : self._hdawg.sines[6].harmonic(), "amp1" : self._hdawg.sines[6].amplitudes[0]() , "amp2" :self._hdawg.sines[6].amplitudes[1]()}, "sin8" : {"osc" : self._hdawg.sines[7].oscselect(), "phaseshift": self._hdawg.sines[7].phaseshift(), "harmonic" : self._hdawg.sines[0].harmonic(), "amp1" : self._hdawg.sines[7].amplitudes[0]() , "amp2" :self._hdawg.sines[7].amplitudes[1]()}}
        self._command_tables =  {"awg1": self._hdawg.awgs[0].commandtable(), "awg2": self._hdawg.awgs[1].commandtable(), "awg3": self._hdawg.awgs[2].commandtable(), "awg4": self._hdawg.awgs[3].commandtable()}
        self._sequences =  {"awg1": self._hdawg.awgs[0].sequencer(), "awg2": self._hdawg.awgs[1].sequencer(), "awg3": self._hdawg.awgs[2].sequencer(), "awg4": self._hdawg.awgs[3].sequencer()}
        for idx in range(4):
            status = self._daq.getInt(f"/{dev_id}/awgs/{idx}/sequencer/status")
            if status == 0:
                self._run_status["awg"+str(idx+1)] = False
            else:
                self._run_status["awg"+str(idx+1)] = True

        return {"connection": self._connection_settings, "oscillators": self._oscillator_freq, "sines": self._sines, "command_tables": self._command_tables , "sequences": self._sequences, "run_status": self._run_status, "channel_map": self._channel_mapping}

    def get_connection_settings(self, param):
      """
      Returns connections setting corresponding to param of the instrument.
      Parameters include: "hdawg_id" ,  "server_host" , "server_port" , "api_level" , "interface" , "connection_status".

      Parameters
      ----------
      param : 'str'
      Parameter must be "hdawg_id" ,  "server_host" , "server_port" , "api_level" , "interface" , or "connection_status".

      Returns
      -------
      connection_setting : 'str' or  'int' or 'bool'.
      Specified connection setting for the HDAWG.
      """
      params = {"hdawg_id" ,  "server_host" , "server_port" , "api_level"  , "interface" ,  "connection_status"}

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

    # def get_waveforms(self):
    #     return {"awg1": self._hdawg.awgs[0].waveform(), "awg2": self._hdawg.awgs[1].waveform(), "awg3": self._hdawg.awgs[2].waveform(), "awg4": self._hdawg.awgs[3].waveform()}

    def get_osc_freq(self, osc_num):
      """
      Returns frequency of oscillator osc_num in Hz. osc_num ranges from 1-16.

      Keep the following oscillator grouping per AWG core in mind:
      -osc 1-4, AWG 1
      -osc 5-9, AWG 2
      -osc 10-13, AWG 3
      -osc 14-16, AWG 4

      Parameters
      ----------
      osc_num : 'int'
      Oscillator index on HDAWG.

      Returns
      -------
      osc_freq : 'float'
      Oscillator frequency in Hz.
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
      Sets oscillator frequency freq in Hz for oscillator osc_num (from 1-16).

      Parameters
      ----------
      osc_num : 'int'
      Oscillator index ranging from 1-16.

      Keep the following oscillator grouping per AWG core in mind:
      -osc 1-4, AWG 1
      -osc 5-9, AWG 2
      -osc 10-13, AWG 3
      -osc 14-16, AWG 4

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
      Gets the phase (in degrees) for sine generator sin_num (from 1-8).

      Parameters
      ----------
      sin_num : 'int'
      Sine generator index ranging from 1-8.

      Returns
      -------
      phaseshift : 'float'
      Phase shift for sine generator in degrees.
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
      Sets oscillator phase (in degrees) for sine generator sin_num (from 1-8).

      Parameters
      ----------
      sin_num : 'int'
      Sine generator index, ranges from 1-8.
      phase : 'float'
      Phase of oscillator in degrees.

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
        """
        Gets modulation mode for sine generator sin_num ranges from 1-8).\n
        Note that modulation mode follows the convention: \n
        - 0, Modulation Off: AWG Output goes directly to Signal Output.\n
        - 1, Sine 11: AWG Outputs 0 and 1 are both multiplied with Sine Generator signal 0.\n
        - 2, Sine 22: AWG Outputs 0 and 1 are both multiplied with Sine Generator signal 1.\n
        - 3, Sine 12: AWG Outputs 0 and 1 are multiplied with Sine Generator signal 0 and 1.\n
        - 4, Sine 21: AWG Outputs 0 and 1 are multiplied with Sine Generator signal 1 and 0.\n
        - 5, Advanced: Output modulates corresponding sines from modulation carriers.\n
        - 6, Mixer Calibration: The AWG outputs are multiplied with the sum or difference of Sine Generators multiplied by gains specified. The resulting output signal is AWG1*(Sine1*Gain1 - Sine2*Gain2) + AWG2*(Sine1*Gain2 + Sine2*Gain1).\n

        Parameters
        ----------
        sin_num : 'int'
        Sine generator ranging from 1-8.

        Returns
        -------
        modulation_mode : 'int'
        Modulation mode of sine generator ranges from 0-6.
        """

        dev_id = self._connection_settings["hdawg_id"]
        cores = {1: [0,0], 2: [1,0], 3: [0,1], 4: [1,1], 5: [0,2], 6: [1,2], 7: [0,3], 8: [1,3]}
        ch_idx = cores[sin_num][0]
        awg_idx = cores[sin_num][1]
        return self._daq.getInt(f"/{dev_id}/awgs/{awg_idx}/outputs/{ch_idx}/modulation/mode")

    def set_modulation_mode(self, sin_num, mode):
        """
        Sets modulation mode for sine generator sin_num ranges from 1-8).\n
        Note that modulation mode follows the convention:\n
        - 0, Modulation Off: AWG Output goes directly to Signal Output.\n
        - 1, Sine 11: AWG Outputs 0 and 1 are both multiplied with Sine Generator signal 0.\n
        - 2, Sine 22: AWG Outputs 0 and 1 are both multiplied with Sine Generator signal 1.\n
        - 3, Sine 12: AWG Outputs 0 and 1 are multiplied with Sine Generator signal 0 and 1.\n
        - 4, Sine 21: AWG Outputs 0 and 1 are multiplied with Sine Generator signal 1 and 0.\n
        - 5, Advanced: Output modulates corresponding sines from modulation carriers.\n
        - 6, Mixer Calibration: The AWG outputs are multiplied with the sum or difference of Sine Generators multiplied by gains specified. The resulting output signal is AWG1x(Sine1xGain1 - Sine2*Gain2) + AWG2x(Sine1xGain2 + Sine2xGain1).\n

        Parameters
        ----------
        sin_num : 'int'
        Sine generator ranging from 1-8.
        mode : 'int'
        Modulation mode varying from 0-6.

        Returns
        -------
        None
        """

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
        Returns a dictionary representing the state of sine generator sin_num (ranges from 1-8). \n
        The dictionary comprises the parameters listed below: \n
        - 'osc', oscillator index (int)\n
        - 'phaseshift', phase offset (degrees) for current sine generator (float)\n
        - 'harmonic', harmonic of the oscillator's output (int)\n
        - 'amp1', amplitude (volts) of sine output 1 (float) \n
        - 'amp2', amplitude (volts) of sine output 2 (float) \n

        Parameters
        ----------
        sin_num : 'int'
        Sine generator ranging from 1-8.

        Returns
        -------
        sine : 'dict'
        Dictionary representing the sine generator's current state.
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
       """
        Assigns an oscillator index (osc_num from 1-16) to a sine generator (sin_num from 1-8).

        Parameters
        ----------
        sin_num : 'int'
        Sine generator ranging from 1-8.
        osc_num : 'int'
        Sine generator ranging from 1-16.

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
        Returns a dictionary representing the state of sine generator sin_num (ranges from 1-8). \n
        The dictionary comprises the parameters listed below: \n
        - 'osc', oscillator index (int)\n
        - 'phaseshift', phase offset (degrees) for current sine generator (float)\n
        - 'harmonic', harmonic of the oscillator's output (int)\n
        - 'amp1', amplitude (volts) of sine output 1 (float) \n
        - 'amp2', amplitude (volts) of sine output 2 (float) \n

        Parameters
        ----------
        sin_num : 'int'
        Sine generator ranging from 1-8.
        osc_num : 'int'
        Oscillator numberranging from 1-16.
        phase : 'float'
        Phase offset in degrees of oscillator (default set to 0.0).
        harmonic : 'int'
        Harmonic of sine generator (default set to 1).
        amp1 : 'float'
        Amplitude of output 1 in volts (default set to 1).
        amp2 : 'float'
        Amplitude of output 2 in volts (default set to 1).
        Returns
        -------
        None
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
        Gets AWG core object for awg core awg_num (ranges from 1-4).

        Parameters
        ----------
        awg_num : 'int'
        AWG core number, ranges from 1-4.

        Returns
        -------
        awg_core :  'zhinst.toolkit.driver.nodes.awg.AWG'
        Zurich AWG core object.
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
       return self._awgs["awg"+str(awg_num)]

    def get_out_amp(self, sin_num, wave_num):
       """
        Gets output amplitude (in volts) for wave output wave_num (ranges from 1-2) of sine generator sin_num (ranges from 1-8).

        Parameters
        ----------
        sin_num : 'int'
        AWG core number, ranges from 1-8.
        wave_num : 'int'
        Wave output channel, ranges from 1-2.

        Returns
        -------
        amp :  'float'
        Amplitude in volts of specified channel output.
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
        Sets output amplitude (in volts) for wave output wave_num (ranges from 1-2) of sine generator sin_num (ranges from 1-8).

        Parameters
        ----------
        sin_num : 'int'
        AWG core number, ranges from 1-8.
        wave_num : 'int'
        Wave output channel, ranges from 1-2.
        amp : 'float'
        Voltage amplitude for specified channel.
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
        Gets the code on the sequencer for a given AWG core index, awg_idx ranging from 0-3.

        Parameters
        ----------
        awg_idx : 'int'
        AWG core index, ranges from 0-3.
        Returns
        -------
        sequence : 'str'
        Sequencer code for specified AWG core.
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

    # def get_waveform(self, awg_num):
    #    # try:
    #    #    if type(awg_num) is not int:
    #    #       raise TypeError("'awg_num' should be an integer.")
    #    # except TypeError:
    #    #    raise
    #    # try:
    #    #    if awg_num < 1 or awg_num > 4:
    #    #       raise ValueError("'awg_num' should be between 1 and 4.")
    #    # except ValueError:
    #    #    raise
    #
    #    #self._waveforms["awg"+str(awg_num)] = self._hdawg.awgs[awg_num-1].waveform()
    #    return self._hdawg.awgs[awg_num-1].waveform()

    def get_updated_run_status(self, awg_num):
       """
        Gets the run status for specified AWG core.

        Parameters
        ----------
        awg_num : 'int'
        AWG core index, ranges from 1-4.
        Returns
        -------
        run_status : 'bool'
        True if currently running, False if not running.
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
        Compiles specified core awg_num.

        Parameters
        ----------
        awg_num : 'int'
        AWG core index, ranges from 1-4.
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


    def compile_run_core(self, awg_num):
       """
        Compiles and runs specified core, awg_num.

        Parameters
        ----------
        awg_num : 'int'
        AWG core index, ranges from 1-4.
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
        Stops specified core.

        Parameters
        ----------
        awg_num : 'int'
        AWG core index, ranges from 1-4.
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

    def set_command_table(self, ct, awg_idx):
        """
         Uploads command table ct (in specified format) to AWG core, awg_idx (ranges from 0-3).

         Parameters
         ----------
         ct : 'dict'
         Command table uploaded to AWG.
         awg_idx : 'int'
         Index of AWG core.
         Returns
         -------
         None.
        """
        dev = self._connection_settings["hdawg_id"]
        self._daq.setVector(f"/{dev}/awgs/{awg_idx}/commandtable/data", json.dumps(ct))
        self._command_tables["awg"+str(awg_idx+1)] = ct
