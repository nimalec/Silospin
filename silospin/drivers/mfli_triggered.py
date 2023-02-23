import zhinst
import zhinst.utils
from zhinst import ziPython
import zhinst.toolkit as tk
from zhinst.ziPython import ziListEnum
import matplotlib.pyplot as plt
import numpy as np
import time
from silospin.drivers.driver_helpers import read_data_update_plot, read_data


class MfliDriver:
    def __init__(self, device_id, server_host = "localhost", server_port = 8004, api_level = 6, interface = '1GbE'):
        """
         Constructor for MFLI driver.
           Returns
           -------
           None.
        """
        (daq, device, _) = zhinst.utils.create_api_session(device_id, api_level, server_host=server_host, server_port=server_port)

        daq.connectDevice(device_id, interface)


        self._connection_settings = {"mfli_id" : device, "server_host" : server_host , "server_port" : server_port, "api_level" : api_level,
                                     "connection_status" : False, "interface": '1GbE'}

        self._daq = daq
        self._device = device
        zhinst.utils.api_server_version_check(self._daq)
        self._daq_module = self._daq.dataAcquisitionModule()
        self._scope_module = self._daq.scopeModule()


    def get_all_mfli_settings(self):
        self._demods_settings = {"enable": self._daq.getInt(f"/{self._device}/demods/0/enable"), "adcselect": self._daq.getInt(f"/{self._device}/demods/0/adcselect") ,
        "freq": self._daq.getDouble(f"/{self._device}/demods/0/freq"), "order": self._daq.getInt(f"/{self._device}/demods/0/order"),
        "oscselect": self._daq.getInt(f"/{self._device}/demods/0/oscselect"), "phaseshift": self._daq.getDouble(f"/{self._device}/demods/0/phaseshift"),
        "phaseadjust":  self._daq.getInt(f"/{self._device}/demods/0/phaseadjust"), "rate" : self._daq.getDouble(f"/{self._device}/demods/0/rate"),
        "sinc": self._daq.getInt(f"/{self._device}/demods/0/sinc"), "timeconstant": self._daq.getDouble(f"/{self._device}/demods/0/timeconstant")
        , "trigger": self._daq.getInt(f"/{self._device}/demods/0/trigger")}
        self._sigins_settings = {"ac": self._daq.getInt(f"/{self._device}/sigins/0/ac"), "autorange": self._daq.getInt(f"/{self._device}/sigins/0/autorange")
        , "diff": self._daq.getInt(f"/{self._device}/sigins/0/diff"),
        "float": self._daq.getInt(f"/{self._device}/sigins/0/float"), "imp50": self._daq.getInt(f"/{self._device}/sigins/0/imp50"),
         "max": self._daq.getDouble(f"/{self._device}/sigins/0/max"), "min": self._daq.getDouble(f"/{self._device}/sigins/0/min"),
        "on": self._daq.getInt(f"/{self._device}/sigins/0/on"), "range": self._daq.getInt(f"/{self._device}/sigins/0/range"), "scaling": self._daq.getInt(f"/{self._device}/sigins/0/scaling")}
        self._sigouts_settings = {
        "autorange": self._daq.getInt(f"/{self._device}/sigouts/0/autorange"),
        "diff": self._daq.getInt(f"/{self._device}/sigouts/0/diff"),
        "imp50": self._daq.getInt(f"/{self._device}/sigouts/0/imp50"),
        "offset": self._daq.getDouble(f"/{self._device}/sigouts/0/offset"),
        "on": self._daq.getDouble(f"/{self._device}/sigouts/0/on"),
        "over": self._daq.getDouble(f"/{self._device}/sigouts/0/over") ,
        "range": self._daq.getDouble(f"/{self._device}/sigouts/0/range")}
        self._currins_settings = {"autorange": self._daq.getInt(f"/{self._device}/currins/0/autorange"), "float": self._daq.getInt(f"/{self._device}/currins/0/float"), "max": self._daq.getDouble(f"/{self._device}/currins/0/max"), "min": self._daq.getDouble(f"/{self._device}/currins/0/min"),
          "on": self._daq.getInt(f"/{self._device}/currins/0/on") , "range": self._daq.getInt(f"/{self._device}/currins/0/range"), "scaling": self._daq.getDouble(f"/{self._device}/currins/0/scaling")}
        self._oscs_settings = {"freq": self._daq.getDouble(f"/{self._device}/oscs/0/freq")}
        return {"connection": self._connection_settings, "demods": self._demods_settings, "sigins": self._sigins_settings, "sigouts": self._sigouts_settings, "currins": self._currins_settings , "oscs": self._oscs_settings}

    def get_osc_freq(self):
        return self._daq.getDouble(f"/{self._device}/oscs/0/freq")

    def set_osc_freq(self, value):
        self._daq.set(f"/{self._device}/oscs/0/freq", value)

    def get_demods_settings(self, key):
        settings_1 = {"enable", "adcselect","bypass", "harmonic", "order", "oscselect", "phaseadjust",  "sinc", "trigger"}
        settings_2 = {"freq", "phaseshift", "rate", "timeconstant", "rate"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/demods/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/demods/0/"+key)
        return value

    def set_demods_settings(self, key, value):
        settings_1 = {"enable", "adcselect","bypass", "harmonic", "order", "oscselect", "phaseadjust",  "sinc", "trigger"}
        settings_2 = {"freq", "phaseshift", "rate", "timeconstant", "rate"}
        if key in settings_1:
            self._daq.set(f"/{self._device}/demods/0/"+key, value)
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/demods/0/"+key)
        elif key in settings_2:
            self._daq.set(f"/{self._device}/demods/0/"+key, value)
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/demods/0/"+key)

    def get_sigins_settings(self, key):
        settings_1 = {"ac", "autorange", "diff", "float","imp50", "on", "range"}
        settings_2 = {"max", "min"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/sigins/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/sigins/0/"+key)
        return value

    def set_sigins_settings(self, key, value):
        settings_1 = {"ac", "autorange", "diff", "float","imp50", "on", "range"}
        settings_2 = {"max", "min"}
        if key in settings_1:
            self._daq.set(f"/{self._device}/sigins/0/"+key, value)
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/sigins/0/"+key)
        elif key in settings_2:
            self._daq.set(f"/{self._device}/sigins/0/"+key, value)
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/sigins/0/"+key)

    def get_sigouts_settings(self, key):
        settings_1 = {"add","autorange", "diff", "imp50", "on", "over", "range"}
        settings_2 = {"offset"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/sigouts/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/sigouts/0/"+key)
        return value

    def set_sigouts_settings(self, key, value):
        settings_1 = {"add","autorange", "diff", "imp50", "on", "over", "range"}
        settings_2 = {"offset"}
        if key in settings_1:
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/sigouts/0/"+key)
            self._daq.set(f"/{self._device}/sigouts/0/"+key, value)
        elif key in settings_2:
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/sigouts/0/"+key)
            self._daq.set(f"/{self._device}/sigouts/0/"+key, value)

    def get_currins_settings(self, key):
        settings_1 = {"autorange", "float", "range"}
        settings_2 = {"max", "min", "scaling"}
        if key in settings_1:
            value = self._daq.getInt(f"/{self._device}/currins/0/"+key)
        elif key in settings_2:
            value = self._daq.getDouble(f"/{self._device}/currins/0/"+key)
        return value

    def set_currins_settings(self, key, value):
        settings_1 = {"autorange","float","range"}
        settings_2 = {"max","min","scaling"}
        if key in settings_1:
            self._demods_settings[key] = self._daq.getInt(f"/{self._device}/currins/0/"+key)
            self._daq.set(f"/{self._device}/currins/0/"+key, value)
        elif key in settings_2:
            self._demods_settings[key] = self._daq.getDouble(f"/{self._device}/currins/0/"+key)
            self._daq.set(f"/{self._device}/currins/0/"+key, value)

    # def enable_data_transfer(self):
    #      self._daq.set(f"/{self._device}/demods/0/enable", 1)
    #      self._demod_settings["enable"] = self._daq.getInt(f"/{self._device}/demods/0/enable")
    #      self._scope_module = self._daq.scopeModule()



class MfliDaqModule:
    def __init__(self, mfli_driver):
        self._mfli = mfli_driver
        self._daq  = self._mfli._daq
        self._dev_id = self._mfli._connection_settings["mfli_id"]
        self._daq_module = self._daq.dataAcquisitionModule()

        self._signal_paths = set()
        self._data = []

        self._counter = 0


    def continuous_data_acquisition_time_domain(self, duration, n_traces = 100,  sample_rate=53570, sig_port  = 'Aux_in_1',  rows = 1 , plot_on = True):
        ##prepare daq module for cont. data acquisition_time

        sig_source = { 'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'   }

        sample_data = []


        #enable data transfer (sampling rate)
        self._daq.setInt(f'/{self._dev_id}/demods/0/enable', 1)
        self._daq.setInt(f'/{self._dev_id}/demods/0/trigger', 0)   #set Trigger to the continuous mode
        self._daq.setDouble(f'/{self._dev_id}/demods/0/rate', sample_rate)


        time.sleep(0.2)  #giving the DAQ enough time to set the sampling/data transfer rate
        print(self._daq.getDouble(f'/{self._dev_id}/demods/0/rate'))  #only for testing

        self._daq_module.set("device", self._dev_id)
        # Specify continuous acquisition (type=0).
        self._daq_module.set("type", 0)


        self._daq_module.set('grid/mode', 4)  #exact on-grid mode (no interpolation)

        # 'grid/cols'
       # '/module/c0p1t8p1cf/dataAcquisitionModule/duration'

        columns = np.ceil(duration*sample_rate)
        self._daq_module.set('grid/cols', columns)
        self._daq_module.set('grid/rows', rows)   # setting the # of rows here

        time.sleep(0.2)  #giving the DAQ enough time to set the sampling/data transfer rate

        columns = self._daq_module.getInt('grid/cols')  #replace the calculated columns with the accepted val

        #im just repeating this to make sure that the correct duration is set for the DAQ module. Without this, even with columns and sample rate set correctly
        #the duration read back from the DAQ module is erroneous

        self._daq_module.set('endless', 1)
        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0
        self._daq_module.execute()
        self._daq_module.finish()
        self._daq_module.unsubscribe('*')

        self._daq_module.set('endless', 1)
        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0


        time.sleep(0.2)
        duration = self._daq_module.getDouble("duration")


        print('sampling rate', self._daq.getDouble(f'/{self._dev_id}/demods/0/rate'), 'columns', columns, 'rows', self._daq_module.getInt("grid/rows"),
              'duration', self._daq_module.getDouble("duration") )  #only for testing



        time_axis = np.linspace(0, duration,  columns)   #preparing x axis
        v_measured = np.zeros(columns)

        fig = plt.figure(self._counter)
        self._counter += 1

        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('time in sec')
        ax1.set_ylabel('volts')

        line, = ax1.plot(time_axis, v_measured, lw=1)  #lw is the thickness of the plot


        #data acquisition starts here
        self._daq_module.execute()

        t_start = time.time()
        while len(sample_data) < n_traces:

            #depending on the parameters, this could return multiple traces or no traces
            data_read = self._daq_module.read(True)

            if sig_source[sig_port].lower() in data_read.keys():

                line.set_data(time_axis, data_read[sig_source[sig_port].lower()][0]['value'][0])   #updating the time trace plot with just the first array from 'read()'
                ax1.set_ylim(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5,
                                 np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5)

                fig.canvas.draw()
                fig.canvas.flush_events()


                for each in data_read[sig_source[sig_port].lower()]:

                    # print(len(data_read['/dev6541/demods/0/sample.auxin0']))  #based on this test, it seems like setting rows to be more than 1 results in
                    # 'read()' only collecting the first trace in every #num of rows traces

                    sample_data.append(each)

        #there could be some leftover data that was not collected from the last 'read()' call but I won't append the leftover data to 'sample_data' array
        #since this is in the continuous mode.


        #clearing the trigger event count and unsubscribing the data stream after the measurement run is over.
        self._daq_module.finish()
        self._daq_module.unsubscribe('*')
        self._daq_module.set('endless', 0)


        t_final = time.time()
        print(t_final - t_start, 'duration')

        #adding 2d plot in case you want it AFTER data collection.

        if plot_on == True:

            x_axis_length = int(columns)
            y_axis_length = int(len(sample_data))

            data_array = np.ones(shape=(y_axis_length, x_axis_length)   )

            x_array = np.linspace(0, x_axis_length, x_axis_length)
            y_array = np.linspace(0, y_axis_length, y_axis_length)

            centers = [0, duration,  0, y_axis_length]

            dx, = np.diff(centers[:2])/(x_axis_length)
            dy, = np.diff(centers[2:])/(y_axis_length)

            extent = [centers[0]-dx/2, centers[1]+dx/2, centers[2]+dy/2, centers[3]-dy/2]

            plt.show(block=False)
            fig = plt.figure(self._counter)
            self._counter += 1

            plt.xlabel('time in sec')
            plt.ylabel('num_traces')

            ax = plt.imshow(data_array, cmap='Greens', interpolation='None',clim=[0, 1], origin='lower',  extent=extent, aspect='auto')

            t_start = time.time()
            for each_y in range(y_axis_length):

                data_array[each_y]= sample_data[each_y]['value'][0]

            ax.set_array(data_array)
            fig.canvas.draw()
            fig.canvas.flush_events()
            t_final = time.time()


        print(t_final - t_start, 'duration')  #only for testing

        return sample_data, time_axis

    def set_triggered_data_acquisition_time_domain(self, duration, sample_rate=53570, rows = 1 ,sig_port  = 'Aux_in_1' , plot_on = True):
        #for now, available input signals are only 'Demod_R' and 'Aux_in_1'
        sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        self._daq_module.set("device", self._dev_id)

        self._daq.setInt(f'/{self._dev_id}/demods/0/enable', 1)
        self._daq.setInt(f'/{self._dev_id}/demods/0/trigger', 0)
        self._daq.setDouble(f'/{self._dev_id}/demods/0/rate', sample_rate)
        time.sleep(0.2)

        self._daq_module.set('type', 6)
        self._daq_module.set('triggernode', f'/{self._dev_id}/demods/0/sample.TrigIn2')
        self._daq_module.set('clearhistory', 1)
        self._daq_module.set('clearhistory', 1)
        self._daq_module.set('bandwidth', 0)
        self._daq_module.set('edge', 1)
        columns = np.ceil(duration*sample_rate)
        self._daq_module.set('grid/mode', 4)
        self._daq_module.set("grid/cols", columns)
        self._daq_module.set('grid/rows', rows)
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("holdoff/count", 0)
        self._daq_module.subscribe(sig_source[sig_port])
        time.sleep(0.8)
        columns = self._daq_module.getInt('grid/cols')

        self._daq_module.set('endless', 0)
        self._daq_module.subscribe(sig_source[sig_port])
        self._daq_module.execute()
        self._daq_module.finish()
        self._daq_module.unsubscribe('*')
        self._daq_module.subscribe(sig_source[sig_port])

        # self._daq_module.execute()
        # while not self._daq_module.finished():
        #     data_read = self._daq_module.read(True)
        #     if sig_source[sig_port].lower() in data_read.keys():
        #         line.set_data(time_axis, data_read[sig_source[sig_port].lower()][0]['value'][0])
        #         ax1.set_ylim(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5,
        #                           np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5)
        #         fig.canvas.draw()
        #         fig.canvas.flush_events()
        #         for each in data_read[sig_source[sig_port].lower()]:
        #             sample_data.append(each)
        # data_read = self._daq_module.read(True)
        # if sig_source[sig_port].lower() in data_read.keys():
        #     for each in data_read[sig_source[sig_port].lower()]:
        #         sample_data.append(each)
        # self._daq_module.finish()
        # self._daq_module.unsubscribe('*')
        # return sample_data, time_axis

    def set_triggered_data_acquisition_time_domain_v2(self, duration, sample_rate=53570, rows = 1 ,sig_port  = 'Aux_in_1'):
        sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        self._daq_module.set("device", self._dev_id)
        self._daq.setInt(f'/{self._dev_id}/demods/0/enable', 1)
        self._daq.setInt(f'/{self._dev_id}/demods/0/trigger', 0)   #set Trigger to the continuous mode
        self._daq.setDouble(f'/{self._dev_id}/demods/0/rate', sample_rate)
#        time.sleep(0.2)  #giving the DAQ enough time to set the sampling/data transfer rate

        # Specify triggered data acquisition (type=0).
        self._daq_module.set('type', 6)
        self._daq_module.set('triggernode', f'/{self._dev_id}/demods/0/sample.TrigIn2')
        self._daq_module.set('clearhistory', 1)   #not sure why history got cleared twice in the API log but I am simply copying what LabOne did.
        self._daq_module.set('clearhistory', 1)
        self._daq_module.set('bandwidth', 0)
        self._daq_module.set('edge', 1)   #trigger edge: positive

        columns = np.ceil(duration*sample_rate)

        self._daq_module.set('grid/mode', 4)  #exact on-grid mode (no interpolation)
        self._daq_module.set("count", 1)
        self._daq_module.set("grid/cols", columns)
        self._daq_module.set('grid/rows', rows)   # setting the # of rows here. we are going to set the default to be 1. this seems relevant when plotting traces on GUI.

        #We set the holdoff time to 0 s to ensure that no triggers are lost in between successive lines
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("holdoff/count", 0)  #num of skipped triggers until the next trigger is recorded again
        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0
        #time.sleep(0.8)  #giving the DAQ enough time to set the the parameters (columns, and num of traces before being read back out)
        #im just repeating this to make sure that the correct duration is set for the DAQ module. Without this, even with columns and sample rate set correctly
        #the duration read back from the DAQ module is erroneous
        # self._daq_module.set('endless', 0)
        # self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0
        # self._daq_module.execute()
        # self._daq_module.finish()
        # self._daq_module.unsubscribe('*')
        # self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0

        ## Execution
        # self._daq_module.execute()
        # while not self._daq_module.finished():
        #     data_read = self._daq_module.read(True)
        #     if sig_source[sig_port].lower() in data_read.keys():
        #         for each in data_read[sig_source[sig_port].lower()]:
        #             sample_data.append(each)
        # data_read = self._daq_module.read(True)
        # if sig_source[sig_port].lower() in data_read.keys():
        #     for each in data_read[sig_source[sig_port].lower()]:
        #         sample_data.append(each)
        # self._daq_module.finish()
        # self._daq_module.unsubscribe('*')

    def set_triggered_data_acquisition_time_domain_v3(self, duration, sample_rate, rows=1, sig_port  = 'Aux_in_1'):
        self._daq_module.set("device", self._dev_id)
        self._daq.setDouble(f'/{self._dev_id}/demods/0/rate', sample_rate)
        self._daq.setInt(f'/{self._dev_id}/demods/0/trigger', 0)
        self._daq_module.set('type', 6)
        self._daq_module.set('triggernode', f'/{self._dev_id}/demods/0/sample.TrigIn2')
        self._daq_module.set('bandwidth', 0)
        self._daq_module.set('edge', 1)

        # columns = np.ceil(duration*sample_rate)
        # self._daq_module.set('grid/mode', 4)
        # self._daq_module.set("count", 1)
        # self._daq_module.set("grid/cols", columns)
        # self._daq_module.set('grid/rows', rows)
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("holdoff/count", 0)


        # sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        # self._daq_module.subscribe(sig_source[sig_port])

    def enable_triggered_data_acquisition_time_domain(self, duration, sample_rate, rows = 1 ,sig_port  = 'Aux_in_1'):
        #sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        self._daq.setInt(f'/{self._dev_id}/demods/0/enable', 1)
        self._daq_module.set('clearhistory', 1)
        self._daq_module.set('clearhistory', 1)

        columns = np.ceil(duration*sample_rate)
        self._daq_module.set("grid/cols", columns)
        self._daq_module.set('grid/rows', rows)
        self._daq_module.set("count", 1)

        sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        self._daq_module.subscribe(sig_source[sig_port])

        # sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}
        # self._daq_module.subscribe(sig_source[sig_port])

        # columns = np.ceil(duration*sample_rate)
        # self._daq_module.set('grid/mode', 4)
        # self._daq_module.set("count", 1)
        # self._daq_module.set("grid/cols", columns)
        # self._daq_module.set('grid/rows', rows)
        # self._daq_module.set("holdoff/time", 0)
        # self._daq_module.set("holdoff/count", 0)
        #self._daq_module.subscribe(sig_source[sig_port])

    def triggered_data_acquisition_time_domain(self, duration, n_traces = 100,  sample_rate=53570, rows = 1 ,sig_port  = 'Aux_in_1' , plot_on = True):

        #for now, available input signals are only 'Demod_R' and 'Aux_in_1'
        sig_source = {'Demod_R': f'/{self._dev_id}/demods/0/sample.R' , 'Aux_in_1': f'/{self._dev_id}/demods/0/sample.AuxIn0'}

        sample_data = []
        self._daq_module.set("device", self._dev_id)

        #enable data transfer (sampling rate)
        self._daq.setInt(f'/{self._dev_id}/demods/0/enable', 1)
        self._daq.setInt(f'/{self._dev_id}/demods/0/trigger', 0)   #set Trigger to the continuous mode
        self._daq.setDouble(f'/{self._dev_id}/demods/0/rate', sample_rate)
        time.sleep(0.2)  #giving the DAQ enough time to set the sampling/data transfer rate
        print(self._daq.getDouble(f'/{self._dev_id}/demods/0/rate'))  #only for testing


        # Specify triggered data acquisition (type=0).
        self._daq_module.set('type', 6)
        self._daq_module.set('triggernode', f'/{self._dev_id}/demods/0/sample.TrigIn2')
        self._daq_module.set('clearhistory', 1)   #not sure why history got cleared twice in the API log but I am simply copying what LabOne did.
        self._daq_module.set('clearhistory', 1)
        self._daq_module.set('bandwidth', 0)
        self._daq_module.set('edge', 1)   #trigger edge: positive

        columns = np.ceil(duration*sample_rate)

        self._daq_module.set('grid/mode', 4)  #exact on-grid mode (no interpolation)
        self._daq_module.set("count", n_traces)
        self._daq_module.set("grid/cols", columns)
        self._daq_module.set('grid/rows', rows)   # setting the # of rows here. we are going to set the default to be 1. this seems relevant when plotting traces on GUI.

        #We set the holdoff time to 0 s to ensure that no triggers are lost in between successive lines
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("holdoff/count", 0)  #num of skipped triggers until the next trigger is recorded again

        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0


        time.sleep(0.8)  #giving the DAQ enough time to set the the parameters (columns, and num of traces before being read back out)

        columns = self._daq_module.getInt('grid/cols')  #replace the calculated columns with the accepted val



        #im just repeating this to make sure that the correct duration is set for the DAQ module. Without this, even with columns and sample rate set correctly
        #the duration read back from the DAQ module is erroneous

        self._daq_module.set('endless', 0)
        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0
        self._daq_module.execute()
        self._daq_module.finish()
        self._daq_module.unsubscribe('*')


        # self._daq_module.set('endless', 0)
        self._daq_module.subscribe(sig_source[sig_port])  #assuming we are measuring from AuxIn0



        print('sampling rate', self._daq.getDouble(f'/{self._dev_id}/demods/0/rate'), 'columns', columns, 'rows', self._daq_module.getInt("grid/rows"),
              'duration', self._daq_module.getDouble("duration") )  #only for testing


        duration = self._daq_module.getDouble("duration")
        columns = self._daq_module.getInt('grid/cols')  #replace the calculated columns with the accepted val

        time_axis = np.linspace(0, duration,  columns)   #preparing x axis
        v_measured = np.zeros(columns)

        fig = plt.figure(self._counter)
        self._counter += 1


        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('time in sec')
        ax1.set_ylabel('volts')
        line, = ax1.plot(time_axis, v_measured, lw=1)  #lw is the thickness of the plot

        #data acquisition starts here
        self._daq_module.execute()

        t_start = time.time()
        while not self._daq_module.finished():

            # print('nm of triggered events', n_traces*self._daq_module.progress()[0] , 'is it finished?',self._daq_module.finished() )
            data_read = self._daq_module.read(True)


            if sig_source[sig_port].lower() in data_read.keys():

                #updating the 1D plot with only the first trace of the bundle recovered from each 'read()' call
                # print('what is this?', data_read.keys())


                line.set_data(time_axis, data_read[sig_source[sig_port].lower()][0]['value'][0])   #updating the time trace plot with just the first array from 'read()'
                ax1.set_ylim(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]) - abs(np.amin(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5,
                                  np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]) + abs(np.amax(data_read[sig_source[sig_port].lower()][0]['value'][0]))/5)

                fig.canvas.draw()
                fig.canvas.flush_events()

                for each in data_read[sig_source[sig_port].lower()]:
                    sample_data.append(each)
        t_final = time.time()
        print(t_final - t_start, 'duration')  #only for testing


        #in case there's leftover data, call the 'read' function again and append it to 'sample_data' array
        data_read = self._daq_module.read(True)
        if sig_source[sig_port].lower() in data_read.keys():
            for each in data_read[sig_source[sig_port].lower()]:
                sample_data.append(each)


        #clearing the trigger event count and unsubscribing the data stream after the measurement run is over.
        self._daq_module.finish()
        self._daq_module.unsubscribe('*')

        return sample_data, time_axis






    # def 2D_plot(self, sample_data, time_axis):

    #I used this function to confirm that if the trigger frequency is faster than the duration of each trace/burst, there will be overlap between the neighboring
    #time traces.
    def array_overlap_test(self, array_1, array_2):

        import collections
        # from collections import Counter


        a = array_1['value'][0]
        b = array_2['value'][0]

        a_multiset = collections.Counter(a)
        b_multiset = collections.Counter(b)

        overlap = list((a_multiset & b_multiset).elements())
        a_remainder = list((a_multiset - b_multiset).elements())
        b_remainder = list((b_multiset - a_multiset).elements())

        print (overlap, len(overlap))

    def data_2D_plot(self, sample_data, time_axis):

        x_axis_length = int(len(time_axis))
        y_axis_length = int(len(sample_data))

        data_array = np.ones(shape=(y_axis_length, x_axis_length)   )

        x_array = np.linspace(0, x_axis_length, x_axis_length)
        y_array = np.linspace(0, y_axis_length, y_axis_length)

        duration = time_axis[-1]

        centers = [0, duration,  0, y_axis_length]

        dx, = np.diff(centers[:2])/(x_axis_length)
        dy, = np.diff(centers[2:])/(y_axis_length)

        extent = [centers[0]-dx/2, centers[1]+dx/2, centers[2]+dy/2, centers[3]-dy/2]

        plt.show(block=False)
        fig = plt.figure(self._counter)
        self._counter += 1

        plt.xlabel('time in sec')
        plt.ylabel('triggerd_num')

        ax = plt.imshow(data_array, cmap='Greens', interpolation='None',clim=[0, 1], origin='lower',  extent=extent, aspect='auto')

        t_start = time.time()


        if type(sample_data[0]) == dict:  #this is for the data coming from the DAQ module
            for each_y in range(y_axis_length):

                data_array[each_y]= sample_data[each_y]['value'][0]

        else:
            for each_y in range(y_axis_length):      #this is for the data coming from the scope module

                data_array[each_y]= sample_data[each_y][0]['wave'][0]


        ax.set_array(data_array)
        fig.canvas.draw()
        fig.canvas.flush_events()
        t_final = time.time()


    def get_all_daq_settings(self):
        self._history_settings = {"clearhistory": self._daq_module.getInt("clearhistory") , "duration": self._daq_module.getDouble("duration")}

        self._trigger_settings = {"forcetrigger": self._daq_module.getInt("forcetrigger"), "bitmask": self._daq_module.getInt("bitmask"),
        "bandwidth": self._daq_module.getDouble("bandwidth"), "bits": self._daq_module.getInt("bits"), "count":  self._daq_module.getInt("count"),
        "delay": self._daq_module.getDouble("delay"), "edge": self._daq_module.getInt("edge"),
        "eventcountmode": self._daq_module.getInt("eventcount/mode"), "holdoffcount": self._daq_module.getInt("holdoff/count"),
         "holdofftime": self._daq_module.getDouble("holdoff/time"), "level": self._daq_module.getDouble("level"),
         "pulsemax": self._daq_module.getDouble("pulse/max"), "pulsemin": self._daq_module.getDouble("pulse/min"),
         "triggernode": self._daq_module.getString("triggernode"), "type": self._daq_module.getInt("type"), "triggered": self._daq_module.getInt("triggered")}

        self._grid_settings = {"cols": self._daq_module.getInt("grid/cols"), "direction": self._daq_module.getInt("grid/direction"),
        "mode": self._daq_module.getInt("grid/mode"),  "overwrite": self._daq_module.getInt("grid/overwrite"), "rowrepetitions": self._daq_module.getInt("grid/rowrepetition"), "rows": self._daq_module.getInt("grid/rows"),  "waterfall": self._daq_module.getInt("grid/waterfall")}

        self._fft_settings = {"spectrumautobw": self._daq_module.getInt("spectrum/autobandwidth"), "absolute": self._daq_module.getInt("fft/absolute"),
         "window": self._daq_module.getInt("fft/window"),  "spectrumenable": self._daq_module.getInt("spectrum/enable"),
         "spectrumoverlapped": self._daq_module.getInt("spectrum/overlapped"), "spectrumfrequencyspan": self._daq_module.getDouble("spectrum/frequencyspan")}
        return {"history": self._history_settings, "trigger": self._trigger_settings, "grid": self._grid_settings, "fft": self._fft_settings}

    def get_history_setting(self, key):
        if key == "clearhistory":
            self._history_settings[key] = self._daq_module.getInt("clearhistory")
        elif key == "duration":
            self._history_settings[key] = self._daq_module.getDouble("duration")
        else:
            pass
        return self._history_settings[key]

    def get_trigger_setting(self, key):
        setings_1 = {"forcetrigger", "bitmask" , "bits", "count",  "edge" , "type", "triggered"}
        setings_2 = {"bandwidth", "delay", "level"}
        if key in setings_1:
            self._trigger_settings[key] = self._daq_module.getInt(key)
        elif key in setings_2:
            self._trigger_settings[key] = self._daq_module.getDouble(key)
        elif key == "eventcountmode":
            self._trigger_settings[key] = self._daq_module.getInt("eventcount/mode")
        elif key == "holdoffcount":
            self._trigger_settings[key] = self._daq_module.getInt("holdoff/count")
        elif key == "holdofftime":
            self._trigger_settings[key] = self._daq_module.getDouble("holdoff/time")
        elif key == "pulsemax":
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/max")
        elif key == "pulsemin":
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/min")
        elif key == "triggernode":
            self._trigger_settings[key] = self._daq_module.getString("triggernode")
        else:
            pass
        return self._trigger_settings[key]

    def get_grid_setting(self, key):
        self._grid_settings[key] = self._daq_module.getInt("grid/"+key)
        return self._grid_settings[key]

    def get_osc_setting(self, key):
        self._grid_settings[key] = self._daq_module.getDouble("grid/"+key)

    def get_fft_setting(self, key):
        settings_1 = {"window", "absolute"}
        if key == "spectrumautobw":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/autobandwidth")
        elif key == "spectrumenable":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/enable")
        elif key == "spectrumoverlapped":
            self._fft_settings[key] = self._daq_module.getInt("spectrum/overlapped")
        elif key == "spectrumfrequencyspan":
            self._fft_settings[key] = self._daq_module.getDouble("spectrum/frequencyspan")
        elif key in settings_1:
            self._fft_settings[key] = self._daq_module.getInt("fft/"+key)
        else:
            pass
        return self._fft_settings[key]

    def set_history_setting(self, key, value):
        if key == "clearhistory":
            self._daq_module.set("clearhistory", value)
            self._history_settings[key] = self._daq_module.getInt("clearhistory")
        elif key == "duration":
            self._daq_module.set("duration", value)
            self._history_settings[key] = self._daq_module.getDouble("duration")
        else:
            pass

    def set_trigger_setting(self, key, value):
        setings_1 = {"forcetrigger", "bitmask" , "bits", "count",  "edge" , "type", "triggered"}
        setings_2 = {"bandwidth", "delay", "level"}
        if key in setings_1:
            self._daq_module.set(key, value)
            self._trigger_settings[key] = self._daq_module.getInt(key)
        elif key in setings_2:
            self._daq_module.set(key, value)
            self._trigger_settings[key] = self._daq_module.getDouble(key)
        elif key == "eventcountmode":
            self._daq_module.set("eventcount/mode", value)
            self._trigger_settings[key] = self._daq_module.getInt("eventcount/mode")
        elif key == "holdoffcount":
            self._daq_module.set("holdoff/count", value)
            self._trigger_settings[key] = self._daq_module.getInt("holdoff/count")
        elif key == "holdofftime":
            self._daq_module.set("holdoff/time", value)
            self._trigger_settings[key] = self._daq_module.getDouble("holdoff/time")
        elif key == "pulsemax":
            self._daq_module.set("pulse/max", value)
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/max")
        elif key == "pulsemin":
            self._daq_module.set("pulse/min", value)
            self._trigger_settings[key] = self._daq_module.getDouble("pulse/min")
        elif key == "triggernode":
            self._daq_module.set("triggernode", value)
            self._trigger_settings[key] = self._daq_module.getString("triggernode")
        else:
            pass

    def set_grid_setting(self, key, value):
        self._daq_module.set("grid/"+key, value)
        self._grid_settings[key] = self._daq_module.getInt("grid/"+key)

    def set_fft_setting(self, key, value):
        settings_1 = {"window", "absolute"}
        if key == "spectrumautobw":
            self._daq_module.set("spectrum/autobandwidth", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/autobandwidth")
        elif key == "spectrumenable":
            self._daq_module.set("spectrum/enable", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/enable")

        elif key == "spectrumoverlapped":
            self._daq_module.set("spectrum/overlapped", value)
            self._fft_settings[key] = self._daq_module.getInt("spectrum/overlapped")
        elif key == "spectrumfrequencyspan":
            self._daq_module.set("spectrum/frequencyspan", value)
            self._fft_settings[key] = self._daq_module.getDouble("spectrum/frequencyspan")
        elif key in settings_1:
            self._daq_module.set("fft/"+key, value)
            self._fft_settings[key] = self._daq_module.getInt("fft/"+key)
        else:
            pass

    def execute(self):
        self._daq_module.execute()

    #i dont think 'read' below is working
    def read(self, read=False, clck_rate=6e7):
        self._daq_module.read(read,clck_rate)

    def subscribe_stream_node(self, nodes=["x", "y"]):
        ##add assert to ensure that correct node is used
        node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
        for nd in nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            self._signal_paths.add(signal_path)
            self._daq_module.subscribe(signal_path)

    def unsubscribe_stream_node(self, nodes=["x", "y"]):
        node_check  = {"x", "y", "r", "theta", "frequency", "auxin0", "auxin1", "xiy", "df"}
        for nd in nodes:
            signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
            self._signal_paths.remove(signal_path)
            self._daq_module.unsubscribe(signal_path)


    def set_continuous_numeric_parameters(self, time_constant=10e-3):
        self._mfli.set_demods_settings("timeconstant", time_constant)
        self._mfli.set_demods_settings("enable", 1)
        self._daq_module.set("device", self._dev_id)
        self._daq_module.set("count", 3)
        self.set_trigger_setting("type", 0)
        self.set_grid_setting("mode", 4)
        signal_path = f"/{self._dev_id}/demods/0/sample.r"
        self._daq_module.set("count", 0)
        self._daq_module.set("grid/cols", 1000)
        self._daq_module.set("holdoff/time", 0)
        self._daq_module.set("refreshrate", 500)
        self._daq_module.subscribe(signal_path)
        self._mfli._daq_module.execute()
        time.sleep(0.6)

    def continuous_numeric(self):
        signal_path = f"/{self._dev_id}/demods/0/sample.r"
        data_read = self._daq_module.read(True)
        return data_read[signal_path]



    def continuous_data_acquisition_spectrum(self, freq_span, n_cols, signal_nodes = ["x", "y"]):
        ##prepare daq module for cont. data acquisition_time
        ## FFT settings (note: currently uses freq_span as standard)
        time_constant = 1/(2*freq_span)
        self.set_fft_setting("spectrumautobw", 1) #Subscribes  automatic bandwidth
        self.set_fft_setting("absolute",1) #Centers wrt demod freq
        self.set_fft_setting("spectrumenable",1) #Enables FFT mode of scope
        signal_path = f"/{self._dev_id}/demods/0/sample.xiy.fft.abs" #Defines signal path for PSD
        self.set_fft_setting("spectrumfrequencyspan", time_constant )

        ##Demod settings
        self._mfli.set_demods_settings("enable", 1) #Enables demodulator
        self._mfli.set_demods_settings("rate", 1e6) #Sets demod rate to 1 MSa/s
        self._mfli.set_demods_settings("freq", 0.0) #Sets demod freq. to 0
        self._mfli.set_demods_settings("timeconstant", 2e-6) #Sets demod freq. to 0
        time.sleep(10 * time_constant)

        ##Sigins settings
        self._mfli.set_sigins_settings("ac", 1)
        self._mfli.set_sigins_settings("imp50", 0)
        self._daq_module.set("device", self._dev_id)

        ## Trigger and grid settings
        self.set_trigger_setting("type", 0) #continuous
        self.set_grid_setting("mode", 4)
        self.set_grid_setting("cols", n_cols)

        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = self._mfli._daq.listNodes(f"/{self._dev_id}", flags)
        demod_path = f"/{self._dev_id}/demods/0/sample"
        if demod_path not in (node.lower() for node in streaming_nodes):
            raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")

        num_cols = int(np.ceil(sample_rate * burst_duration))
        num_bursts = int(np.ceil(total_duration / burst_duration))

        self._daq_module.subscribe(signal_path)
        data = {}
        data[signal_path] = []

        clockbase = float(self._mfli._daq.getInt(f"/{self._dev_id}/clockbase"))
        ts0 = np.nan
        read_count = 0
        self.execute()
        buffer_size = self._daq_module.getInt("buffersize")
        time.sleep(2 * buffer_size)
        data = daq_module.read(return_flat_data_dict)
        self._data = data

    # def hw_trig_data_acquisition_time_domain(self, acquisition_time, signal_nodes = ["x", "y"], trig_level = 1):
    #     self._mfli.set_demods_settings("enable", 1)
    #     self._daq_module.set("device", self._dev_id)
    #     self.set_trigger_setting("type", 6)
    #     self.set_grid_setting("mode", 4)
    #     self._daq_module.set("grid/cols",  num_cols)
    #     sig_paths = []
    #     for nd in signal_nodes:
    #         signal_path = f"/{self._dev_id}/demods/0/sample" + "." + nd
    #         sig_paths.append(signal_path)
    #
    #     self._daq_module.set("level", trig_level)
    #     trigger_duration = 0.18
    #     ##need to specify demod rate somewhere...
    #     self._daq_module.set("duration", trigger_duration)
    #     sample_count = int(demod_rate * trigger_duration)
    #     trigger_duration = daq_module.getDouble("duration")
    #
    #     ##Replace with actual trigger path here
    #     trigger_path = "/%s/demods/%d/sample.r" % (device, demod_index)
    #     self._daq_module.execute()
    #     if self._daq_module.finished():
    #         break
    #     else:
    #         pass
    #     time.sleep(1.2 * buffer_size)
    #     data = daq_module.read(True)
    #     clockbase = float(daq.getInt("/%s/clockbase" % device))
    #     dt_seconds = (samples[0]["timestamp"][0][-1] - samples[0]["timestamp"][0][0]) / clockbase
    #     self._data = data

        ## Figure out sampling rate ...

#device_id='dev6541'
#mfli_driver = MfliDriver(device_id)
#MflidaqModule  =  MfliDaqModule(mfli_driver)
#sample_data, time_axis = MflidaqModule.triggered_data_acquisition_time_domain(duration=3.733e-5, n_traces = 1000, sig_port  = 'Aux_in_1', sample_rate=107e3)
