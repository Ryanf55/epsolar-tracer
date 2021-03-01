import json
import logging
from time import sleep
from pyepsolartracer.client import EPsolarTracerClientExtended,EPsolarTracerClient
from khaotic import MQTT_Client


PORT_NAME = '/dev/ttyUSB0'
CLIENT_ID = 'epsolar'
BROKER_IP = "10.0.0.33"


# configure the client logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

mclient = MQTT_Client(CLIENT_ID, BROKER_IP)



with EPsolarTracerClient(
         port = PORT_NAME,
         #'default_load_state':0
    ) as solar:



    try:
        while True:
            j = {
                "pv" : {
                    'pv-voltage':solar.read_input("Charging equipment input voltage").value,
                    'pv-current':solar.read_input("Charging equipment input current").value,
                    'pv-power':solar.read_input("Charging equipment input power").value
                },
                "bat": {
                    'bat-voltage':solar.read_input("Charging equipment output voltage").value,
                    'bat-current':solar.read_input("Charging equipment output current").value,
                    'bat-power':solar.read_input("Charging equipment output power").value,
                    'bat-temp':solar.read_input("Battery Temperature").value,
                    'bat-perc':solar.read_input("Battery SOC").value
                },
                "load": {
                    'load-voltage':solar.read_input("Discharging equipment output voltage").value,
                    'load-current':solar.read_input("Discharging equipment output current").value,
                    'load-power':solar.read_input("Discharging equipment output power").value
                }
            }
            print(j)
            for k,v in j.items():
                topic = CLIENT_ID + "/" + k
                payload = json.dumps(v)
                mclient.publish(topic=topic, payload=payload, qos=0)
            sleep(1)
    except KeyboardInterrupt:
        quit()


