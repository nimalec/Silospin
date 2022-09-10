from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.zi_mfli_driver import MfliDaqModule as DaqModule
from silospin.drivers.homedac_box import DacDriver
from silospin.plotting.plotting_functions import plot1DVoltageSweep
import matplotlib.pyplot as plt
import numpy as np
import time

class ChargeStabilitySweeps:
    def __init__(self, dac_id="ASRL3::INSTR", mfli_id="dev5759"):
        self._dac = DacDriver(dac_id)
        self._mfli = MfliDriver(mfli_id)
        daq_temp =  DaqModule(self._mfli)
        self._daq_mod =  DaqModule(self._mfli)
        self._input_voltages = []
        self._measured_voltages = []

    def sweep1D(self, channel, start_v, end_v, npoints, plot = False):
        self._dac._dac.query("CH "+str(channel))
        v_array = np.linspace(start_v,end_v,npoints)
        self._input_voltages.append(v_array)
        output_voltages = np.ones(npoints)

        for i in range(npoints):
            self._dac._dac.query("VOLT "+str(v_array[i]))
            time.sleep(0.1)
            self._dac._channel_configuration[channel] = v_array[i]
            val = self._daq_mod.continuous_numeric()
            if i == 0:
                output_voltages = val*output_voltages
            else:
                output_voltages[i] = val

            if plot == True:
                fig = plt.figure(figsize=(4,4))
                #plot1DVoltageSweep(fig, v_array, output_voltages, i, channel)
                plot1DVoltageSweep(fig, v_array, output_voltages, i, channel)
            else:
                pass
            time.sleep(0.1)
        return (v_array, output_voltages)


    #def sweep2D(self,):
