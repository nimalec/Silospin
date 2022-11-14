import serial
from zerorpc import Client

def set_val(parameter, value, channel_mapping):
    ##For now, channel_mapping = input. Once channel mapping is known, we can use a pickle file for this.
    ## Channel map ==> uses a dictionary

    all_gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "M1", "R1", "L2", "M2", "R2", "TS", "BS1", "BS2", "MS"}
    ohmic_gates = {"Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    hemts = {"HEMT1", "HEMT2"}
    sensors02 = {"L2", "M2", "R2"}
    sensors1 = {"L2", "M2", "R2"}
    topgates = {"B1", "P1", "P2", "B3", "P3", "B4", "P4", "B5"}

    if parameter in all_gates:
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        client.set_channel(channel_mapping["gates"][parameter])
        client.set_voltage(value)

    elif parameter == "allgates":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in all_gates:
            client.set_channel(channel_mapping["gates"][gt])
            client.set_voltage(value)

    elif parameter in ohmic_gates:
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        client.set_channel(channel_mapping["ohmics"][parameter])
        client.set_voltage(value)

    elif parameter == "ohmics":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in ohmic_gates:
            client.set_channel(channel_mapping["ohmics"][gt])
            client.set_voltage(value)

    elif parameter in hemts:
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        client.set_channel(channel_mapping["hemts"][gt])
        client.set_voltage(value)

    elif parameter == "hemts":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in hemts:
            client.set_channel(channel_mapping["hemts"][gt])
            client.set_voltage(value)

    elif parameter == "topgates":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in topgates:
            client.set_channel(channel_mapping["gates"][gt])
            client.set_voltage(value)

    elif parameter == "sensor02":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in sensors02:
            client.set_channel(channel_mapping["gates"][gt])
            client.set_voltage(value)

    elif parameter == "sensors1":
        client = Client()
        client.connect("tcp://0.0.0.0:4243")
        for gt in sensors1:
            client.set_channel(channel_mapping["gates"][gt])
            client.set_voltage(value)
    else:
        pass
