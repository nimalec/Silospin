import os
import time
import textwrap
import numpy as np
import zhinst.utils

dev_id = 8446
server_host =  "localhost"
server_port = 8004
apilevel_example = 6
daq, device = zhinst.utils.create_api_session(dev_id, apilevel_example, server_host=server_host, server_port=server_port)
zhinst.utils.api_server_version_check(daq)
zhinst.utils.disable_everything(daq, device)

daq.setInt(f"/{device}/system/awg/channelgrouping", 0)
out_channel = 0
awg_channel = 0
amplitude = 1.0


exp_setting = [
    ["/%s/sigouts/%d/on" % (device, out_channel), 1],
    ["/%s/sigouts/%d/range" % (device, out_channel), 1],
    ["/%s/awgs/0/outputs/%d/amplitude" % (device, awg_channel), amplitude],
    ["/%s/awgs/0/outputs/0/modulation/mode" % device, 0],
    ["/%s/awgs/0/time" % device, 0],
    ["/%s/awgs/0/userregs/0" % device, 0],
]

daq.set(exp_setting)
daq.sync()
AWG_N = 2000


awg_program = textwrap.dedent(
    """\
    const AWG_N = _c1_;
    wave w2 = vect(_w2_);
    playWave(w2);
    """
    )

waveform_2 = np.sin(np.linspace(0, 2 * np.pi, 96))
awg_program = awg_program.replace("_w2_", ",".join([str(x) for x in waveform_2]))
awg_program = awg_program.replace("_c1_", str(AWG_N))

awgModule = daq.awgModule()
awgModule.set("device", device)
awgModule.execute()

awgModule.set("compiler/sourcestring", awg_program)

while awgModule.getInt("compiler/status") == -1:
    time.sleep(0.1)

if awgModule.getInt("compiler/status") == 1:
        # compilation failed, raise an exception
    raise Exception(awgModule.getString("compiler/statusstring"))

if awgModule.getInt("compiler/status") == 2:
    print( "Compilation successful with warnings, will upload the program to the instrument.")
    print("Compiler warning: ", awgModule.getString("compiler/statusstring"))
