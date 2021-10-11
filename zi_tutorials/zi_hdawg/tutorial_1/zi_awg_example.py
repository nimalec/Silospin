import os
import time
import textwrap
import numpy as np
import zhinst.utils


def run_example(
    device_id,
    server_host: str = "localhost",
    server_port: int = 8004, ):
    apilevel_example = 6  #
    (daq, device, _) = zhinst.utils.create_api_session(
        device_id, apilevel_example, server_host=server_host, server_port=server_port)
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
    # Ensure that all settings have taken effect on the device before continuing.
    daq.sync()
    AWG_N = 2000

    awg_program = textwrap.dedent(
        """\
        const AWG_N = _c1_;
        wave w2 = vect(_w2_);
        playWave(w2);
        """
    )

    #waveform_0 = -1.0 * np.blackman(AWG_N)
    waveform_2 = np.sin(np.linspace(0, 2 * np.pi, 96))
        #          considerably and should be used for short waveforms only.
    awg_program = awg_program.replace("_w2_", ",".join([str(x) for x in waveform_2]))
    awg_program = awg_program.replace("_c1_", str(AWG_N))

    awgModule = daq.awgModule()
    awgModule.set("device", device)
    awgModule.execute()

    data_dir = awgModule.getString("directory")
    wave_dir = os.path.join(data_dir, "awg", "waves")

    if not os.path.isdir(wave_dir):
        # The data directory is created by the AWG module and should always exist. If this exception
        # is raised, something might be wrong with the file system.
        raise Exception(
            f"AWG module wave directory {wave_dir} does not exist or is not a directory"
        )
    # Save waveform data to CSV
    csv_file = os.path.join(wave_dir, "wave0.csv")
    np.savetxt(csv_file, waveform_0)

    awgModule.set("compiler/sourcestring", awg_program)


    if __name__ == "__main__":
       import sys
       from pathlib import Path

       cli_util_path = Path(__file__).resolve().parent / "../../utils/python"
       sys.path.insert(0, str(cli_util_path))
       cli_utils = __import__("cli_utils")
       cli_utils.run_commandline(run_example, __doc__)
       sys.path.remove(str(cli_util_path))
