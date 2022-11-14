import serial
from zerorpc import Client

def make_dac_channel_mapping(channel_map=None):
    if channel_map:
        dac_channel_mapping = channel_map
    else:
        dac_channel_mapping = {"gates":
         {"B1": 1, "B2": 2, "B3": 3, "B4": 4, "B5": 5, "P1": 6, "P2": 7,  "P3": 8, "P4": 9, "L1": 10, "L2": 11,  "M1": 12, "M2": 13,  "R1": 14, "R2": 15,  "BS1": 16, "BS2": 17, "TS": 18, "MS": 19} ,
        "ohmics": {"Source1": 20, "Drain1": 21, "Source2": 22, "Drain2": 23, "Source3": 24}}
    return dac_channel_mapping 



def set_val(parameter, value, channel_mapping, client):
    ##For now, channel_mapping = input. Once channel mapping is known, we can use a pickle file for this.
    ## Channel map ==> uses a dictionary
    ## channel_mapping = {"gates": , "ohmics": , "hemts":  , "bottomgates":   }
    ## Should be preconnected to the instrument (use cliient, don't recoonnect each time)

    all_gates = {"B1", "B2", "B3", "B4", "B5", "P1", "P2",  "P3", "P4", "L1", "L2",  "M1", "M2",  "R1", "R2",  "BS1", "BS2", "TS", "MS"}
    ohmic_gates = {"Source1", "Drain1", "Source2", "Drain2", "Source3", "Drain3"}
    sensors02 = {"L2", "M2", "R2"}
    topgates = {"B1", "P1", "P2", "B3", "P3", "B4", "P4", "B5"}
    rightddgates = {"B3", "P3", "P4", "B5"}
    sensors1 = {"L1", "M1", "R1"}
    sensors2 = {"L2", "M2", "R2"}


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
