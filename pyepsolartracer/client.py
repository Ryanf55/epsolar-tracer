# -*- coding: iso-8859-15 -*-

# import the server implementation
#import pymodbus
#import serial
#from pymodbus.pdu import ModbusRequest
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
#from pymodbus.transaction import ModbusRtuFramer
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.mei_message import *
from pyepsolartracer.registers import registerByName



import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
#import logging
#_logger = logging.getLogger(__name__)


class EPsolarTracerClient:
    ''' EPsolar Tracer client
    '''

    def __init__(self, unit=1, serialclient=None, **kwargs):
        ''' Initialize a serial client instance
        '''
        self.unit = unit
        if serialclient is None:
            port = kwargs.get('port', 'COM1')
            baudrate = kwargs.get('baudrate', 115200)
            self.client = ModbusClient(
                method="rtu",
                port=port,
                stopbits=1,
                bytesize=8,
                parity='N',
                baudrate=baudrate,
                timeout = 1.0
            )
        else:
            self.client = serialclient

    def connect(self):
        ''' Connect to the serial
        :returns: True if connection succeeded, False otherwise
        '''
        cc = self.client.connect()
        if cc is False:
            print("Unable to open port. Quitting")
            quit()

        return cc

    def close(self):
        ''' Closes the underlying connection
        '''
        return self.client.close()

    def read_device_info(self):
        #request = ReadDeviceInformationRequest(unit = self.unit)
        request = ReadDeviceInformationRequest(unit=self.unit)
        response = self.client.execute(request)
        return response

    def read_input(self, name):
        register = registerByName(name)
        if register.is_coil():
            response = self.client.read_coils(register.address, register.size, unit=self.unit)
        elif register.is_discrete_input():
            response = self.client.read_discrete_inputs(register.address, register.size, unit=self.unit)
        elif register.is_input_register():
            response = self.client.read_input_registers(register.address, register.size, unit=self.unit)
        else:
            response = self.client.read_holding_registers(register.address, register.size, unit=self.unit)
        return register.decode(response)

    def write_output(self, name, value):
        register = registerByName(name)
        values = register.encode(value)
        response = False
        if register.is_coil():
            self.client.write_coil(register.address, values, unit=self.unit)
            response = True
        elif register.is_discrete_input():
            log.error("Cannot write discrete input " + repr(name))
            pass
        elif register.is_input_register():
            log.error("Cannot write input register " + repr(name))
            pass
        else:
            self.client.write_registers(register.address, values, unit=self.unit)
            response = True
        return response

    def __enter__(self):
        self.connect()
        print("Context mngr connect")
        return self
    def __exit__(self,type,value,traceback):
        self.close()
        print("Context mngr close")


__all__ = [
    "EPsolarTracerClient",
]


class EPsolarTracerClientExtended(EPsolarTracerClient):
    def __init__(self, unit=1, serialclient=None, **kwargs):
        super().__init__(unit=1, serialclient=None, **kwargs)

        #Set this to 1 to allow user to use "Enter" button to control load at the same time as the script running
        #If left at 0 (defualt), the user will not be able to use the hardware button
        self.allow_manual_load_control = kwargs.get('allow_manual_load_control', 0)
        self.default_load_state = kwargs.get('default_load_state', None)
        # previous_load_state =  self.read_input("Default Load On/Off in manual mode").value


        #Todo add in mqtt functionality here instead
        self.mqtt_broker_ip = kwargs.get('mqtt_broker_ip', 'DISABLED')

        # if self.default_load_state is None:
        #     if self.read_input("Default Load On/Off in manual mode").value == 1:
        #         self.default_load_state = 1
        #         print("Default Load in manual mode on. Setting test mode state to on.")
        #     else:
        #         self.default_load_state = 0
        #         print("Default Load in manual mode is off. Setting test mode state to off.")
        # else:
        #     self.set_default_load_state(self.default_load_state)

        # # Enable load test mode if allow_manual_load_control is off
        # # Because there is no way to query the current load state, keep track of it in the code.
        # if self.allow_manual_load_control == 0:
        #     self._write_load_test_mode_enabled(1)
        #     print('Test mode enabled from now on')



    def write_load_state(self,load_state):
        raise NotImplementedError
        # if self.allow_manual_load_control == 1:

        #     # Turn on test mode, set the state, turn off test mode
        #     self._write_load_test_mode_enabled(1)
        #     if load_state == 1:
        #         print("ON")
        #         self.write_output("Force the load on/off",1)
        #     elif load_state == 0:
        #         print("OFF")
        #         self.write_output("Force the load on/off",0)
        #     else:
        #         print("Error. Unsupported Load State")
        #     self._write_load_test_mode_enabled(1)

        # else:
        #     #Already in test mode. Just set the state
        #     if load_state == 1:
        #         print("ON2")
        #         self.write_output("Force the load on/off",1)
        #     elif load_state == 0:
        #         print("OFF2")
        #         self.write_output("Force the load on/off",0)
        #     else:
        #         print("Error. Unsupported Load State")


    def set_load_to_default_load_state(self):
        raise NotImplementedError
        # self.write_load_state(self.default_load_state)

    def _write_load_test_mode_enabled(self,load_test_mode_enabled):
        raise NotImplementedError
        # if load_test_mode_enabled == 1: #user button controllable
        #     self.write_output("Enable load test mode",1)
        # elif load_test_mode_enabled == 0: #remote only
        #     self.write_output("Enable load test mode",0)
        # else:
        #     print("Error. Unsupported load test mode")


    def set_default_load_state(self,default_load_state):
        raise NotImplementedError
        # if default_load_state == 1:
        #     self.write_output("Default Load On/Off in manual mode",1)
        # elif default_load_state == 0:
        #     self.write_output("Default Load On/Off in manual mode",0)
        # else:
        #     print("Error. Unsupported load test mode")

    def close(self):
        ''' Closes the underlying connection
        '''
        # self.set_load_to_default_load_state()
        return self.client.close()



