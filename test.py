import logging

from pyepsolartracer.client import EPsolarTracerClientExtended,EPsolarTracerClient


PORT_NAME = '/dev/ttyUSB0'


# configure the client logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


SOLAR_CLIENT = EPsolarTracerClient(
    port = PORT_NAME,
    #'default_load_state':0
    
)

SOLAR_CLIENT.connect()

#m = mqtt_manager()
#r = rgb_limiter()

response = SOLAR_CLIENT.read_device_info()

print("RESP",response,"SDF")
print(response.information)


