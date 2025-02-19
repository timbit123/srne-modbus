import os
import paho.mqtt.client as mqtt
import time
import json
from dotenv import load_dotenv
from modbus import debug
from mqtt_topic_config import mqtt_config, device, mqtt_set_config

load_dotenv()


writing_queue = []
publishing_queue = []


# This code establishes a connection to an MQTT server and continuously sends data to Home Assistant
def on_connect(client, userdata, flags, rc):
    # Callback function for when the client connects to the MQTT server
    print(f"Connected with result code {rc}")


def on_message(client, userdata, msg):
    # Callback function for when a message is received from the MQTT server
    topic = msg.topic
    payload = msg.payload.decode()
    topic = topic.split("/")  # remove the first two '/' in the topic
    topic = "/".join(topic[2:-1])  # reassemble the topic without leading '/'
    if topic in mqtt_config:
        if "topic_type" in mqtt_config[topic]:
            if mqtt_config[topic]["topic_type"] == "button":
                if "value" in mqtt_config[topic]:
                    payload = mqtt_config[topic]["value"]
                else:
                    payload = 0
        if mqtt_config[topic].get("dangerous", False):
            if mqtt_config["inverter/enable_danger"]["last_value"] != "Enabled":
                print(f"Received message: {msg.payload.decode()} but ignoring since inverter/enable_danger not Enabled")
                return
    if topic in mqtt_set_config:
        writing_queue.append((mqtt_set_config[topic], payload, topic))

    print(f"Received message: {msg.payload.decode()}")


# Create an instance of the MQTT client
client = mqtt.Client()

# Set callback functions for connection and message receipt
client.on_connect = on_connect
client.on_message = on_message


# Set username and password for MQTT client using environment variables from .env file
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
host = os.getenv("MQTT_HOST")
port = int(os.getenv("MQTT_PORT"))

if username is not None and password is not None:
    client.username_pw_set(username, password)
else:
    raise ValueError("Missing MQTT_USERNAME or MQTT_PASSWORD in .env file")


# Connect to the MQTT server
client.connect(host, port)
mqtt_topic = os.getenv("MQTT_TOPIC")

for name, vals in mqtt_config.items():
    if not vals.get("enabled", True):
        continue
    topic = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{name}/state"
    field_name = f"{mqtt_topic}-{str(name).replace('/','-')}"

    if "command_topic" in vals["config"]:
        vals["config"][
            "command_topic"
        ] = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{vals['config']['command_topic']}/set"
        client.subscribe(vals["config"]["command_topic"])
        print(f"Subscribed to {vals['config']['command_topic']}")
    
    discovery_data = {
        "device": device,
        "uniq_id": field_name,
        **{key: vals["config"][key] for key in vals["config"]},
    }
    if vals.get("topic_type", 'sensor') != "button":
        discovery_data["state_topic"] = topic

    json_data = json.dumps(discovery_data)

    client.publish(
        f"homeassistant/{vals.get('topic_type', 'sensor')}/{field_name}/config",
        json_data,
        retain=True,
    )

loop_sleep: float = (
    int(os.getenv("LOOP_SLEEP")) if os.getenv("LOOP_SLEEP") else 200
) / 1000
general_interval: float = (
    int(os.getenv("GENERAL_INTERVAL")) if os.getenv("GENERAL_INTERVAL") else 5000
) / 1000
refresh_interval: float = (
    int(os.getenv("REFRESH_INTERVAL")) if os.getenv("REFRESH_INTERVAL") else 5000
) / 1000

# Loop continuously sending data to Home Assistant
client.loop_start()
while True:

    # check if we need to update values
    if len(writing_queue) > 0:
        for set_fuction, payload, topic in writing_queue:
            returnval = set_fuction(payload) 
            if returnval == "update_value":
                print("Handling update_value for " + topic)
                mqtt_config[topic]["last_value"] = payload
            if returnval != None:
                #print(topic + " last_update was " + str(mqtt_config[topic]["last_update"])) 
                interval = vals.get("interval")
                current_time = time.time()
                mqtt_config[topic]["last_update"] = current_time - interval + refresh_interval 
                #print(topic + " last_update is now " + str(mqtt_config[topic]["last_update"])) 

        writing_queue = []
        time.sleep(loop_sleep)

    for name, vals in mqtt_config.items():
        if not vals.get("enabled", True) or vals.get('topic_type', 'sensor') == "button":
            continue
        # find a way to skip values depending the loop count in vals['loop_count']
        last_update = vals.get("last_update")
        interval = vals.get("interval")
        current_time = time.time()
        if last_update is not None:
            if interval == -1:
                continue
            if current_time - last_update <= interval:
                continue

        debug(f"updating {name}")
        topic = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{name}/state"
        if "args" in vals:  
            vals["args"]["name"] = vals["config"]["name"]
            value = vals["value"](**vals["args"])
        else:
            value = vals["value"]()
        if value != None:
            mqtt_config[name]["last_update"] = current_time
            mqtt_config[name]["last_value"] = value
            publishing_queue.append((topic, value))

    if len(publishing_queue) > 0:
        for topic, value in publishing_queue:
            client.publish(topic, value)
        publishing_queue = []

    time.sleep(loop_sleep)

client.loop_stop()
