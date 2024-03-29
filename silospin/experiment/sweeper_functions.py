from silospin.drivers.set_val import *
from silospin.drivers.homedac_box import DacDriverSerialServer
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability, MfliDriver, MfliScopeModulePoint
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters, pickle_charge_data

import itertools
from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt

def do1DSweep(parameter, start_value, end_value, npoints, n_r = 10, n_fr = 1, plot = True, lockin_config = [1,2], lockins = {1: 'dev5759', 2: 'dev5761'}, dac_settings = {1: 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac1.pickle', 2: 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac2.pickle'}, filter_tc=10e-3, demod_freq =0, save_path=None):
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

    itr = 1
    lockin_drivers = {}
    for idx in range(len(lockins)):
        lockin_drivers[itr] = MfliDriverChargeStability(dev_id = lockins[itr], timeconstant=filter_tc, demod_freq=demod_freq, sig_path= f"/{lockins[itr]}/demods/0/sample")
        itr += 1

    dac_server = DacDriverSerialServer()
    dac_parameters = {}
    for idx in dac_settings:
        dac_dict = unpickle_qubit_parameters(dac_settings[idx])
        dac_parameters[idx] = dac_dict

    v_in_array = np.linspace(start_value, end_value, npoints)

    V_out_average = {}
    for idx in lockin_config:
        V_out_average[idx] = []

    if plot == True:
        fig_str = ''
        plot_0 = ''
        plot_1 = ''
        for idx in lockin_config:
            fig_str += f'fig{idx} = plt.figure()\nax{idx}=fig{idx}.add_subplot(111)\n'
            plot_0 += f'line{idx},=ax{idx}.plot(v_in_array, np.zeros(len(v_in_array)))\nax{idx}.set_xlabel("Applied voltage [V]")\nax{idx}.set_ylabel("Measured output on lock-in {idx} [V]")\nfig{idx}.canvas.draw()\nax{idx}background = fig{idx}.canvas.copy_from_bbox(ax{idx}.bbox)\nplt.show(block=False)\n'
            plot_1 += f'line{idx}.set_data(v_in_array[0:len(V_out_lockins[{idx}])], V_out_lockins[{idx}])\nfig{idx}.canvas.draw()\nfig{idx}.canvas.flush_events()\nax{idx}.set_ylim(np.amin(V_out_lockins[{idx}]), np.amax(V_out_lockins[{idx}]))\n'
        exec(fig_str+plot_0)

        for i in range(n_fr):
            set_val(parameter, v_in_array[0], dac_parameters, dac_server)
            V_out_lockins = {}
            for idx in lockin_config:
                V_out_lockins[idx] = []
            for j in range(npoints):
                set_val(parameter, v_in_array[j], dac_parameters, dac_server)
                for idx in lockin_config:
                    V_out_lockins[idx].append(lockin_drivers[idx].get_sample_r())
                if j%n_r == 0:
                    exec(plot_1)
                else:
                    pass
            for idx in lockin_config:
                V_out_average[idx].append(V_out_lockins[idx])
        return_value = {}
        return_value["v_applied"] = v_in_array.tolist()
        for idx in lockin_config:
            return_value[f'v_out{idx}'] =  np.mean(np.array(V_out_average[idx]),axis=0)
    else:
        for i in range(n_fr):
            V_out_lockins = {}
            for idx in lockin_config:
                V_out_lockins[idx] = []
            for j in range(npoints):
                dac_server = DacDriverSerialServer()
                set_val(parameter, v_in_array[j], dac_parameters, dac_server)
                for idx in lockin_config:
                    V_out_lockins[idx].append(lockin_drivers[idx].get_sample_r())

            for idx in lockin_config:
                V_out_average[idx].append(V_out_lockins[idx])

        return_value = {}
        return_value["v_applied"] = v_in_array.tolist()
        for idx in lockin_config:
            return_value[f'v_out{idx}'] =  np.mean(np.array(V_out_average[idx]),axis=0)
    if save_path:
        pickle_charge_data(return_value, save_path)
    else:
        pass

    return return_value

def do2DSweep(parameter1, start_value1, end_value1, npoints1, parameter2, start_value2, end_value2, npoints2, n_r = 10, n_fr = 1, plot = True, lockin_config = [1,2], lockins = {1: 'dev5759', 2: 'dev5761'},  dac_settings = {1: 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac1.pickle', 2: 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac2.pickle'}, filter_tc=10e-3, demod_freq = 0, save_path=None):
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
    itr = 1
    lockin_drivers = {}
    for idx in range(len(lockins)):
        lockin_drivers[itr] = MfliDriverChargeStability(dev_id = lockins[itr], timeconstant=filter_tc, demod_freq=demod_freq, sig_path= f"/{lockins[itr]}/demods/0/sample")
        itr += 1

    ##Make connection to DAC server
    dac_server = DacDriverSerialServer()
    dac_parameters = {}
    for idx in dac_settings:
        dac_dict = unpickle_qubit_parameters(dac_settings[idx])
        dac_parameters[idx] = dac_dict

    V_out_average = {}
    for idx in lockin_config:
        V_out_average[idx] = []

    V_out_lockins = {}
    for idx in lockin_config:
        V_out_lockins[idx] = np.ones((npoints1,npoints2)).flatten()

    v_x = np.linspace(start_value1, end_value1, npoints1)
    v_y = np.linspace(start_value2, end_value2, npoints2)
    V_x, V_y = np.meshgrid(v_x, v_y)
    V_x_f = V_x.flatten()
    V_y_f = V_y.flatten()

    if plot == True:
        fig_str = ''
        plot_0 = ''
        plot_1 = ''
        plot_2 = ''
        plot_3 = ''
        for idx in lockin_config:
            fig_str += f'fig{idx} = plt.figure()\nax{idx}=fig{idx}.add_subplot(111)\n'
            plot_0 += f'img{idx} = ax{idx}.imshow(V_out_lockins[{idx}].reshape([npoints1, npoints2]).T, extent=[start_value1,end_value1,end_value2,start_value2])\nax{idx}.set_xlabel(parameter1+" gate voltage [V]")\nax{idx}.set_ylabel(parameter2+" gate voltage [V]")\nfig{idx}.canvas.draw()\ncbar{idx} = fig{idx}.colorbar(img{idx}, ax=ax{idx}, extend="both")\ncbar{idx}.set_label("Demodulated voltage from lock-in {idx} [V]", rotation=270, labelpad=30)\nplt.show(block=False)\n\n'
            plot_1 += f'cbar{idx}.remove()\ncbar{idx} = fig{idx}.colorbar(img{idx}, ax=ax{idx}, extend="both")\n'
            plot_2 += f'img{idx}.set_data(V_out_lockins[{idx}].reshape([npoints1, npoints2]).T)\nimg{idx}.set_clim(np.amin(V_out_lockins[{idx}]), np.amax(V_out_lockins[{idx}]))\n\n'
            plot_3 += f'fig{idx}.canvas.draw()\nplt.show(block=False)\nfig{idx}.canvas.flush_events()\n\n'

        exec(fig_str)
        for i in range(n_fr):
            set_val(parameter1, V_x_f[0], dac_parameters, dac_server)
            set_val(parameter2, V_y_f[0], dac_parameters, dac_server)
            V_out_lockins = {}
            for idx in lockin_config:
                V_out_lockins[idx] = np.ones((npoints1,npoints2)).flatten()

            for j in range(len(V_x_f)):
                if j == 0:
                    set_val(parameter1, V_x_f[j], dac_parameters, dac_server)
                    set_val(parameter2, V_y_f[j], dac_parameters, dac_server)

                    for idx in lockin_config:
                        v_meas = lockin_drivers[idx].get_sample_r()
                        V_out_lockins[idx] = v_meas*V_out_lockins[idx]

                    exec(plot_0)
                    if i > 0:
                        exec(plot_1)
                    else:
                        pass
                else:
                    set_val(parameter1, V_x_f[j], dac_parameters, dac_server)
                    set_val(parameter2, V_y_f[j], dac_parameters, dac_server)
                    for idx in lockin_config:
                        V_out_lockins[idx][j] = lockin_drivers[idx].get_sample_r()

                    if j%n_r == 0:
                        exec(plot_2)
                        exec(plot_3)
                    else:
                        pass
                    for idx in lockin_config:
                        V_out_average[idx].append(V_out_lockins[idx])
    else:
        for i in range(n_fr):
            set_val(parameter1, V_x_f[0], dac_parameters, dac_server)
            set_val(parameter2, V_y_f[0], dac_parameters, dac_server)
            V_out_lockins = {}
            for idx in lockin_config:
                V_out_lockins[idx] = np.ones((npoints1,npoints2)).flatten()

            for j in range(len(V_x_f)):
                if j == 0:
                    set_val(parameter1, V_x_f[j], dac_parameters, dac_server)
                    set_val(parameter2, V_y_f[j], dac_parameters, dac_server)

                    for idx in lockin_config:
                        v_meas = lockin_drivers[idx].get_sample_r()
                        V_out_lockins[idx] = v_meas*V_out_lockins[idx]
                else:
                    set_val(parameter1, V_x_f[j], dac_parameters, dac_server)
                    set_val(parameter2, V_y_f[j], dac_parameters, dac_server)
                    for idx in lockin_config:
                        V_out_lockins[idx][j] = lockin_drivers[idx].get_sample_r()
                    for idx in lockin_config:
                        V_out_average[idx].append(V_out_lockins[idx])

    return_value = {}
    return_value["V_x_in"] = V_x_f
    return_value["V_y_in"] = V_y_f
    for idx in lockin_config:
        return_value[f'v_out{idx}'] =  np.mean(np.array(V_out_average[idx]),axis=0)
    if save_path:
        pickle_charge_data(return_value, save_path)
    else:
        pass
    return return_value
