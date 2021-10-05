#!/usr/bin/env python
import zhinst
import zhinst.utils

HOST = "localhost"

class HdawgDriver(Driver):
    '''
    Primary driver class of ZI-HDAWG instrument.

    ...

    Attributes
    - - - - - - -
    controller : str
         description

    Methods
    - - - - - - -
    example (additional=" "):
        Print ...
    '''

    def __init__(self):
       """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            name : str
                first name of the person
            surname : str
                family name of the person
            age : int
                age of the person
        """

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

    def init_config(self):
        d=1

    def value_setter(self):
        d=1

    def value_getter(self):
        d=1

    def awg_start_stop(self):
        d=1

    def queue_waveforms(self):
        d=1

    def sequence_getter(self):
        d=1

    def sequence_compiler(self):
        d=1  
