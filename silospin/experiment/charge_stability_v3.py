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
    def __init__(self, dac_id="COM3", filter_tc=10e-3):
        self._mflis = {0: MfliDriverChargeStability(excluded_devices=["dev5761", "dev8446", "dev8485", "dev6573"], timeconstant=filter_tc), 1: MfliDriverChargeStability(excluded_devices=["dev5759", "dev8446", "dev8485", "dev6573"], timeconstant=filter_tc)}
        self._dac = DacDriverSerial(dac_id)

    def sweep1D(self, channel, start_v, end_v, npoints, lockins = {1, 2}, n_r = 10, n_fr = 1, plot = True):
        ##Lockin 1 ==> "dev5759"
        ##Lockin 2 ==> "dev5761"
        v_in_array = np.linspace(start_v,end_v,npoints)
        self._dac.set_channel(channel)

        if {1,2} == lockins:
            V_out_all_1 = []
            V_out_all_2 = []
            if plot == True:
                fig_1 = plt.figure()
                ax_1 = fig_1.add_subplot(111)
                fig_2 = plt.figure()
                ax_2 = fig_2.add_subplot(111)
                for j in range(n_fr):
                    V_out_1 = []
                    V_out_2 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[0].get_sample_r()
                        V_meas_2 = self._mflis[1].get_sample_r()
                        V_out_1.append(V_meas_1)
                        V_out_2.append(V_meas_2)
                        if i%n_r == 0:
                            ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
                            ax_1.set_xlabel('Applied barrier voltage [V]')
                            ax_1.set_ylabel('Measured output on lock-in 1 [V]')
                            fig_1.canvas.draw()

                            ax_2.plot(v_in_array[0:len(V_out_2)], V_out_2)
                            ax_2.set_xlabel('Applied barrier voltage [V]')
                            ax_2.set_ylabel('Measured output voltage on lock-in 2 [V]')
                            fig_2.canvas.draw()

                            plt.show(block=False)
                    V_out_all_2.append(V_out_1)

            else:
                for j in range(n_fr):
                    V_out_1 = []
                    V_out_2 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[0].get_sample_r()
                        V_meas_2 = self._mflis[1].get_sample_r()
                        V_out_1.append(V_meas_1)
                        V_out_2.append(V_meas_2)
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
            return_value = (v_in_array,np.mean(np.array(V_out_all_1),axis=0), np.mean(np.array(V_out_all_2),axis=0))

        elif {1} == lockins:
            V_out_all_1 = []
            if plot == True:
                fig_1 = plt.figure()
                ax_1 = fig_1.add_subplot(111)
                for j in range(n_fr):
                    V_out_1 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[0].get_sample_r()
                        V_out_1.append(V_meas_1)
                        if i%n_r == 0:
                            ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
                            ax_1.set_xlabel('Applied barrier voltage [V]')
                            ax_1.set_ylabel('Measured output voltage on lock-in 1 [V]')
                            fig_1.canvas.draw()
                            plt.show(block=False)
                    V_out_all_1.append(V_out_1)

            else:
                for j in range(n_fr):
                    V_out_1 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[0].get_sample_r()
                        V_out_1.append(V_meas_1)
                V_out_all_1.append(V_out_1)
            return_value = (v_in_array,np.mean(np.array(V_out_all_1),axis=0))

        elif {2} == lockins:
            V_out_all_1 = []
            v_in_array = np.linspace(start_v,end_v,npoints)
            if plot == True:
                fig_1 = plt.figure()
                ax_1 = fig_1.add_subplot(111)
                for j in range(n_fr):
                    V_out_1 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[1].get_sample_r()
                        V_out_1.append(V_meas_1)
                        if i%n_r == 0:
                            ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
                            ax_1.set_xlabel('Applied barrier voltage [V]')
                            ax_1.set_ylabel('Measured output voltage on lock-in 2[V]')
                            fig_1.canvas.draw()
                            plt.show(block=False)
                    V_out_all_1.append(V_out_1)

            else:
                for j in range(n_fr):
                    V_out_1 = []
                    for i in range(len(v_in_array)):
                        self._dac.set_voltage(v_in_array[i])
                        V_meas_1 = self._mflis[1].get_sample_r()
                        V_out_1.append(V_meas_1)
                V_out_all_1.append(V_out_1)
            return_value = (v_in_array,np.mean(np.array(V_out_all_1),axis=0))
        else:
            pass

        return return_value
