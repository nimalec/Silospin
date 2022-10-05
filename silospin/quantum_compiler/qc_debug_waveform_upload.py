from silospin.drivers.zi_hdawg_driver import HdawgDriver as hdawg
from zhinst.toolkit import Waveforms
from zhinst.toolkit import Session
import numpy as np

class TestWaveformUpload:
    def __init__(self, dev_id="dev8446"):
        device = hdawg(dev_id)
        #session = Session('localhost')
        #evice = session.connect_device(dev_id)
        waveforms = Waveforms()
        waveforms.assign_waveform(slot=0, wave1=np.ones(256))
        for idx in range(0,4):
            device.awgs[idx].write_to_waveform_memory(waveforms)
