from silospin.drivers.set_val import *
from silospin.drivers.homedac_box import DacDriverSerialServer
from silospin.drivers.zi_mfli_driver import MfliDriverChargeStability
from silospin.experiment.setup_experiment_helpers import unpickle_qubit_parameters

import numpy as np
import matplotlib.pyplot as plt

def do1DSweep(parameter, start_value, end_value, npoints, n_r = 10, n_fr = 1, plot = True, lockins = {1,2,3}, filter_tc=10e-3, dac_mapping_file_path = 'C:\\Users\\Sigillito Lab\\Desktop\\experimental_workspaces\\quantum_dot_workspace_bluefors1\\experiment_parameters\\bluefors1_dac.pickle'):
    dac_server = DacDriverSerialServer()
    mflis = {0: MfliDriverChargeStability(dev_id = "dev5759", timeconstant=filter_tc), 1: MfliDriverChargeStability(dev_id = "dev5761", timeconstant=filter_tc), 2: MfliDriverChargeStability(dev_id = "dev6573", timeconstant=filter_tc)}
    gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS", "Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    lockin_configs = {1: {1,2,3}, 2: {1,2}, 3: {2,3}, 4: {1}, 5: {2}, 6: {3}}
    dac_dict = unpickle_qubit_parameters(dac_mapping_file_path)
    channel_mapping = dac_dict["channel_mapping"]

    # if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
    #     v_in_arrays = []
    #     for i in range(len(start_value)):
    #         v_in_arrays.append(np.linspace(start_value[i][1], end_value[i][1], npoints))
    # elif parameter in gates or parameter == "channel_voltage":
    #     v_in_array = np.linspace(start_value, end_value, npoints)
    # else:
    #     pass
    v_in_array = np.linspace(start_value, end_value, npoints)

    if lockins == lockin_configs[1]:
        V_out_all_1 = []
        V_out_all_2 = []
        V_out_all_3 = []
        if plot == True:
            fig_1 = plt.figure()
            ax_1 = fig_1.add_subplot(111)
            fig_2 = plt.figure()
            ax_2 = fig_2.add_subplot(111)
            fig_3 = plt.figure()
            ax_3 = fig_2.add_subplot(111)

            for i in range(n_fr):
                V_out_1 = []
                V_out_2 = []
                V_out_3 = []
                for j in range(npoints):
                    if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
                        pass
                        # for k in range(len(v_in_arrays)):
                        #     ## For case where a set of voltage ranges per channel is provided
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())

                        if j%n_r == 0:
                            ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
                            ax_1.set_xlabel('Applied barrier voltage [V]')
                            ax_1.set_ylabel('Measured output on lock-in 1 [V]')
                            fig_1.canvas.draw()

                            ax_2.plot(v_in_array[0:len(V_out_2)], V_out_2)
                            ax_2.set_xlabel('Applied barrier voltage [V]')
                            ax_2.set_ylabel('Measured output on lock-in 2 [V]')
                            fig_2.canvas.draw()

                            ax_3.plot(v_in_array[0:len(V_out_3)], V_out_3)
                            ax_3.set_xlabel('Applied barrier voltage [V]')
                            ax_3.set_ylabel('Measured output on lock-in 3 [V]')
                            fig_3.canvas.draw()
                            plt.show(block=False)
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
                        # for k in range(len(v_in_arrays)):
                        #     ## For case where a set of voltage ranges per channel is provided
                    else:
                        set_val(parameter, v_in_array[j], channel_mapping, dac_server)
                        V_out_1.append(mflis[0].get_sample_r())
                        V_out_2.append(mflis[1].get_sample_r())
                        V_out_3.append(mflis[2].get_sample_r())
                V_out_all_1.append(V_out_1)
                V_out_all_2.append(V_out_2)
                V_out_all_3.append(V_out_3)
        return_value = (v_in_array, np.mean(np.array(V_out_all_1),axis=0), np.mean(np.array(V_out_all_2),axis=0), np.mean(np.array(V_out_all_3),axis=0))

    # elif lockins in {lockin_configs[2], lockin_configs[3]}:
    #     V_out_all_1 = []
    #     V_out_all_2 = []
    #     idx_1 = list(lockins)[0]
    #     idx_2 = list(lockins)[1]
    #     if plot == True:
    #         fig_1 = plt.figure()
    #         ax_1 = fig_1.add_subplot(111)
    #         fig_2 = plt.figure()
    #         ax_2 = fig_2.add_subplot(111)
    #         for i in range(n_fr):
    #             V_out_1 = []
    #             V_out_2 = []
    #             for j in range(npoints):
    #                 if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
    #                     pass
    #                     # for k in range(len(v_in_arrays)):
    #                     #     ## For case where a set of voltage ranges per channel is provided
    #                 else:
    #                     set_val(parameter, v_in_array[j], channel_mapping, dac_server)
    #                     V_out_1.append(self._mflis[idx_1].get_sample_r())
    #                     V_out_2.append(self._mflis[idx_2].get_sample_r())
    #                     if j%n_r == 0:
    #                         ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
    #                         ax_1.set_xlabel('Applied barrier voltage [V]')
    #                         ax_1.set_ylabel('Measured output on lock-in 1 [V]')
    #                         fig_1.canvas.draw()
    #                         ax_2.plot(v_in_array[0:len(V_out_2)], V_out_2)
    #                         ax_2.set_xlabel('Applied barrier voltage [V]')
    #                         ax_2.set_ylabel('Measured output on lock-in 2 [V]')
    #                         fig_2.canvas.draw()
    #                         plt.show(block=False)
    #             V_out_all_1.append(V_out_1)
    #             V_out_all_2.append(V_out_2)
    #
    #     else:
    #         for i in range(n_fr):
    #             V_out_1 = []
    #             V_out_2 = []
    #             for j in range(npoints):
    #                 if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
    #                     pass
    #                     # for k in range(len(v_in_arrays)):
    #                     #     ## For case where a set of voltage ranges per channel is provided
    #                 else:
    #                     set_val(parameter, v_in_array[j], channel_mapping, dac_server)
    #                     V_out_1.append(self._mflis[idx_1].get_sample_r())
    #                     V_out_2.append(self._mflis[idx_2].get_sample_r())
    #             V_out_all_1.append(V_out_1)
    #             V_out_all_2.append(V_out_2)
    #     return_value = (v_in_array, np.mean(np.array(V_out_all_1),axis=0), np.mean(np.array(V_out_all_2),axis=0))

    # elif lockins in {lockin_configs[4], lockin_configs[5], lockin_configs[6]}:
    #     V_out_all_1 = []
    #     idx_1 = list(lockins)[0]
    #     if plot == True:
    #         fig_1 = plt.figure()
    #         ax_1 = fig_1.add_subplot(111)
    #         for i in range(n_fr):
    #             V_out_1 = []
    #             for j in range(npoints):
    #                 if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
    #                     pass
    #                     # for k in range(len(v_in_arrays)):
    #                     #     ## For case where a set of voltage ranges per channel is provided
    #                 else:
    #                     set_val(parameter, v_in_array[j], channel_mapping, dac_server)
    #                     V_out_1.append(self._mflis[idx_1].get_sample_r())
    #
    #                     if j%n_r == 0:
    #                         ax_1.plot(v_in_array[0:len(V_out_1)], V_out_1)
    #                         ax_1.set_xlabel('Applied barrier voltage [V]')
    #                         ax_1.set_ylabel('Measured output on lock-in 1 [V]')
    #                         fig_1.canvas.draw()
    #                         plt.show(block=False)
    #             V_out_all_1.append(V_out_1)
    #     else:
    #         for i in range(n_fr):
    #             V_out_1 = []
    #             for j in range(npoints):
    #                 if parameter == "channel_voltage_set" or parameter == "gates_voltages_set":
    #                     pass
    #                     # for k in range(len(v_in_arrays)):
    #                     #     ## For case where a set of voltage ranges per channel is provided
    #                 else:
    #                     set_val(parameter, v_in_array[j], channel_mapping, dac_server)
    #                     V_out_1.append(self._mflis[idx_1].get_sample_r())
    #             V_out_all_1.append(V_out_1)
    #     return_value = (v_in_array, np.mean(np.array(V_out_all_1),axis=0), np.mean(np.array(V_out_all_2),axis=0))
    # else:
    #     pass
    return return_value

#def do2DSweep(parameter1, start_value1, end_value1, npoints1, parameter2, start_value2, end_value2, npoints2):
