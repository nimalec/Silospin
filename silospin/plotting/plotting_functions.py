import matplotlib.pyplot as plt

def plot1DVoltageSweep(fig, input_voltage, output_voltage, idx, channel_number):
    plt.figure(figsize=(4,4))
    plt.plot(input_voltage[0:idx-1], output_voltage[0:idx-1], label='linear', color = "red")
    plt.xlabel('Barrier Gate Voltage [V]')
    plt.ylabel('Measured Voltage [V]')
    plt.title("Measured Output Voltage from Sweep on CH" + str(channel_number))
    plt.show()

def plot2DVoltageSweep(V_x, V_y, V_out, channel_numbers):
    plt.figure(figsize=(4,4))
    fig, ax0 = plt.subplots(1, 1)
    c = ax0.pcolor(V_x, V_y, V_out, cmap='PuBu_r')
    fig.colorbar(c, ax=ax0)
    plt.title("Measured Output Voltage from Sweep on CH" + str(channel_numbers[0]) + "and CH" + str(channel_numbers[1]))
    plt.show()
    # #plt.xlabel('Barrier Gate Voltage [V]')
    # #plt.ylabel('Measured Voltage [V]')
    # plt.title("Measured Output Voltage from Sweep on CH" + str(channel_numbers[0]) + "and CH" + str(channel_numbers[1]))
    # plt.show()
