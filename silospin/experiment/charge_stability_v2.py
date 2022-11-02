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
    def __init__(self, dac_id="COM3", mfli_id="dev5759", excluded_zurich_devices= ["dev8446", "dev5761"], filter_tc=10e-3):
        self._mfli = MfliDriverChargeStability(excluded_devices = excluded_zurich_devices, timeconstant=filter_tc)
        #self._dac = DacDriverSerial(dac_id)

    # def sweep1D(self, channel, start_v, end_v, npoints, n_r = 10, n_fr = 1, plot = True):
    #     self._dac.set_channel(channel)
    #     v_array = np.linspace(start_v,end_v,npoints)
    #     v_outer = []
    #     v_inner = []
    #     v_mean = []
    #
    #     plotter = None
    #     if plot == True:
    #         fig, ax = plt.subplots()
    #         def plot1Dtrace(i):
    #             self._dac.set_voltage(v_array[i])
    #             v_meas = self._mfli.get_sample_r()
    #             v_inner.append(v_meas)
    #             if len(v_inner) == npoints-1:
    #                 v_outer.append(v_inner)
    #             else:
    #                 pass
    #             if i%n_r == 0:
    #                 ax.clear()
    #                 ax.plot(v_array[0:len(v_inner)], v_inner)
    #                 ax.set_xlabel('Applied barrier voltage [V]')
    #                 ax.set_ylabel('Measured output [V]')
    #             else:
    #                 pass
    #             if len(v_outer) == n_fr:
    #                 plotter.pause()
    #                 v_mean.append(np.mean(np.array(v_outer),axis=0))
    #                 print("Plotting finished!")
    #             else:
    #                 pass
    #             if i == npoints-2:
    #                 v_inner.clear()
    #             else:
    #                 pass
    #         plotter = FuncAnimation(fig, plot1Dtrace, frames=npoints-1, interval=1, repeat=True)
    #         return (v_array, v_mean), plotter
    #         plt.show()
    #     else:
    #         v_outer = []
    #         idx = 0
    #         for j in range(n_fr):
    #             v_inner = []
    #             for i in range(npoints):
    #                 self._dac.set_voltage(v_array[i])
    #                 v_meas = self._mfli.get_sample_r()
    #                 v_inner.append(v_meas)
    #             v_outer.append(v_inner)
    #         return (v_array, v_mean.append(np.mean(np.array(v_outer),axis=0)))

# def sweep1D_v1(self, channels, v_range, npoints, n_r = 10, n_fr = 1, plot = True):
#     ##Need to add frame averaging here....
#     ##channels ==> tuple of ints for channel idxs
#     ##v_range ==> 2x2 list of voltage ranges
#     ##npoints ==> tuple of number of points for each dimension
#     ##n_r frequency of repeats
#     ##n_fr number of frames to loop over
#
#     ##V_out ==> list of output arrays to be averaged over eventually
#
#     #Input voltage mesh
#     V_outs = []
#     v_x = np.linspace(v_range[0][0], v_range[0][1], npoints[0])
#     v_y = np.linspace(v_range[1][0], v_range[1][1], npoints[1])
#     V_x, V_y = np.meshgrid(v_x, v_y)
#     V_x_f = V_x.flatten()
#     V_y_f = V_y.flatten()
#
#     #Output voltage array
#     output_voltages = np.ones((npoints[0], npoints[1]))
#     output_voltages_f = output_voltages.flatten()
#
#     if plot == True:
#         fig = plt.figure()
#         ax = fig.add_subplot(111)
#         for j in range(n_fr):
#             output_voltages = np.ones((npoints[0], npoints[1]))
#             output_voltages_f = output_voltages.flatten()
#             for i in range(len(V_x_f)):
#                 if i == 0:
#                     ##Apply new settings, plot
#                     self._dac.set_channel(channels[0])
#                     self._dac.set_voltage(V_x_f[i])
#                     self._dac.set_channel(channels[1])
#                     self._dac.set_voltage(V_y_f[i])
#                     v_meas = self._mfli.get_sample_r()
#                     output_voltages_new = v_meas*output_voltages_f
#                     V_out = output_voltages_new.reshape([npoints[0], npoints[1]])
#                     img = ax.imshow(V_out, interpolation="None", cmap="RdBu")
#                     fig.canvas.draw()
#                     ax.set_xlim(v_range[0][0]-0.5, v_range[0][1]+0.5)
#                     ax.set_ylim(v_range[1][0]-0.5, v_range[1][1]+0.5)
#                     ax.set_xlabel("Left barrier voltage [V]")
#                     ax.set_ylabel("Right barrier voltage [V]")
#                     plt.show(block=False)
#                 else:
#                     if i%npoints[0] == 0:
#                         self._dac.set_channel(channels[0])
#                         self._dac.set_voltage(V_x_f[i])
#                         self._dac.set_channel(channels[1])
#                         self._dac.set_voltage(V_y_f[i])
#                         v_meas = self._mfli.get_sample_r()
#                         output_voltages_new[i] = v_meas
#                     else:
#                         self._dac.set_voltage(V_y_f[i])
#                         v_meas = self._mfli.get_sample_r()
#                         output_voltages_new[i] = v_meas
#                     V_out = output_voltages_new.reshape([npoints[0], npoints[1]])
#
#                     if i%n_r == 0:
#                         img.set_data(V_out)
#                         img.set_clim(np.amin(V_out), np.amax(V_out))
#                         ax.set_xlim(v_range[0][0]-0.5, v_range[0][1]+0.5)
#                         ax.set_ylim(v_range[1][0]-0.5, v_range[1][1]+0.5)
#                         ax.set_xlabel("Left barrier voltage [V]")
#                         ax.set_ylabel("Right barrier voltage [V]")
#                         fig.canvas.draw()
#                         fig.canvas.flush_events()
#                     else:
#                         pass
#             V_outs.append(V_out)
#     else:
#         for j in range(n_fr):
#             output_voltages = np.ones((npoints[0], npoints[1]))
#             output_voltages_new = output_voltages.flatten()
#             for i in range(len(V_x_f)):
#                 if i%npoints[0] == 0:
#                      self._dac.set_channel(channels[0])
#                      self._dac.set_voltage(V_x_f[i])
#                      self._dac.set_channel(channels[1])
#                      self._dac.set_voltage(V_y_f[i])
#                      v_meas = self._mfli.get_sample_r()
#                      output_voltages_new[i] = v_meas
#                 else:
#                      self._dac.set_voltage(V_y_f[i])
#                      v_meas = self._mfli.get_sample_r()
#                      output_voltages_new[i] = v_meas
#                 V_out = output_voltages_new.reshape([npoints[0], npoints[1]])
#             V_outs.append(V_out)
#     V_out = np.mean(np.array(V_outs), axis=0)
#     return (V_x, V_y, V_out)

def sweep2D(self, channels, v_range, npoints, n_r = 10, n_fr = 1, plot = True):
    ##Need to add frame averaging here....
    ##channels ==> tuple of ints for channel idxs
    ##v_range ==> 2x2 list of voltage ranges
    ##npoints ==> tuple of number of points for each dimension
    ##n_r frequency of repeats
    ##n_fr number of frames to loop over

    ##V_out ==> list of output arrays to be averaged over eventually

    #Input voltage mesh
    V_outs = []
    v_x = np.linspace(v_range[0][0], v_range[0][1], npoints[0])
    v_y = np.linspace(v_range[1][0], v_range[1][1], npoints[1])
    V_x, V_y = np.meshgrid(v_x, v_y)
    V_x_f = V_x.flatten()
    V_y_f = V_y.flatten()

    #Output voltage array
    output_voltages = np.ones((npoints[0], npoints[1]))
    output_voltages_f = output_voltages.flatten()

    if plot == True:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for j in range(n_fr):
            output_voltages = np.ones((npoints[0], npoints[1]))
            output_voltages_f = output_voltages.flatten()
            for i in range(len(V_x_f)):
                if i == 0:
                    ##Apply new settings, plot
                    #self._dac.set_channel(channels[0])
                    #self._dac.set_voltage(V_x_f[i])
                    #self._dac.set_channel(channels[1])
                    #self._dac.set_voltage(V_y_f[i])
                    v_meas = self._mfli.get_sample_r()
                    output_voltages_new = v_meas*output_voltages_f
                    V_out = output_voltages_new.reshape([npoints[0], npoints[1]])
                    img = ax.imshow(V_out, interpolation="None", cmap="RdBu")
                    fig.canvas.draw()
                    ax.set_xlim(v_range[0][0]-0.5, v_range[0][1]+0.5)
                    ax.set_ylim(v_range[1][0]-0.5, v_range[1][1]+0.5)
                    ax.set_xlabel("Left barrier voltage [V]")
                    ax.set_ylabel("Right barrier voltage [V]")
                    plt.show(block=False)
                else:
                    if i%npoints[0] == 0:
                        #self._dac.set_channel(channels[0])
                        #self._dac.set_voltage(V_x_f[i])
                        #self._dac.set_channel(channels[1])
                        #self._dac.set_voltage(V_y_f[i])
                        v_meas = self._mfli.get_sample_r()
                        output_voltages_new[i] = v_meas
                    else:
                        #self._dac.set_voltage(V_y_f[i])
                        v_meas = self._mfli.get_sample_r()
                        output_voltages_new[i] = v_meas
                    V_out = output_voltages_new.reshape([npoints[0], npoints[1]])

                    if i%n_r == 0:
                        img.set_data(V_out)
                        img.set_clim(np.amin(V_out), np.amax(V_out))
                        ax.set_xlim(v_range[0][0]-0.5, v_range[0][1]+0.5)
                        ax.set_ylim(v_range[1][0]-0.5, v_range[1][1]+0.5)
                        ax.set_xlabel("Left barrier voltage [V]")
                        ax.set_ylabel("Right barrier voltage [V]")
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                    else:
                        pass
            V_outs.append(V_out)
    else:
        for j in range(n_fr):
            output_voltages = np.ones((npoints[0], npoints[1]))
            output_voltages_new = output_voltages.flatten()
            for i in range(len(V_x_f)):
                if i%npoints[0] == 0:
                    # self._dac.set_channel(channels[0])
                    # self._dac.set_voltage(V_x_f[i])
                    # self._dac.set_channel(channels[1])
                    # self._dac.set_voltage(V_y_f[i])
                     v_meas = self._mfli.get_sample_r()
                     output_voltages_new[i] = v_meas
                else:
                    # self._dac.set_voltage(V_y_f[i])
                     v_meas = self._mfli.get_sample_r()
                     output_voltages_new[i] = v_meas
                V_out = output_voltages_new.reshape([npoints[0], npoints[1]])
            V_outs.append(V_out)
    V_out = np.mean(np.array(V_outs), axis=0)
    return (V_x, V_y, V_out)
