from silospin.drivers.set_val import *
from silospin.drivers.homedac_box import DacDriverSerialServer
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters, pickle_charge_data

import numpy as np
import matplotlib.pyplot as plt

def do1DSweep(parameter, start_value, end_value, npoints, n_r = 10, n_fr = 1, plot = True, lockins = {1,2,3}, filter_tc=10e-3, demod_freq = 100e3, dac_mapping_file_path = 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac.pickle', save_path=None):
    '''
    Outputs the mapping between AWG cores/channels and gate labels. \n
    Outer keys of dictionary correspond to core number running from 1-4 (e.g. chanel_mapping = {1 : {}, ... , 4: {}). These keys have values in the form of dictonaries with the following keys and values. \n
    - "ch", dictionary of the core's output channels, output gate labels, and gate indices in the GST convention (dict) \n
    - "rf", 1 if core is for RF pulses and 0 if for DC pulses (int) \n
    The dictionaries corresponding to the key "ch" have the following keys and values,
    - "index", list of 2 channels corresponding the specified core (grouping given by- 1: [1,2], 2: [3,4], 3: [5,6], 4: [7,8]). \n
    - "label", list of 2 labels corresponding to each channel (e.g. ["i1", "q1"] as IQ pair for RF or  ["p12", "p21"] as 2 plunger channels for DC). \n
    - "gateindex", list of 2 gate indices corresponding to GST indices. (e.g. gate (1)x(1) maps to gateindex [1,1] for core 1 or (7)p(7)(8)p(8) maps to indices [7,8] of core 4.)\n
    Note: currently configured for 1 HDAWG unit with 4 AWG cores.   \n
    Parameters:
                    rf_cores (list): list of core indices dedicated to RF control (default set to [1,2,3]).
                    plunger_channels (dict): dictionary of RF core (default set to  {"p12": 7, "p21": 8})).
    Returns:
       channel_mapper (dict): Dictionary representing channel mapping.
    '''

    dac_server = DacDriverSerialServer()
    #mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq), 2: MfliDriverChargeStability(dev_id = "dev6573", timeconstant=filter_tc, demod_freq=demod_freq)}
    mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq, sig_path="/dev5759/demods/0/sample"), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq, sig_path="/dev5761/demods/0/sample")}

    gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS", "Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    lockin_configs = {1: {1,2,3}, 2: {1,2}, 3: {2,3}, 4: {1,3}, 5: {1}, 6: {2}, 7: {3}}
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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())
                        dac_server.close()

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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())
                        dac_server.close()
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
                V_out_all_3.append(V_out_3)
        return_value = {"v_applied": v_in_array.tolist(), "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_2),axis=0).tolist(), "v_out3": np.mean(np.array(V_out_all_3),axis=0).tolist()}

    elif lockins == lockin_configs[2] or lockins == lockin_configs[3] or lockins == lockin_configs[4]:
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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        V_out_2.append(mflis[idx_2-1].get_sample_r())

                        dac_server.close()
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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        V_out_2.append(mflis[idx_2-1].get_sample_r())
                        dac_server.close()
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
        return_value = {"v_applied": v_in_array.tolist(), "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_2),axis=0).tolist()}

    elif lockins == lockin_configs[5] or lockins == lockin_configs[6] or lockins == lockin_configs[7]:
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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        dac_server.close()

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
                        dac_server = DacDriverSerialServer()
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[idx_1-1].get_sample_r())
                        dac_server.close()
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
    '''
    Outputs the mapping between AWG cores/channels and gate labels. \n
    Outer keys of dictionary correspond to core number running from 1-4 (e.g. chanel_mapping = {1 : {}, ... , 4: {}). These keys have values in the form of dictonaries with the following keys and values. \n
    - "ch", dictionary of the core's output channels, output gate labels, and gate indices in the GST convention (dict) \n
    - "rf", 1 if core is for RF pulses and 0 if for DC pulses (int) \n
    The dictionaries corresponding to the key "ch" have the following keys and values,
    - "index", list of 2 channels corresponding the specified core (grouping given by- 1: [1,2], 2: [3,4], 3: [5,6], 4: [7,8]). \n
    - "label", list of 2 labels corresponding to each channel (e.g. ["i1", "q1"] as IQ pair for RF or  ["p12", "p21"] as 2 plunger channels for DC). \n
    - "gateindex", list of 2 gate indices corresponding to GST indices. (e.g. gate (1)x(1) maps to gateindex [1,1] for core 1 or (7)p(7)(8)p(8) maps to indices [7,8] of core 4.)\n
    Note: currently configured for 1 HDAWG unit with 4 AWG cores.   \n
    Parameters:
                    rf_cores (list): list of core indices dedicated to RF control (default set to [1,2,3]).
                    plunger_channels (dict): dictionary of RF core (default set to  {"p12": 7, "p21": 8})).
    Returns:
       channel_mapper (dict): Dictionary representing channel mapping.
    '''
    dac_server = DacDriverSerialServer()
    #mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq), 2: MfliDriverChargeStability(dev_id = "dev6573", timeconstant=filter_tc, demod_freq=demod_freq)}
    mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc, demod_freq=demod_freq, sig_path="/dev5759/demods/0/sample"), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc, demod_freq=demod_freq, sig_path="/dev5761/demods/0/sample")}
    gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS", "Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    lockin_configs = {1: {1,2,3}, 2: {1,2}, 3: {2,3}, 4: {1,3}, 5: {1}, 6: {2}, 7: {3}}
    dac_dict = unpickle_qubit_parameters(dac_mapping_file_path)
    channel_mapping = dac_dict["channel_mapping"]

    v_x = np.linspace(start_value1, end_value1, npoints1)
    v_y = np.linspace(start_value2, end_value2, npoints2)
    V_x, V_y = np.meshgrid(v_x, v_y)
    V_x_f = V_x.flatten()
    V_y_f = V_y.flatten()
    print(V_x_f)
    print(V_y_f)

    ## All lockins simultaneous: 1,2,3.
    if lockins == lockin_configs[1]:
        V_out_all_1 = []
        V_out_all_2 = []
        V_out_all_3 = []
        v_out_1 = np.ones((npoints1,npoints2)).flatten()
        v_out_2 = np.ones((npoints1,npoints2)).flatten()
        v_out_3 = np.ones((npoints1,npoints2)).flatten()
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)
            fig3 = plt.figure()
            ax3 = fig3.add_subplot(111)

            for i in range(n_fr):
                 v_out_1 = np.ones((npoints1,npoints2)).flatten()
                 v_out_2 = np.ones((npoints1,npoints2)).flatten()
                 v_out_3 = np.ones((npoints1,npoints2)).flatten()

                 for j in range(len(V_x_f)):
                     if j == 0:
                         dac_server = DacDriverSerialServer()
                         set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                         set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                         dac_server.close()
                         v_meas_1 = mflis[0].get_sample_r()
                         v_meas_2 = mflis[1].get_sample_r()
                         v_meas_3 = mflis[2].get_sample_r()
                         v_out_1  = v_meas_1*v_out_1
                         v_out_2  = v_meas_2*v_out_2
                         v_out_3  = v_meas_3*v_out_3
                         V_out1 =  v_out_1.reshape([npoints1, npoints2])
                         V_out2 =  v_out_2.reshape([npoints1, npoints2])
                         V_out3 =  v_out_3.reshape([npoints1, npoints2])

                         img1 = ax1.imshow(V_out1, extent=[start_value1,end_value1,start_value2,end_value2])
                         ax1.set_xlabel(parameter1+" gate voltage [V]")
                         ax1.set_ylabel(parameter2+" gate voltage [V]")
                         fig1.canvas.draw()
                         cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                         cbar1.set_label('Demodulated voltage from lock-in 1 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         img2 = ax2.imshow(V_out2, extent=[start_value1,end_value1,start_value2,end_value2])
                         ax2.set_xlabel(parameter1+" gate voltage [V]")
                         ax2.set_ylabel(parameter2+" gate voltage [V]")
                         fig2.canvas.draw()
                         cbar2 = fig2.colorbar(img2, ax=ax2, extend='both')
                         cbar2.set_label('Demodulated voltage from lock-in 2 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         img3 = ax3.imshow(V_out3, extent=[start_value1,end_value1,start_value2,end_value2])
                         ax3.set_xlabel(parameter1+" gate voltage [V]")
                         ax3.set_ylabel(parameter2+" gate voltage [V]")
                         fig3.canvas.draw()
                         cbar3 = fig3.colorbar(img3, ax=ax3, extend='both')
                         cbar3.set_label('Demodulated voltage from lock-in 3 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         if i>0:
                             cbar1.remove()
                             cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                             cbar2.remove()
                             cbar2 = fig2.colorbar(img2, ax=ax2, extend='both')
                             cbar3.remove()
                             cbar3 = fig1.colorbar(img3, ax=ax3, extend='both')
                         else:
                             pass
                     else:
                         if j%npoints1 == 0:
                             pass
                             dac_server = DacDriverSerialServer()
                             set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         else:
                             pass
                             dac_server = DacDriverSerialServer()
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         v_meas_1 = mflis[0].get_sample_r()
                         v_meas_2 = mflis[1].get_sample_r()
                         v_meas_3 = mflis[2].get_sample_r()
                         v_out_1[j] = v_meas_1
                         v_out_2[j] = v_meas_2
                         v_out_3[j] = v_meas_3

                         if j%n_r == 0:
                             img1.set_data(v_out_1.reshape([npoints1, npoints2]))
                             img1.set_clim(np.amin(v_out_1), np.amax(v_out_1))

                             img2.set_data(v_out_2.reshape([npoints1, npoints2]))
                             img2.set_clim(np.amin(v_out_2), np.amax(v_out_2))

                             img3.set_data(v_out_3.reshape([npoints1, npoints2]))
                             img3.set_clim(np.amin(v_out_3), np.amax(v_out_3))

                             fig1.canvas.draw()
                             plt.show(block=False)
                             fig1.canvas.flush_events()

                             fig2.canvas.draw()
                             plt.show(block=False)
                             fig2.canvas.flush_events()

                             fig3.canvas.draw()
                             plt.show(block=False)
                             fig3.canvas.flush_events()

                         else:
                            pass
                 V_out_all_1.append(v_out_1)
                 V_out_all_2.append(v_out_2)
                 V_out_all_3.append(v_out_3)

        return_value = {"v_applied": [V_x.tolist(), V_y.tolist()], "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_3),axis=0).tolist(), "v_out3": np.mean(np.array(V_out_all_3),axis=0).tolist()}

    elif lockins == lockin_configs[2] or lockins == lockin_configs[3] or lockins == lockin_configs[4]:
        idx_1 = list(lockins)[0]-1
        idx_2 = list(lockins)[1]-1

        V_out_all_1 = []
        V_out_all_2 = []
        v_out_1 = np.ones((npoints1,npoints2)).flatten()
        v_out_2 = np.ones((npoints1,npoints2)).flatten()
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)

            for i in range(n_fr):
                 v_out_1 = np.ones((npoints1,npoints2)).flatten()
                 v_out_2 = np.ones((npoints1,npoints2)).flatten()

                 for j in range(len(V_x_f)):
                     if j == 0:
                         dac_server = DacDriverSerialServer()
                         set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                         set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                         dac_server.close()
                         v_meas_1 = mflis[idx_1].get_sample_r()
                         v_meas_2 = mflis[idx_2].get_sample_r()

                         v_out_1  = v_meas_1*v_out_1
                         v_out_2  = v_meas_2*v_out_2


                         V_out1 =  v_out_1.reshape([npoints1, npoints2]).T
                         V_out2 =  v_out_2.reshape([npoints1, npoints2]).T

                         img1 = ax1.imshow(V_out1, extent=[start_value1,end_value1,end_value2,start_value2])
                         #img1 = ax1.imshow(V_out1, extent=[start_value2,end_value2,start_value1,end_value1])
                         ax1.set_xlabel(parameter1+" gate voltage [V]")
                         ax1.set_ylabel(parameter2+" gate voltage [V]")
                         fig1.canvas.draw()
                         cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                         cbar1.set_label('Demodulated voltage from lock-in 1 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         #img2 = ax2.imshow(V_out2, extent=[start_value1,end_value1,start_value2,end_value2])
                         img2 = ax2.imshow(V_out2, extent=[start_value1,end_value1,end_value2,start_value2])
                         #img2 = ax2.imshow(V_out2, extent=[end_value1,start_value1,start_value2,end_value2])
                         #img2 = ax2.imshow(V_out2, extent=[start_value2,end_value2,start_value1,end_value1])
                         ax2.set_xlabel(parameter1+" gate voltage [V]")
                         ax2.set_ylabel(parameter2+" gate voltage [V]")
                         fig2.canvas.draw()
                         cbar2 = fig2.colorbar(img2, ax=ax2, extend='both')
                         cbar2.set_label('Demodulated voltage from lock-in 2 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         if i>0:
                             cbar1.remove()
                             cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                             cbar2.remove()
                             cbar2 = fig2.colorbar(img2, ax=ax2, extend='both')
                         else:
                             pass
                     else:
                         if j%npoints1 == 0:
                             print(V_y_f[j]) 
                             dac_server = DacDriverSerialServer()
                             set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         else:
                             dac_server = DacDriverSerialServer()
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         v_meas_1 = mflis[idx_1].get_sample_r()
                         v_meas_2 = mflis[idx_2].get_sample_r()

                         v_out_1[j] = v_meas_1
                         v_out_2[j] = v_meas_2


                         if j%n_r == 0:
                             #img1.set_data(v_out_1.reshape([npoints1, npoints2]))
                             img1.set_data(v_out_1.reshape([npoints2, npoints1]))
                             img1.set_clim(np.amin(v_out_1), np.amax(v_out_1))

                             #img2.set_data(v_out_2.reshape([npoints1, npoints2]))
                             img2.set_data(v_out_2.reshape([npoints2, npoints1]))
                             img2.set_clim(np.amin(v_out_2), np.amax(v_out_2))


                             fig1.canvas.draw()
                             plt.show(block=False)
                             fig1.canvas.flush_events()

                             fig2.canvas.draw()
                             plt.show(block=False)
                             fig2.canvas.flush_events()

                         else:
                            pass
                 V_out_all_1.append(v_out_1)
                 V_out_all_2.append(v_out_2)

        return_value = {"v_applied": [V_x.tolist(), V_y.tolist()], "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist(), "v_out2": np.mean(np.array(V_out_all_2),axis=0).tolist()}

    elif lockins == lockin_configs[5] or lockins == lockin_configs[6] or lockins == lockin_configs[7]:
        idx_1 = list(lockins)[0]-1
        V_out_all_1 = []
        v_out_1 = np.ones((npoints1,npoints2)).flatten()
        if plot == True:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(111)
            for i in range(n_fr):
                 v_out_1 = np.ones((npoints1,npoints2)).flatten()
                 for j in range(len(V_x_f)):
                     if j == 0:
                         dac_server = DacDriverSerialServer()
                         set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                         set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                         dac_server.close()
                         v_meas_1 = mflis[idx_1].get_sample_r()
                         v_out_1  = v_meas_1*v_out_1
                         V_out1 =  v_out_1.reshape([npoints1, npoints2])
                         img1 = ax1.imshow(V_out1, extent=[start_value1,end_value1,start_value2,end_value2])
                         ax1.set_xlabel(parameter1+" gate voltage [V]")
                         ax1.set_ylabel(parameter2+" gate voltage [V]")
                         fig1.canvas.draw()
                         cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                         cbar1.set_label('Demodulated voltage from lock-in 1 [V]', rotation=270, labelpad=30)
                         plt.show(block=False)

                         if i>0:
                             cbar1.remove()
                             cbar1 = fig1.colorbar(img1, ax=ax1, extend='both')
                         else:
                             pass
                     else:
                         if j%npoints1 == 0:
                             pass
                             dac_server = DacDriverSerialServer()
                             set_val(parameter1, V_x_f[j], channel_mapping, dac_server)
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         else:
                             pass
                             dac_server = DacDriverSerialServer()
                             set_val(parameter2, V_y_f[j], channel_mapping, dac_server)
                             dac_server.close()

                         v_meas_1 = mflis[idx_1].get_sample_r()
                         v_out_1[j] = v_meas_1
                         if j%n_r == 0:
                             img1.set_data(v_out_1.reshape([npoints1, npoints2]))
                             img1.set_clim(np.amin(v_out_1), np.amax(v_out_1))
                             fig1.canvas.draw()
                             plt.show(block=False)
                             fig1.canvas.flush_events()
                         else:
                            pass
                 V_out_all_1.append(v_out_1)

        return_value = {"v_applied": [V_x.tolist(), V_y.tolist()], "v_out1": np.mean(np.array(V_out_all_1),axis=0).tolist()}

    else:
        pass
    return return_value
