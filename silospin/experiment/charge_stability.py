from silospin.drivers.zi_mfli_driver import MfliDriver
from silospin.drivers.zi_mfli_driver import MfliDaqModule as DaqModule
from silospin.drivers.homedac_box import DacDriver

class ChargeStabilitySweeps:
    def __init__(self, dac_id="ASRL3::INSTR", mfli_id="dev5759"):
        self._dac = DacDriver(dac_id)
        self._mfli = MfliDriver(mfli_id)
        self._daq_mod =  DaqModule(self._mfli)
        self._input_voltages = []
        self._measured_voltages = []

    def sweep1D(self, channel, start_v, end_v, npoints):
        self._dac._dac.query("CH "+str(channel))
        v_array = np.linspace(start_v,end_v,npoints)
        self._input_voltages.append(v_array)
        output_voltages = []
        for v in v_array:
            self._dac._dac.query("VOLT "+str(v))
            voltage_str = self._dac._dac.query("VOLT?")
            self._dac._channel_configuration[channel] = v
            val = self._daq_mod.continuous_numeric()
            output_voltages.append(val)
        output_voltages = np.array(output_voltages)
        return (v_array, output_voltages)


    #def sweep2D(self,):
