# Modbus to MQTT for Home Assistant

## Description
This project reads data from an SRNE device using Modbus protocol v1.96 and publishes the data to a MQTT broker for integration with Home Assistant. 

This is still a work in progress and contributions are welcome!
Most of the registry are done, I would say around 90%. Then I will add more data to home assistant.

Right now, data is sent to a MQTT broker but I might want to add my own dashboard. 

I'm also considering adding support for JKBMS devices as well later on.

## Configuration
Create a `.env` file in the root directory of your project with the following configurations:


```sh
MQTT_HOST= #MQTT Broker Hostname or IP address
MQTT_PORT= #MQTT Broker Port (default is 1883)
MQTT_USERNAME= #The username for the MQTT broker.
MQTT_PASSWORD= #The password for the MQTT broker.
MQTT_TOPIC=srne1 #The MQTT topic to publish the data to.

DEBUG=false

DEVICE_MANUFACTURER=SRNE #Manufacturer of the device, name will be displayed in Home Assistant as device.
MODBUS_ADDRESS=1 #Modbus address of the device (usually 1)
SPLIT_PHASE=2 #Number of phase for the inverter (1,2,3)
NB_MPP_TRACKERS=1 #Number of MPPT tracker connected (0,1,2)
BATTERY_CONNECTED=true #Is a battery connected (true,false)

HAS_AMBIENT_TEMPERATURE=false # does the inverter has ambient temperature sensor (true/false)

SYNC_DATETIME_ON_STARTUP=true #Update datetime during startup with the inverter (true,false)

PUBLISH_SYSTEM=true # publish system information to mqtt at statup (true,false)
LOOP_SLEEP=5

#### UPDATE INTERVALS ####
PV_INTERVAL=1000 # time in ms between data update
BATTERY_INTERVAL=1000 # time in ms between data update
LOAD_INTERVAL=2000
GRID_INTERVAL=2000
INVETER_INTERVAL=2000
TEMPERATURE_INTERVAL=5000 # time in ms between data update
GENERAL_INTERVAL=5000 # time in ms between data update
STATISTICS_INTERVAL=60000
LOOP_SLEEP=200 # time in ms to sleep after a full loop. too small value could crash the modbus communication (default is 200ms)

```
## Installation
1. Install the required dependencies:
```sh
pip install -r requirements.txt
```

2. Create and configure the `.env` file as described above.

## Usage
Run the script to start reading data from the SRNE device and publishing it to the MQTT broker:
```sh
python [main.py]
```

## TODOs
- Add service to run on boot (systemd)
- Add remaining modbus registers
- Add remaining MQTT topics read/writes

## TODOs v2
- Add JKBMS
- Create webserver with better graphs and data visualization