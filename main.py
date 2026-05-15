import os
import paho.mqtt.client as mqtt
import time
import json
import signal
import sys
import random
from dotenv import load_dotenv
from modbus import debug
import modbus
from mqtt_topic_config import mqtt_config, device, mqtt_set_config, LEAD_ACID_BATTERY_TYPES, EQUALIZATION_AVAIL_TOPIC


load_dotenv()


mqtt_topic = os.getenv("MQTT_TOPIC") or ""

# Sync inverter datetime
last_datetime_sync = None
datetime_sync_interval = (
    int(os.getenv("SYNC_DATETIME_INTERVAL")) * 60
)  # minutes to seconds
datetime_sync_enabled = os.getenv("SYNC_DATETIME_ENABLED") == "true"


writing_queue = []
publishing_queue = []

_last_equalization_avail: str = ""
_hidden_register_topics: set = set()


def _is_value_in_range(value: str, vals: dict) -> bool:
    """Return False if a number entity value is outside its configured min/max.
    Non-number entities always pass."""
    if vals.get("topic_type") != "number":
        return True
    config = vals.get("config", {})
    min_val = config.get("min")
    max_val = config.get("max")
    if min_val is None and max_val is None:
        return True
    try:
        v = float(value)
        if min_val is not None and v < float(min_val):
            return False
        if max_val is not None and v > float(max_val):
            return False
    except (ValueError, TypeError):
        return False
    return True


def _hide_topic(client, name: str, vals: dict):
    """Publish an empty retained payload to remove a topic from HA discovery."""
    field_name = f"{mqtt_topic}-{name.replace('/', '-')}"
    client.publish(
        f"homeassistant/{vals.get('topic_type', 'sensor')}/{field_name}/config",
        "",
        retain=True,
    )
    print(f"Disabled HA entity for unsupported register: {name}")


def _restore_topic(client, name: str, vals: dict):
    """Re-publish a discovery message for a topic whose register has recovered."""
    field_name = f"{mqtt_topic}-{name.replace('/', '-')}"
    discovery_data = {
        "device": device,
        "uniq_id": field_name,
        **{key: vals["config"][key] for key in vals["config"]},
    }
    if vals.get("topic_type", "sensor") != "button":
        discovery_data["state_topic"] = (
            f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{name}/state"
        )
    client.publish(
        f"homeassistant/{vals.get('topic_type', 'sensor')}/{field_name}/config",
        json.dumps(discovery_data),
        retain=True,
    )
    vals["last_update"] = None  # force immediate re-read
    print(f"Restored HA entity for recovered register: {name}")


def publish_equalization_availability(client):
    """Publish online/offline to the equalization availability topic based on battery type."""
    global _last_equalization_avail
    battery_type = mqtt_config.get("battery/type", {}).get("last_value")
    payload = "online" if battery_type in LEAD_ACID_BATTERY_TYPES else "offline"
    if payload != _last_equalization_avail:
        client.publish(EQUALIZATION_AVAIL_TOPIC, payload, retain=True)
        _last_equalization_avail = payload
        print(f"Equalization availability: {payload} (battery type: {battery_type})")


# This code establishes a connection to an MQTT server and continuously sends data to Home Assistant
def on_connect(client, userdata, connect_flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    if reason_code.is_failure:
        return
    subscribe(client)
    # Read battery type immediately so equalization availability is correct from the start
    battery_type = modbus.read_lookup_register(0xE004, modbus.BATTERY_TYPES)
    if battery_type is not None:
        mqtt_config["battery/type"]["last_value"] = battery_type
    publish_equalization_availability(client)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Unexpected MQTT disconnect: {reason_code} — will auto-reconnect")
    else:
        print("MQTT disconnected cleanly")


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
                print(
                    f"Received message: {msg.payload.decode()} but ignoring since inverter/enable_danger not Enabled"
                )
                return
    if topic in mqtt_set_config:
        last_value = mqtt_config.get(topic, {}).get("last_value")
        if (
            mqtt_config.get(topic, {}).get("topic_type") != "button"
            and last_value is not None
            and str(payload) == str(last_value)
        ):
            print(f"Received message: {msg.payload.decode()} (skipping write to {topic}: value unchanged)")
            return
        writing_queue.append((mqtt_set_config[topic], payload, topic))

    print(f"Received message: {msg.payload.decode()}")


def subscribe(client):
    for name, vals in mqtt_config.items():
        if not vals.get("enabled", True):
            continue

        # Check skip state before publishing discovery — avoids showing then hiding entities
        if "args" in vals:
            register = vals["args"].get("register")
            if register is not None:
                if not modbus.is_register_available(register):
                    _hidden_register_topics.add(name)
                    continue
                elif name in _hidden_register_topics:
                    # Register recovered since last connect — restore it
                    _hidden_register_topics.discard(name)

        topic = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{name}/state"
        field_name = f"{mqtt_topic}-{str(name).replace('/','-')}"

        if "command_topic" in vals["config"]:
            raw_cmd = vals["config"]["command_topic"]
            if not raw_cmd.startswith(mqtt_topic + "/"):
                raw_cmd = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{raw_cmd}/set"
                vals["config"]["command_topic"] = raw_cmd
            client.subscribe(raw_cmd)
            print(f"Subscribed to {raw_cmd}")

        discovery_data = {
            "device": device,
            "uniq_id": field_name,
            **{key: vals["config"][key] for key in vals["config"]},
        }
        if vals.get("topic_type", "sensor") != "button":
            discovery_data["state_topic"] = topic

        json_data = json.dumps(discovery_data)

        client.publish(
            f"homeassistant/{vals.get('topic_type', 'sensor')}/{field_name}/config",
            json_data,
            retain=True,
        )


def update_inverter_datetime():
    global last_datetime_sync
    if not datetime_sync_enabled:
        return
    if (
        last_datetime_sync is None
        or (time.time() - last_datetime_sync) > datetime_sync_interval
    ):
        modbus.write_system_date_time()
        last_datetime_sync = time.time()


# Create an instance of the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)

# Set callback functions for connection and message receipt
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message


# Set username and password for MQTT client using environment variables from .env file
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
host = os.getenv("MQTT_HOST") or ""
port = int(os.getenv("MQTT_PORT") or 1883)

if not username or not password:
    raise ValueError("Missing MQTT_USERNAME or MQTT_PASSWORD in .env file")

client.username_pw_set(username, password)


# Connect to the MQTT server, retrying with backoff if the broker is unavailable
_retry_delay = 1
while True:
    try:
        client.connect(host, port)
        break
    except Exception as e:
        print(f"MQTT connection failed: {e} — retrying in {_retry_delay}s")
        time.sleep(_retry_delay)
        _retry_delay = min(_retry_delay * 2, 60)

loop_sleep: float = int(os.getenv("LOOP_SLEEP") or 200) / 1000
general_interval: float = int(os.getenv("GENERAL_INTERVAL") or 5000) / 1000
refresh_interval: float = int(os.getenv("REFRESH_INTERVAL") or 5000) / 1000
max_reads_per_loop: int = int(os.getenv("MAX_READS_PER_LOOP") or 20)

# Add these variables before the while loop
running = True


def signal_handler(signum, frame):
    global running
    print("\nSignal received. Cleaning up...")
    running = False


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Stagger initial update times so all entries fire within the first 60 seconds,
# spread evenly to avoid bus saturation.
# Formula: last_update = now - interval + jitter  →  due in jitter seconds (0..60s).
# Previous formula (now - jitter) was wrong for long intervals: a 600s entry with
# jitter=5 would not fire for another 595 seconds.
_now = time.time()
_JITTER_MAX = 60.0
for _vals in mqtt_config.values():
    _interval = _vals.get("interval")
    if _interval and _interval > 0:
        _vals["last_update"] = _now - _interval + random.uniform(0, min(_interval, _JITTER_MAX))

# Loop continuously sending data to Home Assistant
client.loop_start()

# Wait for on_connect to fire so subscribe() re-publishes all current discovery topics
# before clearing stale ones — avoids a window where authorization could be affected.
time.sleep(2.0)

# Clear stale HA discovery topics from previous runs using a separate temporary
# MQTT client so the cleanup is fully isolated from the main connection.
_current_disc = {
    f"homeassistant/{vals.get('topic_type', 'sensor')}/{mqtt_topic}-{name.replace('/', '-')}/config"
    for name, vals in mqtt_config.items()
    if vals.get("enabled", True)
}
try:
    _stale: list = []
    _clean = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
    _clean.username_pw_set(username, password)

    def _disc_collector(c, u, msg):
        parts = msg.topic.split("/")
        if (
            len(parts) == 4
            and parts[2].startswith(f"{mqtt_topic}-")
            and msg.payload
            and msg.topic not in _current_disc
        ):
            _stale.append(msg.topic)

    _clean.on_message = _disc_collector
    _clean.connect(host, port)
    _clean.subscribe("homeassistant/+/+/config")
    _end = time.time() + 1.0
    while time.time() < _end:
        _clean.loop(timeout=0.1)
    for _topic in _stale:
        _clean.publish(_topic, "", retain=True)
    _clean.disconnect()
    if _stale:
        print(f"Cleared {len(_stale)} stale HA discovery topics: {_stale}")
except Exception as e:
    print(f"Stale discovery cleanup skipped: {e}")

while running:
    try:
        # check if we need to update values
        if len(writing_queue) > 0:
            for set_fuction, payload, topic in writing_queue:
                returnval = set_fuction(payload)
                if returnval == "update_value":
                    print("Handling update_value for " + topic)
                    mqtt_config[topic]["last_value"] = payload
                if returnval != None:
                    interval = mqtt_config[topic].get("interval") or 0
                    current_time = time.time()
                    mqtt_config[topic]["last_update"] = (
                        current_time - interval + refresh_interval
                    )
                    if topic == "battery/type":
                        publish_equalization_availability(client)

            writing_queue = []
            time.sleep(loop_sleep)

        modbus_reads_this_loop = 0
        for name, vals in mqtt_config.items():
            if (
                not vals.get("enabled", True)
                or vals.get("topic_type", "sensor") == "button"
            ):
                continue
            last_update = vals.get("last_update")
            interval = vals.get("interval")
            current_time = time.time()
            if last_update is not None:
                if interval == -1:
                    continue
                if current_time - last_update <= interval:
                    continue

            is_modbus_read = "args" in vals
            if is_modbus_read:
                register = vals["args"].get("register")
                if register is not None:
                    if not modbus.is_register_available(register):
                        if name not in _hidden_register_topics:
                            _hidden_register_topics.add(name)
                            _hide_topic(client, name, vals)
                        continue
                    if name in _hidden_register_topics:
                        _hidden_register_topics.discard(name)
                        _restore_topic(client, name, vals)
                if modbus_reads_this_loop >= max_reads_per_loop:
                    continue
                modbus_reads_this_loop += 1

            debug(f"updating {name}")
            topic = f"{mqtt_topic}/{vals.get('topic_type', 'sensor')}/{name}/state"
            if is_modbus_read:
                vals["args"]["name"] = vals["config"]["name"]
                value = vals["value"](**vals["args"])
            else:
                value = vals["value"]()
            if value is not None and is_modbus_read:
                register = vals["args"].get("register")
                if register is not None and not _is_value_in_range(value, vals):
                    debug(f"Out-of-range value for {name}: {value}")
                    modbus.record_invalid_value(register)
                    value = None
            if value != None:
                mqtt_config[name]["last_update"] = current_time
                mqtt_config[name]["last_value"] = value
                publishing_queue.append((topic, value))

        if len(publishing_queue) > 0:
            for topic, value in publishing_queue:
                client.publish(topic, value)
            publishing_queue = []

        modbus.check_reconnect()
        update_inverter_datetime()
        publish_equalization_availability(client)
        time.sleep(loop_sleep)

    except Exception as e:
        print(f"Loop error: {e}")
        publishing_queue = []
        time.sleep(5)

# Clean up
print("Disconnecting from MQTT broker...")
client.loop_stop()
client.disconnect()
sys.exit(0)
