#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

#TODO improve robustness for data requests
#TODO add battery alert working
#TODO check power computation outdoor


# This reads severals values from the EPSolar-charging-controller via RS485-USB-Cable (correct kernel-driver-module needed)

from pyepsolartracer.client import EPsolarTracerClientExtended
import time
port_name = 'COM1'

#MQTT Color Maps
class rgb_limiter():
    def __init__(self):
        self.max_v = 14
        self.min_v = 12
 
        self.max_r = 255
        self.min_r = 0
        self.max_g = 255
        self.min_g = 0


    def get_rgb(self,cur_v):
        v_scale = (cur_v - self.min_v) /  (self.max_v - self.min_v)
        r_val = self.clamp(round((1 - v_scale)* (self.max_r - self.min_r) + self.min_r),self.min_r,self.max_r)
        g_val = self.clamp(round((v_scale)* (self.max_g - self.min_g) + self.min_g),self.min_g,self.max_g)

        return r_val*65536 + g_val*256 + 0 

    def clamp(self,n, minn, maxn):
        return max(min(maxn, n), minn)



#MQTT
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import sys

#broker_address= "10.7.100.87" # Your local computer ip broker if running tests
broker_address= "192.168.0.180" 
broker_port = 1883

client_name = 'EPEVER Client'
sub_topics = {
    "load" : "solar_commands/load", #turn on and off load
}

mqtt_connected_flag = False




def connect_to_broker(client,broker_address):
    try:
        client.connect(broker_address)               #connect to broker 

    #If the broker connection has a timeout, try again. If wanting to run the cart without mqtt connection to the rail, comment out the recursive call
    except TimeoutError:
        print("Error: MQTT broker connection timeout. Retrying connection to ",broker_address,"...")
        connect_to_broker(client,broker_address)

    except OSError:
        print("Error: MQTT broker address of ",broker_address, " is not reachable on the current network. Will retry but double check broker_address.")

def on_connect(client, userdata, flags, rc):    #todo if rc != 0
    if rc==0:
        print("connected ok, userdata = ",userdata, "flags = ",flags,"rc = ",rc )
        global mqtt_connected_flag
        mqtt_connected_flag = True


        #Subscribe to all topics needed
        for sub_topic_name in sub_topics:
            print("Subbing to ",sub_topic_name,":",sub_topics[sub_topic_name])
            client.subscribe(sub_topics[sub_topic_name])

        client.publish("connection/solar",0*65536+255*256+0)
        print(client_name,"is now connected to MQTT broker.")

        #TODO scan for clients to ensure the cart is connected to mqtt otherwise wait.

def on_disconnect(client, userdata, rc): #TODO lastwill and logging.
    # TODO Don't let the cart returning to mqtt light the led until both rail and cart are connected. Use connected_flag for rail
    global mqtt_connected_flag
    mqtt_connected_flag = False
    print("Warning. MQTT Client Disconnected.")

class mqtt_manager:
    def __init__(self):
        self.mqtt_client = mqtt.Client('Rpi_Vulcan')            # create new instance 
        self.mqtt_client.on_connect=on_connect                  # bind call back function for connecting
        self.mqtt_client.on_disconnect = on_disconnect          # bind call back function for connecting
        self.mqtt_client.on_message = on_message
        self.mqtt_client.will_set("connection/solar", 255*65536+0*256+0,qos=1,retain=False) #green 0*65536+255*256+0

        self.mqtt_client.loop_start()   
        print("Starting Loop")
        


        #Try connecting until the broker is on 

        try:
            print("Connecting Vulcan to MQTT Network...")
            connect_to_broker(self.mqtt_client,broker_address)
            print("Success. Connected to broker ",broker_address)
            

        except ConnectionRefusedError:
            print ("Client is not able to find broker")

    def publish_mqtt(self,topic,payload):
        if mqtt_connected_flag == True:
            try:
                self.mqtt_client.publish(topic,payload)

            except:
                print("Unexpected error in publishing mqtt sensors of :",sys.exc_info())
            return True
        else:
            return False


def on_message(client, userdata, msg):
    global solar_client
    try:
        topic = msg.topic
        message_str = str(msg.payload.decode("utf-8"))
        print(topic,"->",message_str)
        if topic.startswith("solar_commands/"): #TODO add a dictionary to move all these strings into it. Ex:"rail_sensors", "True",etc.
            action_name = topic.split("solar_commands/")[1]
            if action_name == "load":
                if message_str == "1":
                    solar_client.write_load_state(1)
                elif message_str == "0":
                    solar_client.write_load_state(0)
                else:
                    print("Unknown Load State Request of",action_name)
                
                #print("MSG Parse Success. Rail Estop:",rail_estop_button)
            else:
                print("Error. on_message unknown action_name of ",action_name)
        else:
            print("Error. on_message hasn't acted upon ",topic,"->",message_str)
    except: 
        print("Error: Uncaptured error in on_message.")
        print(sys.exc_info())
    else:
        #print("Message:",topic, " -> ",message_str)
        pass


# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


solar_client = EPsolarTracerClientExtended({  'port':port_name,
                                        'default_load_state':0})
solar_client.connect()

m = mqtt_manager()
r = rgb_limiter()

response = solar_client.read_device_info()
print("Manufacturer:", repr(response.information[0]))
print("Model:", repr(response.information[1]))
print("Version:", repr(response.information[2]))

print("")
print("Battery:")
print(solar_client.read_input("Battery SOC"))  # Momentary Percentage of Battery's remaining capacity


while True:
    
    try:
        m.publish_mqtt('solar_data/solar_voltage'   ,solar_client.read_input("Charging equipment input voltage").value)  # Momentary Voltage of PV-Generator
        m.publish_mqtt('solar_data/solar_current'   ,solar_client.read_input("Charging equipment input current").value)  # Momentary Current of PV-Generator
        m.publish_mqtt('solar_data/solar_power'     ,solar_client.read_input("Charging equipment input power").value)  # Momentary Power of PV-Generator
        m.publish_mqtt('solar_data/battery_voltage' ,solar_client.read_input("Charging equipment output voltage").value)  # Momentary Voltage of Battery-Output
        m.publish_mqtt('solar_data/battery_current' ,solar_client.read_input("Charging equipment output current").value)  # Momentary Current of Battery-Output
        m.publish_mqtt('solar_data/battery_power'   ,solar_client.read_input("Charging equipment output power").value)  # Momentary Power of Battery-Output
        m.publish_mqtt('solar_data/load_voltage'    ,solar_client.read_input("Discharging equipment output voltage").value)  # Momentary Voltage of LOAD-Output
        m.publish_mqtt('solar_data/load_current'    ,solar_client.read_input("Discharging equipment output current").value)  # Momentary Current of LOAD-Output
        m.publish_mqtt('solar_data/load_power'      ,solar_client.read_input("Discharging equipment output power").value)  # Momentary Power of LOAD-Output
        
        # Net Power
        try:
            net_power = solar_client.read_input("Charging equipment input power").value - solar_client.read_input("Charging equipment output power").value - solar_client.read_input("Discharging equipment output power").value
            m.publish_mqtt('solar_data/net_power'       ,net_power)
        except:
            print("Error net power calc")

        # Low Battery
        cur_voltage = solar_client.read_input("Charging equipment output voltage").value
        try:
            if cur_voltage < 12.5:
                print("Low Battery")
                m.publish_mqtt('solar_data/battery_alert'   ,r.get_rgb(cur_voltage))  # Momentary Voltage of PV-Generator
            else:
                m.publish_mqtt('solar_data/battery_alert'   ,r.get_rgb(cur_voltage))
        except TypeError:
            pass


        time.sleep(5)
    except KeyboardInterrupt:
        solar_client.close()
        break

solar_client.close()
