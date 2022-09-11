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
        self._daq_mod =  DaqModule(self._mfli)
        # try:
        #     self._daq_mod =  DaqModule(self._mfli)
        # except VisaIOError:
        #     print(1)
        #     self._daq_mod =  DaqModule(self._mfli)
        # else:
        #     print("Cannot Connect to Daq")

        self._input_voltages = []
        self._measured_voltages = []

    def sweep1D(self, channel, start_v, end_v, npoints, plot = False):
        self._dac._dac.query("CH "+str(channel))
        v_array = np.linspace(start_v,end_v,npoints)
        self._input_voltages.append(v_array)
        output_voltages = np.ones(npoints)

        for i in range(npoints):
            self._dac._dac.query("VOLT "+str(v_array[i]))
            self._dac._channel_configuration[channel] = v_array[i]
            val = self._daq_mod.continuous_numeric()
            if i == 0:
                output_voltages = val*output_voltages
            else:
                output_voltages[i] = val
            if plot == True:
                fig = plt.figure(figsize=(4,4))
                plot1DVoltageSweep(fig, v_array, output_voltages, i, channel)
            else:
                pass
        return (v_array, output_voltages)

    def sweep2D(self, channel_1, channel_2, start_v_1, end_v_1, start_v_2, end_v_2, n_points_1, n_points_2, plot = False):
        vx = np.linspace(start_v_1, end_v_1, n_points_1)
        vy = np.linspace(start_v_2, end_v_2, n_points_2)
        V_x, V_y = np.meshgrid(vx, vy)
        output_voltages = np.ones((n_points_1, n_points_2))
        idx = 0
        (dim0, dim1) = np.shape(V_x)
        for i in range(dim0):
            for j in range(dim1):
                self._dac.set_voltage(channel_1, V_x[i][j])
                self._dac.set_voltage(channel_2, V_y[i][j])
                val = self._daq_mod.continuous_numeric()
                if idx == 0:
                    output_voltages = val*output_voltages
                else:
                    output_voltages[i][j] = val
                if plot == True:
                    plot2DVoltageSweep(V_x, V_y, output_voltages, (channel_1, channel_2))
                idx += 1
        return (V_x, V_y, output_voltages)


        # self._dac._dac.query("CH "+str(channel))
        # v_array = np.linspace(start_v,end_v,npoints)
        # self._input_voltages.append(v_array)
        # output_voltages = np.ones(npoints)
        #
        # for i in range(npoints):
        #     self._dac._dac.query("VOLT "+str(v_array[i]))
        #     self._dac._channel_configuration[channel] = v_array[i]
        #     val = self._daq_mod.continuous_numeric()
        #     if i == 0:
        #         output_voltages = val*output_voltages
        #     else:
        #         output_voltages[i] = val
        #
        #     if plot == True:
        #         fig = plt.figure(figsize=(4,4))
        #         plot1DVoltageSweep(fig, v_array, output_voltages, i, channel)
        #     else:
        #         pass
        # return (v_array, output_voltages)
