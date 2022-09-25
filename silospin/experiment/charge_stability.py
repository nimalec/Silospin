from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.zi_mfli_driver import MfliDaqModule as DaqModule
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability
from silospin.drivers.homedac_box import DacDriver, DacDriverSerial
from silospin.plotting.plotting_functions import plot1DVoltageSweep, plot2DVoltageSweep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class ChargeStabilitySweeps:
    def __init__(self, dac_id="ASRL3::INSTR", mfli_id="dev5759", excluded_zurich_devices= ["dev8446", "dev5761"], filter_tc=10e-3):
        self._mfli = MfliDriverChargeStability(excluded_devices = excluded_zurich_devices, timeconstant=filter_tc)
        self._dac = DacDriver(dac_id)

    def sweep1D(self, channel, start_v, end_v, npoints, plot = True):
        ##Note: need to add external loopss
        self._dac.set_channel(channel)
        v_array = np.linspace(start_v,end_v,npoints)
        v_outputs = []
        if plot == True:
            fig, ax = plt.subplots()
            def plot1Dtrace(i):
                self._dac.set_voltage(v_array[i])
                v_meas = self._mfli.get_sample_r()
                v_outputs.append(v_meas)
                ax.clear()
                ax.plot(v_array[0:len(v_outputs)], v_outputs)
                ax.set_xlabel("Applied barrier voltage [V]")
                ax.set_ylabel("Measured output [V]")
            plotter = FuncAnimation(fig, plot1Dtrace, frames=npoints, interval=0.001, repeat=False)
            return plotter
            plt.show()
        else:
            v_outputs = []
            for i in range(npoints):
                self._dac.set_voltage(v_array[i])
                v_meas = self._mfli.get_sample_r()
                v_outputs.append(v_meas)
        return v_outputs

    def sweep2D(self, channel_1, channel_2, start_v_1, end_v_1, start_v_2, end_v_2, n_points_1, n_points_2):
        ##Note: need to add external loopss
        vx = np.linspace(start_v_1, end_v_1, n_points_1)
        vy = np.linspace(start_v_2, end_v_2, n_points_2)
        V_x, V_y = np.meshgrid(vx, vy)
        output_voltages = np.ones((n_points_1, n_points_2))
        V_x_f = V_x.flatten()
        V_y_f = V_y.flatten()
        output_voltages_f = output_voltages.flatten()

        fig, ax = plt.subplots()
        def plot2Dtrace(i):
            if i == 0:
                self._dac.set_channel(channel_1)
                self._dac.set_voltage(V_x_f[i])
                self._dac.set_channel(channel_2)
                self._dac.set_voltage(V_y_f[i])
                v_meas = self._mfli.get_sample_r()
                ax.clear()
                output_voltages_f_t = v_meas*output_voltages_f
                V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
                z_min = np.min(output_voltages_f_t)
                z_max = np.max(output_voltages_f_t)
                c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
                cbar = fig.colorbar(c, ax=ax0)
                cbar.set_label('Output Voltage [V]', rotation=270)
                ax.set_xlabel("Left barrier voltage [V]")
                ax.set_ylabel("Right barrier voltage [V]")
            else:
                if V_x_f[i] == V_x_f[i-1]:
                    self._dac.set_channel(channel_2)
                    self._dac.set_voltage(V_y_f[i])
                    v_meas = self._mfli.get_sample_r()
                    ax.clear()
                    output_voltages_f_t[i] = v_meas
                    V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
                    z_min = np.min(output_voltages_f_t)
                    z_max = np.max(output_voltages_f_t)
                    c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
                    cbar = fig.colorbar(c, ax=ax0)
                elif V_y_f[i] == V_y_f[i-1]:
                    self._dac.set_channel(channel_1)
                    self._dac.set_voltage(V_x_f[i])
                    v_meas = self._mfli.get_sample_r()
                    ax.clear()
                    output_voltages_f_t[i] = v_meas
                    V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
                    z_min = np.min(output_voltages_f_t)
                    z_max = np.max(output_voltages_f_t)
                    c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
                    cbar = fig.colorbar(c, ax=ax0)
                else:
                    self._dac.set_channel(channel_1)
                    self._dac.set_voltage(V_x_f[i])
                    self._dac.set_channel(channel_2)
                    self._dac.set_voltage(V_y_f[i])
                    v_meas = self._mfli.get_sample_r()
                    ax.clear()
                    output_voltages_f_t[i] = v_meas
                    V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
                    z_min = np.min(output_voltages_f)
                    z_max = np.max(output_voltages_f)
                    c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
                    cbar = fig.colorbar(c, ax=ax0)
        plotter = FuncAnimation(fig, plot2Dtrace, frames=n_points_1*n_points_2, interval=0.001, repeat=False)
        return plotter
        plt.show()

class ChargeStabilitySweepsSerial:
    def __init__(self, dac_id="COM3", mfli_id="dev5759", excluded_zurich_devices= ["dev8446", "dev5761"], filter_tc=10e-3):
        self._mfli = MfliDriverChargeStability(excluded_devices = excluded_zurich_devices, timeconstant=filter_tc)
        self._dac = DacDriverSerial(dac_id)

    def sweep1D(self, channel, start_v, end_v, npoints, plot = True):
        ##Note: need to add external loops
        self._dac.set_channel(channel)
        v_array = np.linspace(start_v,end_v,npoints)
        v_outputs = []
        if plot == True:
            fig, ax = plt.subplots()
            def plot1Dtrace(i):
                self._dac.set_voltage(v_array[i])
                v_meas = self._mfli.get_sample_r()
                v_outputs.append(v_meas)
                ax.clear()
                ax.plot(v_array[0:len(v_outputs)], v_outputs)
                ax.set_xlabel("Applied barrier voltage [V]")
                ax.set_ylabel("Measured output [V]")
            plotter = FuncAnimation(fig, plot1Dtrace, frames=npoints, interval=0.001, repeat=False)
            return plotter, v_outputs
            plt.show()
        else:
            v_outputs = []
            for i in range(npoints):
                self._dac.set_voltage(v_array[i])
                v_meas = self._mfli.get_sample_r()
                v_outputs.append(v_meas)
            return v_outputs

    def sweep1DFrameAverage(self, channel, start_v, end_v, npoints, n_fr = 1, plot = True):
        ##Note: need to add external loops
        self._dac.set_channel(channel)
        v_array = np.linspace(start_v,end_v,npoints)
        v_outer = []
        v_inner = []
        v_mean = None
        plotter = None
        if plot == True:
            fig, ax = plt.subplots()
            def plot1Dtrace(i):
                self._dac.set_voltage(v_array[i])
                v_meas = self._mfli.get_sample_r()
                v_inner.append(v_meas)
                ax.clear()
                ax.plot(v_array[0:len(v_inner)], v_inner)
                ax.set_xlabel("Applied barrier voltage [V]")
                ax.set_ylabel("Measured output [V]")
                if len(v_inner) == npoints-1:
                    v_outer.append(v_inner)
                    if len(v_outer) == n_fr:
                        plotter.pause()
                    else:
                        pass
                else:
                    pass

                if i == npoints-2:
                    v_inner.clear()
                else:
                    pass

            plotter = FuncAnimation(fig, plot1Dtrace, frames=npoints-1, interval=0.001, repeat=True)
            return v_outer, v_outputs 
            plt.show()
        else:
            v_outer = []
            for j in range(n_fr):
                v_inner = []
                for i in range(npoints):
                    self._dac.set_voltage(v_array[i])
                    v_meas = self._mfli.get_sample_r()
                    v_inner.append(v_meas)
                v_outer.append(np.array(v_inner))
            v_outer = np.array(v_outer)
            return np.mean(v_outer, axis = 0)

    # def sweep2D(self, channel_1, channel_2, start_v_1, end_v_1, start_v_2, end_v_2, n_points_1, n_points_2):
    #     ##Note: need to add external loopss
    #     vx = np.linspace(start_v_1, end_v_1, n_points_1)
    #     vy = np.linspace(start_v_2, end_v_2, n_points_2)
    #     V_x, V_y = np.meshgrid(vx, vy)
    #     output_voltages = np.ones((n_points_1, n_points_2))
    #     V_x_f = V_x.flatten()
    #     V_y_f = V_y.flatten()
    #     output_voltages_f = output_voltages.flatten()
    #
    #     fig, ax = plt.subplots()
    #     def plot2Dtrace(i):
    #         if i == 0:
    #             self._dac.set_channel(channel_1)
    #             self._dac.set_voltage(V_x_f[i])
    #             self._dac.set_channel(channel_2)
    #             self._dac.set_voltage(V_y_f[i])
    #             v_meas = self._mfli.get_sample_r()
    #             ax.clear()
    #             output_voltages_f_t = v_meas*output_voltages_f
    #             V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
    #             z_min = np.min(output_voltages_f_t)
    #             z_max = np.max(output_voltages_f_t)
    #             c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
    #             cbar = fig.colorbar(c, ax=ax0)
    #             cbar.set_label('Output Voltage [V]', rotation=270)
    #             ax.set_xlabel("Left barrier voltage [V]")
    #             ax.set_ylabel("Right barrier voltage [V]")
    #         else:
    #             if V_x_f[i] == V_x_f[i-1]:
    #                 self._dac.set_channel(channel_2)
    #                 self._dac.set_voltage(V_y_f[i])
    #                 v_meas = self._mfli.get_sample_r()
    #                 ax.clear()
    #                 output_voltages_f_t[i] = v_meas
    #                 V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
    #                 z_min = np.min(output_voltages_f_t)
    #                 z_max = np.max(output_voltages_f_t)
    #                 c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
    #                 cbar = fig.colorbar(c, ax=ax0)
    #             elif V_y_f[i] == V_y_f[i-1]:
    #                 self._dac.set_channel(channel_1)
    #                 self._dac.set_voltage(V_x_f[i])
    #                 v_meas = self._mfli.get_sample_r()
    #                 ax.clear()
    #                 output_voltages_f_t[i] = v_meas
    #                 V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
    #                 z_min = np.min(output_voltages_f_t)
    #                 z_max = np.max(output_voltages_f_t)
    #                 c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
    #                 cbar = fig.colorbar(c, ax=ax0)
    #             else:
    #                 self._dac.set_channel(channel_1)
    #                 self._dac.set_voltage(V_x_f[i])
    #                 self._dac.set_channel(channel_2)
    #                 self._dac.set_voltage(V_y_f[i])
    #                 v_meas = self._mfli.get_sample_r()
    #                 ax.clear()
    #                 output_voltages_f_t[i] = v_meas
    #                 V_out = output_voltages_f_t.reshape([n_points_1, n_points_2])
    #                 z_min = np.min(output_voltages_f)
    #                 z_max = np.max(output_voltages_f)
    #                 c = ax.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
    #                 cbar = fig.colorbar(c, ax=ax0)
    #     plotter = FuncAnimation(fig, plot2Dtrace, frames=n_points_1*n_points_2, interval=0.001, repeat=False)
    #     return plotter
    #     plt.show()
