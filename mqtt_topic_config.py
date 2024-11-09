import os
from dotenv import load_dotenv
import modbus

load_dotenv()

device = {
    "name": os.getenv("MQTT_TOPIC"),
    "identifiers": [modbus.read_serial_number()],
    "manufacturer": os.getenv("DEVICE_MANUFACTURER"),
    "serial_number": modbus.read_serial_number(),
    "model": f"{modbus.read_model()}",
}

system_enabled: bool = True if os.getenv("PUBLISH_SYSTEM") == "true" else False
battery_enabled: bool = True if os.getenv("BATTERY_CONNECTED") == "true" else False
split_phase: int = int(os.getenv("SPLIT_PHASE")) if os.getenv("SPLIT_PHASE") else 2
has_ambient_temperature: bool = (
    True if os.getenv("HAS_AMBIENT_TEMPERATURE") == "true" else False
)
pv_mpp_trackers: int = (
    int(os.getenv("NB_MPP_TRACKERS")) if os.getenv("NB_MPP_TRACKERS") else 0
)

pv_interval: float = (
    int(os.getenv("PV_INTERVAL")) if os.getenv("PV_INTERVAL") else 1000
) / 1000
battery_interval: float = (
    int(os.getenv("BATTERY_INTERVAL")) if os.getenv("BATTERY_INTERVAL") else 1000
) / 1000
load_interval: float = (
    int(os.getenv("LOAD_INTERVAL")) if os.getenv("LOAD_INTERVAL") else 1000
) / 1000
grid_interval: float = (
    int(os.getenv("GRID_INTERVAL")) if os.getenv("GRID_INTERVAL") else 1000
) / 1000
inverter_interval: float = (
    int(os.getenv("INVETER_INTERVAL")) if os.getenv("INVETER_INTERVAL") else 1000
) / 1000
statistics_interval: float = (
    int(os.getenv("STATISTICS_INTERVAL")) if os.getenv("STATISTICS_INTERVAL") else 1000
) / 1000
temperature_interval: float = (
    int(os.getenv("TEMPERATURE_INTERVAL"))
    if os.getenv("TEMPERATURE_INTERVAL")
    else 5000
) / 1000
general_interval: float = (
    int(os.getenv("GENERAL_INTERVAL")) if os.getenv("GENERAL_INTERVAL") else 5000
) / 1000
system_interval: int = -1  # will fetch data one time only

mqtt_set_config: dict[str, any] = {
    "charging/pv_current_limit": modbus.write_pv_charging_current_limit,
    "charging/voltage_back_to_battery": modbus.write_battery_charging_return_voltage,
    "charging/voltage_limit": modbus.write_battery_charge_limit_voltage,
    "charging/voltage_balancing": modbus.write_battery_balancing_voltage,
    "charging/source_priority": modbus.write_charging_source_priority,
    "charging/overcharge_voltage": modbus.write_battery_overcharge_voltage,
    "charging/float_voltage": modbus.write_battery_float_charge_voltage,
    "charging/overdischarge_return_voltage": modbus.write_battery_overdischarge_return_voltage,
    "charging/undervoltage_warning_voltage": modbus.write_battery_undervoltage_warning,
    "charging/discharge_limit_voltage": modbus.write_battery_discharge_limit_voltage,
    "charging/stop_discharge_soc_limit": modbus.write_battery_stop_state_of_charge,
    "charging/stop_charging_soc_limit": modbus.write_stop_charging_soc_set,
    "charging/total_charging_current_limit": modbus.write_total_charging_current_limit,
    "inverter/power_saving": modbus.write_power_saving_mode,
    "inverter/output_priority": modbus.write_output_priority,
}

mqtt_config: dict[str, dict[str, any]] = {
    "system/build_time": {
        "enabled": system_enabled,
        "value": modbus.read_cpu_build_time,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Build time",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/read_minor_version": {
        "enabled": system_enabled,
        "value": modbus.read_minor_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Minor version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/app_version": {
        "enabled": system_enabled,
        "value": modbus.read_app_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "App version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/bootloader_version": {
        "enabled": system_enabled,
        "value": modbus.read_bootloader_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Bootloader version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/control_panel_version": {
        "enabled": system_enabled,
        "value": modbus.read_control_panel_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Control Panel version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/power_amplifier_version": {
        "enabled": system_enabled,
        "value": modbus.read_power_amplifier_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Power Amplifier version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/rs485_version": {
        "enabled": system_enabled,
        "value": modbus.read_rs485_version,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/rs485_address": {
        "enabled": system_enabled,
        "value": modbus.read_rs485_address,
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 address",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    ############ Battery #####################
    "battery/soc": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_soc,
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Battery level",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "device_class": "battery",
        },
    },
    "battery/voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage,
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Battery voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "battery/current": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_current,
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Battery current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "battery/temperature": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_temperature,
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Battery temperature",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    ############ PV1 #####################
    "pv1/voltage": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv1_voltage,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "pv1/current": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv1_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "pv1/charge_power": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv1_charge_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 charge power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ PV2 #####################
    "pv2/voltage": {
        "enabled": pv_mpp_trackers >= 2,
        "value": modbus.read_pv2_voltage,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "pv2/current": {
        "enabled": pv_mpp_trackers >= 2,
        "value": modbus.read_pv2_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "pv2/charge_power": {
        "enabled": pv_mpp_trackers >= 2,
        "value": modbus.read_pv2_charge_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 charge power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ PV #####################
    "pv/total_power": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv_total_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV total power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "pv/charging_current": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv_charging_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV charging current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    ############ Grid #####################
    "grid/voltage_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_voltage_a,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid voltage A",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "grid/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_current_a,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "grid/frequency": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_frequency,
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid frequency",
            "icon": "mdi:pulse",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
        },
    },
    "grid/power_a": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["grid/voltage_a"]["last_value"]
            * mqtt_config["grid/current_a"]["last_value"],
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid power A",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/voltage_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_grid_voltage_b,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid voltage B",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "grid/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_grid_current_b,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "grid/power_b": {
        "enabled": split_phase >= 2,
        "value": lambda: round(
            mqtt_config["grid/voltage_b"]["last_value"]
            * mqtt_config["grid/current_b"]["last_value"],
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid power B",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/voltage_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_grid_voltage_c,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid voltage C",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "grid/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_grid_current_c,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "grid/power_c": {
        "enabled": split_phase >= 3,
        "value": lambda: round(
            mqtt_config["grid/voltage_c"]["last_value"]
            * mqtt_config["grid/current_c"]["last_value"],
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid power c",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/total_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["grid/power_a"]["last_value"]
            + mqtt_config["grid/power_b"]["last_value"]
            + mqtt_config["grid/power_c"]["last_value"],
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Grid total power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ Inverter #####################
    "inverter/state": {
        "enabled": True,
        "value": modbus.read_machine_state,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter state",
            "icon": "mdi:information",
        },
    },
    "inverter/charging_power": {
        "enabled": True,
        "value": modbus.read_charging_power,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Charging power",
            "icon": "mdi:battery-charging",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "inverter/bus_voltage": {
        "enabled": True,
        "value": modbus.read_bus_voltage,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Bus voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/pbus_voltage": {
        "enabled": True,
        "value": modbus.read_pbus_voltage,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "PBus voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/nbus_voltage": {
        "enabled": True,
        "value": modbus.read_nbus_voltage,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "NBus voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/frequency": {
        "enabled": split_phase >= 1,
        "value": modbus.read_inverter_frequency,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter frequency",
            "icon": "mdi:sine-wave",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
        },
    },
    "inverter/voltage_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_inverter_voltage_a,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter voltage A",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_inverter_current_a,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/power_a": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["inverter/voltage_a"]["last_value"]
            * mqtt_config["inverter/current_a"]["last_value"],
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter power A",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "inverter/voltage_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_inverter_voltage_b,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter voltage B",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_inverter_current_b,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/power_b": {
        "enabled": split_phase >= 2,
        "value": lambda: round(
            mqtt_config["inverter/voltage_b"]["last_value"]
            * mqtt_config["inverter/current_b"]["last_value"],
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter power B",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "inverter/voltage_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_inverter_voltage_c,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter voltage C",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "inverter/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_inverter_current_c,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/power_c": {
        "enabled": split_phase >= 3,
        "value": lambda: round(
            mqtt_config["inverter/voltage_c"]["last_value"]
            * mqtt_config["inverter/current_c"]["last_value"],
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter power C",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "inverter/total_power": {
        "enabled": split_phase >= 1,
        "value": lambda: mqtt_config["inverter/power_a"]["last_value"]
        + mqtt_config["inverter/power_b"]["last_value"]
        + mqtt_config["inverter/power_c"]["last_value"],
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter total power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ Load ######################
    "load/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_current_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "load/active_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_active_power_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load active power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/reactive_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_reactive_power_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load reactive power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VAR",
            "device_class": "reactive_power",
        },
    },
    "load/power_a": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["inverter/voltage_a"]["last_value"]
            * mqtt_config["load/current_a"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load power A",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/ratio_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_ratio_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load ratio A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
        },
    },
    "load/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_current_b,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "load/active_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_active_power_b,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load active power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/reactive_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_reactive_power_b,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load reactive power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VAR",
            "device_class": "reactive_power",
        },
    },
    "load/power_b": {
        "enabled": split_phase >= 2,
        "value": lambda: round(
            mqtt_config["inverter/voltage_b"]["last_value"]
            * mqtt_config["load/current_b"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load power B",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/ratio_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_ratio_b,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load ratio B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
        },
    },
    "load/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_current_c,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "load/active_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_active_power_c,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load active power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/reactive_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_reactive_power_c,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load reactive power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VAR",
            "device_class": "reactive_power",
        },
    },
    "load/power_c": {
        "enabled": split_phase >= 3,
        "value": lambda: round(
            mqtt_config["inverter/voltage_c"]["last_value"]
            * mqtt_config["load/current_c"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_value": 0,
        "last_update": None,
        "config": {
            "name": "Load power C",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/ratio_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_ratio_c,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load ratio C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
        },
    },
    "load/total_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["load/power_a"]["last_value"]
            + mqtt_config["load/power_b"]["last_value"]
            + mqtt_config["load/power_c"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load total power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ Charging Configuration #####################
    "charging/pv_current_limit": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv_charging_current_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "PV Current Limit for charging",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "A",
            "device_class": "current",
            "entity_category": "config",
            "min": 0,
            "max": 200,
            "step": 0.1,
            "command_topic": "charging/pv_current_limit",
        },
    },
    "charging/voltage_back_to_battery": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_charging_return_voltage,
        "interval": battery_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Back to battery voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/voltage_back_to_battery",
        },
    },
    "charging/voltage_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_charge_limit_voltage,
        "interval": battery_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery voltage charge limit",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/voltage_limit",
        },
    },
    "charging/voltage_balancing": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_balancing_voltage,
        "interval": battery_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery balancing voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/voltage_balancing",
        },
    },
    "charging/source_priority": {
        "value": modbus.read_charging_source_priority,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Charging Source Priority",
            "icon": "mdi:import",
            "options": [
                "Solar first",
                "Utility first",
                "Solar and utility simultaneously",
                "Solar only",
            ],
            "command_topic": "charging/source_priority",
        },
    },
    "charging/overcharge_voltage": {
        "value": modbus.read_battery_overcharge_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery overcharge voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/overcharge_voltage",
        },
    },
    "charging/float_voltage": {
        "value": modbus.read_battery_float_charge_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery float charge voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/float_voltage",
        },
    },
    "charging/overdischarge_return_voltage": {
        "value": modbus.read_battery_overdischarge_return_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery back from overdischarge voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/overdischarge_return_voltage",
        },
    },
    "charging/undervoltage_warning_voltage": {
        "value": modbus.read_battery_undervoltage_warning,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery undervoltage warning",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/undervoltage_warning_voltage",
        },
    },
    "charging/discharge_limit_voltage": {
        "value": modbus.read_battery_discharge_limit_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery discharge limit",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/discharge_limit_voltage",
        },
    },
    "charging/stop_discharge_soc_limit": {
        "value": modbus.read_battery_stop_state_of_charge,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery SOC discharge cutoff",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/stop_discharge_soc_limit",
        },
    },
    "charging/stop_charging_soc_limit": {
        "value": modbus.read_stop_charging_soc_set,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery SOC stop charging",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/stop_charging_soc_limit",
        },
    },
    "charging/total_charging_current_limit": {
        "value": modbus.read_total_charging_current_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery total charging current limit",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "min": 0,
            "max": 200,
            "step": 0.1,
            "command_topic": "charging/total_charging_current_limit",
        },
    },
    # "charging/": {},
    "inverter/power_saving": {
        "value": modbus.read_power_saving_mode,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Power Saving",
            "icon": "mdi:leaf",
            "state_off": 0,
            "state_on": 1,
            "payload_off": 0,
            "payload_on": 1,
            "command_topic": "inverter/power_saving",
        },
    },
    "inverter/output_priority": {
        "value": modbus.read_output_priority,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Output priority",
            "icon": "mdi:export",
            "options": ["Solar first", "Utility first", "Solar/Battery/Utility"],
            "command_topic": "inverter/output_priority",
        },
    },
    # "battery/shutdown_voltage": {},
    ############ Temperatures #####################
    "temperature/dc_dc": {
        "value": modbus.read_temperature_dc_dc,
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature DC-DC",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    "temperature/dc_ac": {
        "value": modbus.read_temperature_dc_ac,
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature DC-AC",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    "temperature/transformer": {
        "value": modbus.read_temperature_transformer,
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature transformer",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    "temperature/ambient": {
        "enabled": has_ambient_temperature,
        "value": modbus.read_temperature_ambient,
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature ambient",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    ############ Statistics Configuration #####################
    "statistics/daily_generated_energy_to_grid": {
        "value": modbus.read_total_generated_energy_to_grid_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Generated Energy to Grid",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
    "statistics/daily_battery_charged": {
        "value": modbus.read_total_battery_charged_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Battery Charged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
        },
    },
    "statistics/daily_battery_discharged": {
        "value": modbus.read_total_battery_discharged_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Battery Discharged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
        },
    },
    "statistics/daily_pv_production": {
        "value": modbus.read_total_pv_power_generated_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily PV Power Generated",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
    "statistics/daily_grid_consumed": {
        "value": modbus.read_total_grid_consumed_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
    "statistics/daily_grid_charged": {
        "value": modbus.read_total_grid_charged_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Battery Charging",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
        },
    },
    "statistics/daily_load_consumed": {
        "value": modbus.read_total_load_consumed_today,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
}
