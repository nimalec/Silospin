from zhinst.toolkit import Waveforms
import numpy as np

class TestWaveformUpload:
    def __init__(self, hdawg):
        waveforms = Waveforms()
        waveforms.assign_waveform(slot=0, wave1=np.ones(256))
        for idx in rnage(0,4):
            awg._hdawg.awgs[idx].write_to_waveform_memory(waveforms)
