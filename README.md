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
MODBUS_DEVICE="/dev/ttyUSB0" #tty port to use for modbus communication
SPLIT_PHASE=2 #Number of phase for the inverter (1,2,3)
NB_MPPT_TRACKERS=1 #Number of MPPT tracker connected (0,1,2)
BATTERY_CONNECTED=true #Is a battery connected (true,false)

HAS_AMBIENT_TEMPERATURE=false # does the inverter has ambient temperature sensor (true/false)

SYNC_DATETIME_ENABLED=true #Update datetime from interval
SYNC_DATETIME_INTERVAL=60 #Update inverter datetime every 60 minutes
#If empty, system will use local time. If not, you can specify your timezone (e.g., "America/New_York")
TIMEZONE=

PUBLISH_SYSTEM=true # publish system information to mqtt at statup (true,false)

#### UPDATE INTERVALS ####
PV_INTERVAL=1000 # time in ms between data update
BATTERY_INTERVAL=1000 # time in ms between data update
LOAD_INTERVAL=2000
GRID_INTERVAL=2000
INVETER_INTERVAL=2000
TEMPERATURE_INTERVAL=5000 # time in ms between data update
GENERAL_INTERVAL=5000 # time in ms between data update
REFRESH_INTERVAL=1000 # time before updating a value that was just set
STATISTICS_INTERVAL=60000
LOOP_SLEEP=200 # time in ms to sleep after a full loop. too small value could crash the modbus communication (default is 200ms)

```

## Installation

1. Clone project and setup venv with the required dependencies:

```sh
git clone https://github.com/timbit123/srne-modbus
cd srne-modbus
python3 -m venv ./venv
./venv/bin/pip3 install -r requirements.txt
```

2. Create and configure the `.env` file as described above.

## Usage

Run the script to start reading data from the SRNE device and publishing it to the MQTT broker:

```sh
./venv/bin/python3 [main.py]
```

## Setup to Run Automatically on Boot

If your OS uses systemd, you can create a service file that will start the script automatically on boot and restart it if it crashes:

```sh
[Unit]
Description=SRNE Modbus
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5s
User=<user script will run as>
WorkingDirectory=<path where project was cloned>/srne-modbus
ExecStart=<path where project was cloned>/srne-modbus/venv/bin/python3 main.py

[Install]
WantedBy=multi-user.target
```

Place the file at /etc/systemd/system/srne-modbus.service, then enable and start by running:

```sh
sudo systemctl enable srne-modbus.service
sudo systemctl start srne-modbus.service
```

## TODOs

- Add remaining modbus registers
- Add remaining MQTT topics read/writes

## TODOs v2

- Add JKBMS
- Create webserver with better graphs and data visualization
