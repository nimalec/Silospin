from silospin.drivers.set_val import *
from silospin.drivers.homedac_box import DacDriverSerialServer
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters, pickle_charge_data

import numpy as np
import matplotlib.pyplot as plt

def do1DSweep(parameter, start_value, end_value, npoints, n_r = 10, n_fr = 1, plot = True, lockins = {1,2,3}, filter_tc=10e-3, demod_freq = 100e3, dac_mapping_file_path = 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac.pickle', save_path=None):
    dac_server = DacDriverSerialServer()
    mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq), 2: MfliDriverChargeStability(dev_id = "dev6573", timeconstant=filter_tc, demod_freq=demod_freq)}
    gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS", "Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    lockin_configs = {1: {1,2,3}, 2: {1,2}, 3: {2,3}, 4: {1}, 5: {2}, 6: {3}}
    dac_dict = unpickle_qubit_parameters(dac_mapping_file_path)
    channel_mapping = dac_dict["channel_mapping"]
    v_in_array = np.linspace(start_value, end_value, npoints)

    if lockins == lockin_configs[1]:
        V_out_all_1 = []
        V_out_all_2 = []
        V_out_all_3 = []
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)
            fig3 = plt.figure()
            ax3 = fig3.add_subplot(111)

            line1, = ax1.plot(v_in_array, np.zeros(len(v_in_array)))
            ax1.set_xlabel('Applied voltage [V]')
            ax1.set_ylabel('Measured output on lock-in 1 [V]')
            fig1.canvas.draw()
            ax1background = fig1.canvas.copy_from_bbox(ax1.bbox)
            plt.show(block=False)

            line2, = ax2.plot(v_in_array, np.zeros(len(v_in_array)))
            ax2.set_xlabel('Applied voltage [V]')
            ax2.set_ylabel('Measured output on lock-in 2 [V]')
            fig2.canvas.draw()
            ax2background = fig2.canvas.copy_from_bbox(ax2.bbox)
            plt.show(block=False)

            line3, = ax3.plot(v_in_array, np.zeros(len(v_in_array)))
            ax3.set_xlabel('Applied voltage [V]')
            ax3.set_ylabel('Measured output on lock-in 3 [V]')
            fig3.canvas.draw()
            ax3background = fig3.canvas.copy_from_bbox(ax3.bbox)
            plt.show(block=False)

            for i in range(n_fr):
                V_out_1 = []
                V_out_2 = []
                V_out_3 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())

                        if j%n_r == 0:
                            line1.set_data(v_in_array[0:len(V_out_1)], V_out_1)
                            fig1.canvas.draw()
                            fig1.canvas.flush_events()
                            ax1.set_ylim(np.amin(V_out_1), np.amax(V_out_1))

                            line2.set_data(v_in_array[0:len(V_out_2)], V_out_2)
                            fig2.canvas.draw()
                            fig2.canvas.flush_events()
                            ax2.set_ylim(np.amin(V_out_2), np.amax(V_out_2))

                            line3.set_data(v_in_array[0:len(V_out_3)], V_out_3)
                            fig3.canvas.draw()
                            fig3.canvas.flush_events()
                            ax3.set_ylim(np.amin(V_out_3), np.amax(V_out_3))

                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
                V_out_all_3.append(V_out_3)
        else:
            for i in range(n_fr):
                V_out_1 = []
                V_out_2 = []
                V_out_3 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
                V_out_all_3.append(V_out_3)
        return_value = {"v_applied": v_in_array.tolist(), "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_2),axis=0).tolist(), "v_out3": np.mean(np.array(V_out_all_3),axis=0).tolist()}

    elif lockins == lockin_configs[2] or lockins == lockin_configs[3]:
        V_out_all_1 = []
        V_out_all_2 = []
        idx_1 = list(lockins)[0]
        idx_2 = list(lockins)[1]
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)

            line1, = ax1.plot(v_in_array, np.zeros(len(v_in_array)))
            ax1.set_xlabel('Applied voltage [V]')
            ax1.set_ylabel('Measured output on lock-in '+str(idx_1)+' [V]')
            fig1.canvas.draw()
            ax1background = fig1.canvas.copy_from_bbox(ax1.bbox)
            plt.show(block=False)

            line2, = ax2.plot(v_in_array, np.zeros(len(v_in_array)))
            ax2.set_xlabel('Applied voltage [V]')
            ax2.set_ylabel('Measured output on lock-in '+str(idx_2)+' [V]')
            fig2.canvas.draw()
            ax2background = fig2.canvas.copy_from_bbox(ax1.bbox)
            plt.show(block=False)

            for i in range(n_fr):
                V_out_1 = []
                V_out_2 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        V_out_2.append(mflis[idx_2-1].get_sample_r())
                        if j%n_r == 0:
                            line1.set_data(v_in_array[0:len(V_out_1)], V_out_1)
                            fig1.canvas.draw()
                            fig1.canvas.flush_events()
                            ax1.set_ylim(np.amin(V_out_1), np.amax(V_out_1))

                            line2.set_data(v_in_array[0:len(V_out_2)], V_out_2)
                            fig2.canvas.draw()
                            fig2.canvas.flush_events()
                            ax2.set_ylim(np.amin(V_out_2), np.amax(V_out_2))
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)

        else:
            for i in range(n_fr):
                V_out_1 = []
                V_out_2 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        V_out_2.append(mflis[idx_2-1].get_sample_r())
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
        return_value = {"v_applied": v_in_array.tolist(), "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_2),axis=0).tolist()}

    elif lockins == lockin_configs[4] or lockins == lockin_configs[5] or lockins == lockin_configs[6]:
        V_out_all_1 = []
        idx_1 = list(lockins)[0]
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            line1, = ax1.plot(v_in_array, np.zeros(len(v_in_array)))
            ax1.set_xlabel('Applied voltage [V]')
            ax1.set_ylabel('Measured output on lock-in '+str(idx_1)+' [V]')
            fig1.canvas.draw()
            ax1background = fig1.canvas.copy_from_bbox(ax1.bbox)
            plt.show(block=False)

            for i in range(n_fr):
                V_out_1 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())

                        if j%n_r == 0:
                            line1.set_data(v_in_array[0:len(V_out_1)], V_out_1)
                            fig1.canvas.draw()
                            fig1.canvas.flush_events()
                            ax1.set_ylim(np.amin(V_out_1), np.amax(V_out_1))
                V_out_all_1.append(V_out_1)
        else:
            for i in range(n_fr):
                V_out_1 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                V_out_all_1.append(V_out_1)
        return_value = {"v_applied": v_in_array.tolist(), "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist()}
    else:
        pass

    if save_path:
        pickle_charge_data(return_value, save_path)
    else:
        pass
    return return_value

def do2DSweep(parameter1, start_value1, end_value1, npoints1, parameter2, start_value2, end_value2, npoints2, n_r = 10, n_fr = 1, plot = True, lockins = {1,2,3}, filter_tc=10e-3, demod_freq = 100e3, dac_mapping_file_path = 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac.pickle', save_path=None):
    dac_server = DacDriverSerialServer()
    mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq), 2: MfliDriverChargeStability(dev_id = "dev6573", timeconstant=filter_tc, demod_freq=demod_freq)}
    gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS", "Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    lockin_configs = {1: {1,2,3}, 2: {1,2}, 3: {2,3}, 4: {1}, 5: {2}, 6: {3}}
    dac_dict = unpickle_qubit_parameters(dac_mapping_file_path)
    channel_mapping = dac_dict["channel_mapping"]

    v_x = np.linspace(start_value1, end_value1, npoints1)
    v_y = np.linspace(start_value2, end_value2, npoints2)
    V_x, V_y = np.meshgrid(v_x, v_y)
    V_x_f = V_x.flatten()
    V_y_f = V_y.flatten()

    if lockins == lockin_configs[1]:
        V_out_all_1 = []
        V_out_all_2 = []
        V_out_all_3 = []
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            #ax1.set_xlim(start_value1, end_value1)
            #ax1.set_ylim(start_value2, end_value2)
            # fig2 = plt.figure()
            # ax2 = fig2.add_subplot(111)
            # fig3 = plt.figure()
            # ax3 = fig3.add_subplot(111)

            for i in range(n_fr):
                 v_out_1 = np.ones((npoints1,npoints2)).flatten()
                 v_out_2 = np.ones((npoints1,npoints2)).flatten()
                 v_out_3 = np.ones((npoints1,npoints2)).flatten()

                 for j in range(len(V_x_f)):
                     if j == 0:
                         set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                         set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                         v_meas_1 = mflis[0].get_sample_r()
                         v_meas_2 = mflis[1].get_sample_r()
                         v_meas_3 = mflis[2].get_sample_r()
                         v_out_1  = v_meas_1*v_out_1
                         v_out_2  = v_meas_2*v_out_2
                         v_out_3  = v_meas_3*v_out_3
                         V_out1 =  v_out_1.reshape([npoints1, npoints2])
                         V_out2 =  v_out_2.reshape([npoints1, npoints2])
                         V_out3 =  v_out_2.reshape([npoints1, npoints2])

                         img1 = ax1.imshow(V_out1)
                         fig1.canvas.draw()
                         plt.show(block=False)
                         # img2 = ax2.imshow(V_out2)
                         # fig2.canvas.draw()
                         # plt.show(block=False)
                         # img3 = ax3.imshow(V_out3)
                         # fig3.canvas.draw()
                         # plt.show(block=False)

                     else:
                         if j%npoints1 == 0:
                             set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                         else:
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)

                         v_meas_1 = mflis[0].get_sample_r()
                         v_meas_2 = mflis[1].get_sample_r()
                         v_meas_3 = mflis[2].get_sample_r()
                         v_out_1[j] = v_meas_1
                         v_out_2[j] = v_meas_2
                         v_out_3[j] = v_meas_3

                         if j%n_r == 0:
                             img1.set_data(v_out_1.reshape([npoints1, npoints2]))
                             img1.set_clim(np.amin(v_out_1), np.amax(v_out_1))
                             #ax1.set_xlim(start_value1, end_value1)
                             #ax1.set_ylim(start_value2, end_value2)
                            # ax.set_xlabel("Left barrier voltage [V]")
                            # ax.set_ylabel("Right barrier voltage [V]")
                             fig1.canvas.draw()
                             plt.show(block=False)
                             fig1.canvas.flush_events()

                            #  img2.set_data(v_out_2.reshape([npoints1, npoints2]))
                            #  img2.set_clim(np.amin(v_out_2), np.amax(v_out_2))
                            #  #ax2.set_xlim(start_value1, end_value1)
                            #  #ax2.set_ylim(start_value2, end_value2)
                            # # ax.set_xlabel("Left barrier voltage [V]")
                            # # ax.set_ylabel("Right barrier voltage [V]")
                            #  fig2.canvas.draw()
                            #  plt.show(block=False)
                            #  fig2.canvas.flush_events()
                            #
                            #  img3.set_data(v_out_3.reshape([npoints1, npoints2]))
                            #  img3.set_clim(np.amin(v_out_3), np.amax(v_out_3))
                            #  #ax3.set_xlim(start_value1, end_value1)
                            #  #ax3.set_ylim(start_value2, end_value2)
                            # # ax.set_xlabel("Left barrier voltage [V]")
                            # # ax.set_ylabel("Right barrier voltage [V]")
                            #  fig3.canvas.draw()
                            #  plt.show(block=False)
                            #  fig3.canvas.flush_events()
                         else:
                            pass
