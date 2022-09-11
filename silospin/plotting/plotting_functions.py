import matplotlib.pyplot as plt
import numpy as np

def plot1DVoltageSweep(fig, input_voltage, output_voltage, idx, channel_number):
    plt.figure(figsize=(4,4))
    plt.plot(input_voltage[0:idx-1], output_voltage[0:idx-1], label='linear', color = "red")
    plt.xlabel('Barrier Gate Voltage [V]')
    plt.ylabel('Measured Voltage [V]')
    plt.show()

def plot2DVoltageSweep(V_x, V_y, V_out, channel_numbers):
    plt.figure(figsize=(4,4))
    fig, ax0 = plt.subplots(1, 1)
    z_min = np.min(V_out)
    z_max = np.max(V_out)
    c = ax0.pcolor(V_x, V_y, V_out, cmap='RdBu', vmin=z_min, vmax=z_max)
    cbar = fig.colorbar(c, ax=ax0)
    cbar.set_label('Output Voltage [V]', rotation=270)
    plt.xlabel('Channel ' +str(channel_numbers[0]) + ' Barrier Voltage [V]')
    plt.ylabel('Channel ' +str(channel_numbers[1]) + ' Barrier Voltage [V]')
    plt.show()
