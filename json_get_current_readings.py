#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-


# This reads severals values from the EPSolar-charging-controller via RS485-USB-Cable (correct kernel-driver-module needed)

from pyepsolartracer.client import EPsolarTracerClient
import json

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

client = EPsolarTracerClient(port = '/dev/ttyUSB0')
if client.connect() == False:
    print("Error. Port not able to be opened")


data = []  # New List for Data

response = client.read_device_info()

#data.append(["Device Info"])  # Root Layer
#data[0].append(
data.append(
    {
        'con-manufacturer':repr(response.information[0]),
        'con-model':repr(response.information[1]),
        'con-version':repr(response.information[2]),
        'con-temp-controller':client.read_input("Temperature inside equipment").value,
        'con-temp-heatsink':client.read_input("Power components temperature").value
    }
)

#data.append(["PV-Generator"])  # Root Layer
#data[1].append(
data.append(
    {
        'pv-voltage':client.read_input("Charging equipment input voltage").value,
        'pv-current':client.read_input("Charging equipment input current").value,
        'pv-power':client.read_input("Charging equipment input power").value
    }
)

#data.append(["Battery"])  # Root Layer
#data[2].append(
data.append(
    {
        'bat-voltage':client.read_input("Charging equipment output voltage").value,
        'bat-current':client.read_input("Charging equipment output current").value,
        'bat-power':client.read_input("Charging equipment output power").value,
        'bat-temp':client.read_input("Battery Temperature").value,
        'bat-perc':client.read_input("Battery SOC").value
    }
)

#data.append(["Load"])  # Root Layer
#data[3].append(
data.append(
    {
        'load-voltage':client.read_input("Discharging equipment output voltage").value,
        'load-current':client.read_input("Discharging equipment output current").value,
        'load-power':client.read_input("Discharging equipment output power").value
    }
)

client.close()

#DEBUG
#print(data[0].get('con-manufacturer'))


# json.dump(data, outfile)
jsondata=json.dumps(data,indent=4)
print(jsondata)
