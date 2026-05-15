# Modbus to MQTT for Home Assistant

## Description

This project reads data from an SRNE hybrid solar inverter using Modbus RTU and publishes it to an MQTT broker for integration with Home Assistant. It supports a wide range of SRNE inverter models and exposes sensor, number, select, switch, text, and button entities via MQTT discovery.

Features include:

- **Full register coverage** — sensors, controls, and statistics for DC data, inverter data, battery, PV, grid, load, generator port, BMS, and grid protection parameters
- **Automatic register skip** — registers that fail to read or return out-of-range values are automatically skipped and their HA entities removed, then retried periodically
- **Equalization availability** — equalization controls are only exposed when a lead-acid battery type is configured
- **Write deduplication** — writes to Modbus are skipped if the value matches the last known value, reducing EEPROM wear
- **Lovelace dashboard** — a ready-to-use dashboard template plus a script to generate a filtered version that omits unsupported registers

---

## Configuration

Create a `.env` file in the root directory with the following settings:

```sh
MQTT_HOST=                                       # MQTT broker hostname or IP
MQTT_PORT=1883                                   # MQTT broker port
MQTT_USERNAME=                                   # MQTT username
MQTT_PASSWORD=                                   # MQTT password
MQTT_TOPIC=srne1                                 # Device topic prefix (becomes the HA device name)

DEBUG=false                                      # Set true for verbose register read logging

DEVICE_MANUFACTURER=SRNE                         # Shown as manufacturer in HA device info
MODBUS_ADDRESS=1                                 # Modbus device address (usually 1)
MODBUS_DEVICE=/dev/ttyUSB0                       # Serial port for Modbus RTU
MODBUS_BAUDRATE=9600                             # Serial baud rate
MODBUS_TIMEOUT=0.1                               # Seconds to wait for a register response (default 0.1)

SPLIT_PHASE=2                                    # Inverter phase count: 1, 2, or 3
PARALLEL=false                                   # false=single inverter, true=parallel (uses parallel registers),
                                                 # N=simulate parallel by multiplying single-inverter registers by N
NB_MPPT_TRACKERS=2                               # Number of connected MPPT inputs (0-6)
BATTERY_CONNECTED=true                           # Whether a battery is connected

HAS_AMBIENT_TEMPERATURE=false                    # Whether the inverter has an ambient temperature sensor

SYNC_DATETIME_ENABLED=true                       # Keep inverter clock in sync with host
SYNC_DATETIME_INTERVAL=60                        # How often to sync datetime, in minutes
TIMEZONE=                                        # Optional: e.g. America/New_York (defaults to system time)

PUBLISH_SYSTEM=true                              # Publish firmware/model info at startup

#### UPDATE INTERVALS (milliseconds) ####
PV_INTERVAL=1000                                 # Solar panel data
BATTERY_INTERVAL=5000                            # Battery data
LOAD_INTERVAL=10000                              # Load data
GRID_INTERVAL=10000                              # Grid data
INVETER_INTERVAL=10000                           # Inverter data
TEMPERATURE_INTERVAL=60000                       # Temperature sensors
GENERAL_INTERVAL=60000                           # Settings and configuration registers
STATISTICS_INTERVAL=300000                       # Energy totals — 5 min default, rarely need faster
SYSTEM_INTERVAL=600000                           # Firmware/model info
REFRESH_INTERVAL=200                             # Delay before re-reading a register after writing it
LOOP_SLEEP=200                                   # Milliseconds between main loop iterations

#### ADVANCED TUNING ####
MAX_READS_PER_LOOP=20                            # Cap on Modbus reads per loop iteration (prevents bus saturation)
MODBUS_SKIP_THRESHOLD=5                          # Consecutive failures before a register is skipped
MODBUS_SKIP_RETRY_INTERVAL=3600                  # Seconds before a skipped register is retried (default 1 hour)
MODBUS_SKIP_STATE_FILE=register_skip_state.json  # File to persist skip state across restarts
```

---

## Installation

```sh
git clone https://github.com/timbit123/srne-modbus
cd srne-modbus
python3 -m venv ./venv
./venv/bin/pip3 install -r requirements.txt
```

Create and configure the `.env` file, then run:

```sh
./venv/bin/python3 main.py
```

---

## Running as a systemd Service

Create `/etc/systemd/system/srne-modbus.service`:

```ini
[Unit]
Description=SRNE Modbus to MQTT
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5s
User=<user>
WorkingDirectory=<path>/srne-modbus
Environment=PYTHONUNBUFFERED=1
ExecStart=<path>/srne-modbus/venv/bin/python3 main.py

[Install]
WantedBy=multi-user.target
```

Enable and start:

```sh
sudo systemctl enable srne-modbus.service
sudo systemctl start srne-modbus.service
```

---

## Automatic Register Skip

Some registers are not supported by all firmware versions or inverter models. Rather than flooding the Modbus bus with retries or showing unavailable entities in HA, the script automatically detects and handles these:

- **Communication failures** — if a register fails to respond `MODBUS_SKIP_THRESHOLD` times consecutively, it is marked as skipped
- **Out-of-range values** — if a number register returns a value outside its configured min/max (e.g. a firmware default of 585V for a grid protection threshold), it is also counted as a failure
- **HA entity removal** — when a register is skipped, its Home Assistant discovery entry is cleared so the entity disappears from HA
- **Automatic retry** — after `MODBUS_SKIP_RETRY_INTERVAL` seconds (default 1 hour), the register is tried again; if it now succeeds, the HA entity is re-announced
- **Persistent state** — skip state is saved to `register_skip_state.json` so registers that failed in a previous run are not retried on startup until their retry interval has elapsed

To reset skip state and retry all registers immediately, delete `register_skip_state.json` and restart the script.

---

## Lovelace Dashboard

Two dashboard files are provided:

| File | Purpose |
|---|---|
| `lovelace-dashboard.yaml` | Full template — all entities including potentially unsupported ones |
| `lovelace-dashboard-current.yaml` | Generated — filtered to only show entities whose registers are working |

### Generating the filtered dashboard

```sh
cd /path/to/srne-modbus
python3 generate_dashboard.py
```

Options:

```
--output FILE        Output path (default: lovelace-dashboard-current.yaml)
--mqtt-topic TOPIC   Override MQTT_TOPIC from .env
--skip-state FILE    Path to skip state JSON (default: register_skip_state.json)
--template FILE      Template dashboard to filter (default: lovelace-dashboard.yaml)
```

Re-run after the script has been running for a while (once unsupported registers have been identified and persisted to `register_skip_state.json`) to get the cleanest dashboard.

### Installing the dashboard in Home Assistant

1. In HA, go to **Settings → Dashboards → Add Dashboard**
2. Choose **YAML mode**
3. Paste the contents of `lovelace-dashboard-current.yaml` (or the full template)

### Required HACS integrations

Install these via **HACS → Frontend**:

| Card | URL | Required for |
|---|---|---|
| `custom:power-flow-card-plus` | https://github.com/flixlix/power-flow-card-plus | Power flow diagram on Overview |
| `custom:fold-entity-row` | https://github.com/thomasloven/lovelace-fold-entity-row | Collapsible sections in Settings |

---

## Dangerous Controls

Some inverter controls (power off, reset, clear statistics) are gated behind a safety switch. To access them:

1. In the Settings view, find **Enable Danger Controls** and set it to **Enabled**
2. The **Danger Zone** section will appear at the bottom of Settings with the protected controls

---

## Multi-Inverter Setup

Run a separate instance of the script for each inverter, each with its own `.env` file specifying a unique `MQTT_TOPIC`, `MODBUS_DEVICE` (serial port), and `MODBUS_ADDRESS`. Each instance creates its own HA device with its own set of entities.

If multiple inverters share the same RS-485 bus, they must have different `MODBUS_ADDRESS` values and use the same `MODBUS_DEVICE`. If they are on separate serial adapters, each instance gets its own `MODBUS_DEVICE` path.
