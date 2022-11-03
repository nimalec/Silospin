import serial

def set_val(device_id, intrument_type, parameter, value, value_type, device_connected=None):
    ##Value type ==> float, int, or str
    ## Intrument ==> connection ID  (should aso include baud_rate , termination_char, verbose)
    baud_rates =  {'dac': 250000, 'mw': 250000}
    if device_connected:
        device = device_connected
    else:
        device = serial.Serial(device_id, baudrate=baud_rates[device_id], parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=1)

    if value_type == 'float':
        write_command = parameter+' '+str('{:.6f}'.format(value))+'\n'
    elif value_type == 'int':
        write_command = parameter+' '+str(int(value))+'\n'
    elif value_type == 'str':
        write_command = parameter+' '+str(value)+'\n'
    else:
        pass
            device.write(write_command.encode('utf-8'))
