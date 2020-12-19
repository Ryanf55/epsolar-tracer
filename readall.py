#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# import time

# import the server implementation
# from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from pyepsolartracer.client import EPsolarTracerClient
from test.testdata import ModbusMockClient as ModbusClient
from pymodbus.mei_message import *
from pyepsolartracer.registers import registers, coils

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)
log.setLevel(logging.WARN)

#Solar-controller-ID:
unitnum = 1

# choose the serial client
#client = ModbusClient(method='rtu', port='/dev/ttyXRUSB0', baudrate=115200, stopbits = 1, bytesize = 8, timeout=1)

client = EPsolarTracerClient(port='/dev/ttyUSB0')
client.connect()

request = ReadDeviceInformationRequest(unit=unitnum)
#response = client.execute(request)
response = client.client.execute(request)
print(repr(response.information))

for reg in registers:
    print()
    print(reg)
    #rr = client.read_input_registers(reg.address, 1, unit=unitnum)
    rr = client.client.read_input_registers(reg.address, 1, unit=unitnum)
    if hasattr(rr, "getRegister"):
        print("read_input_registers:", rr.getRegister(0))
    else:
        print("read_input_registers", str(rr))
    #rr = client.read_holding_registers(reg.address, 1, unit=unitnum)
    rr = client.client.read_holding_registers(reg.address, 1, unit=unitnum)
    if hasattr(rr, "getRegister"):
        print("read_holding_registers:", rr.getRegister(0))
    else:
        print("read_holding_registers:", str(rr))

for reg in coils:
    print()
    print(reg)
    #rr = client.read_coils(reg.address, unit=unitnum)
    rr = client.client.read_coils(reg.address, unit=unitnum)
    if hasattr(rr, "bits"):
        print("read_coils:", str(rr.bits))
    else:
        print("read_coils:", str(rr))
    #rr = client.read_discrete_inputs(reg.address, unit=unitnum)
    rr = client.client.read_discrete_inputs(reg.address, unit=unitnum)
    if hasattr(rr, "bits"):
        print("read_discrete_inputs:", str(rr.bits))
    else:
        print("read_discrete_inputs:", str(rr))


