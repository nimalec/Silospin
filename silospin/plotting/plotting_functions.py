def plot1DVoltageSweep(input_voltage, output_voltage, idx, channel_number):
    plt.figure(figsize=(5, 2.7))
    plt.plot(input_voltage[0:idx-1], output_voltage[0:idx-1], label='linear', color = "red")
    plt.xlabel('Barrier Gate Voltage [V]')
    plt.ylabel('Measured Voltage [V]')
    plt.title("Measured Output Voltage from Sweep on CH" + str(channel_number))
