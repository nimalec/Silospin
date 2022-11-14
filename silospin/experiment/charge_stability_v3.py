from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.zi_mfli_driver import MfliDaqModule as DaqModule
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability
from silospin.drivers.homedac_box import DacDriver, DacDriverSerial
from silospin.plotting.plotting_functions import plot1DVoltageSweep, plot2DVoltageSweep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
import time

class ChargeStabilitySweepsSerial:
    def __init__(self, dac_id="COM3", mfli_id= "dev5759", excluded_zurich_devices= ["dev8446", "dev5761"], filter_tc=10e-3):

        ##Modify here to account for multiple instruments
        self._mfli = MfliDriverChargeStability(excluded_devices = excluded_zurich_devices, timeconstant=filter_tc)
        self._dac = DacDriverSerial(dac_id)

    def sweep1D(self, channel, start_v, end_v, npoints, n_r = 10, n_fr = 1, plot = True):
        self._dac.set_channel(channel)
        V_out_all_1 = []
        v_in_array = np.linspace(start_v,end_v,npoints)
        if plot == True:
            fig_1 = plt.figure()
            ax_1 = fig_1.add_subplot(111)
            for j in range(n_fr):
                V_out_1 = []
                for i in range(len(v_in_array)):
                    self._dac.set_voltage(v_in_array[i])
                    V_meas_1 = self._mfli.get_sample_r()
                    V_out_1.append(V_meas_1)
                    if i%n_r == 0:
                        ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
                        ax_1.set_xlabel('Applied barrier voltage [V]')
                        ax_1.set_ylabel('Measured output [V]')
                        fig_1.canvas.draw()
                        plt.show(block=False)
                V_out_all_1.append(V_out_1)

        else:
            for j in range(n_fr):
                V_out_1 = []
                for i in range(len(v_in_array)):
                    self._dac.set_voltage(v_in_array[i])
                    V_meas_1 = self._mfli.get_sample_r()
                    V_out_1.append(V_meas_1)
            V_out_all_1.append(V_out_1)
            print(len(V_out_all_1))
        return (v_in_array, np.mean(np.array(V_out_all_1),axis=0))
