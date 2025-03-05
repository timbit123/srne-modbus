import os
from dotenv import load_dotenv
import modbus

load_dotenv()

device = {
    "name": os.getenv("MQTT_TOPIC"),
    "identifiers": [modbus.read_register_str(0x035, "Serial Number", clean = True)],
    "manufacturer": os.getenv("DEVICE_MANUFACTURER"),
    "serial_number": modbus.read_register_str(0x035, "Serial Number", clean = True),
    "model": modbus.read_register_value(0x01B, "Model", integer = True),
}

system_enabled: bool = True if os.getenv("PUBLISH_SYSTEM") == "true" else False
battery_enabled: bool = True if os.getenv("BATTERY_CONNECTED") == "true" else False
split_phase: int = int(os.getenv("SPLIT_PHASE")) if os.getenv("SPLIT_PHASE") else 2
has_ambient_temperature: bool = (
    True if os.getenv("HAS_AMBIENT_TEMPERATURE") == "true" else False
)
pv_mppt_trackers: int = (
    int(os.getenv("NB_MPPT_TRACKERS")) if os.getenv("NB_MPPT_TRACKERS") else 0
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
system_interval: float = (
    int(os.getenv("SYSTEM_INTERVAL")) if os.getenv("SYSTEM_INTERVAL") else 600000
) / 1000

mqtt_set_config: dict[str, any] = {
    "charging/pv_current_limit": modbus.write_pv_charging_current_limit,
    "charging/voltage_limit": modbus.write_battery_charge_limit_voltage,
    "charging/overvoltage_limit": modbus.write_battery_overvoltage_protection_voltage,
    "charging/bulk_charge_time": modbus.write_battery_bulk_charge_time,
    "charging/bulk_voltage": modbus.write_battery_bulk_voltage,
    "charging/rebulk_voltage": modbus.write_battery_rebulk_voltage,
    "charging/overdischarge_return_voltage": modbus.write_battery_overdischarge_return_voltage,
    "charging/undervoltage_warning_voltage": modbus.write_battery_undervoltage_warning,
    "charging/discharge_limit_voltage": modbus.write_battery_discharge_limit_voltage,
    "charging/overdicharge_limit": modbus.write_battery_overdischarge_limit,
    "charging/stop_discharge_soc_limit": modbus.write_battery_stop_state_of_charge,
    "charging/stop_grid_discharge_soc_limit": modbus.write_battery_soc_switch_to_line,
    "charging/restart_grid_discharge_soc_limit": modbus.write_battery_soc_switch_to_battery,
    "charging/stop_charging_soc_limit": modbus.write_stop_charging_soc_set,
    "charging/total_charging_current_limit": modbus.write_total_charging_current_limit,
    "charging/stop_charging_current_limit": modbus.write_stop_charging_current_limit,
    "charging/source_priority": modbus.write_charging_source_priority,
    "charging/bms_communication": modbus.write_bms_communication_enabled,
    "charging/charging_limit_mode": modbus.write_bms_charging_limit_current_mode_setting,
    "charging/bms_protocol": modbus.write_bms_protocol,
    "charging/time_charge_enabled": modbus.write_time_charge_enabled,
    "inverter/power_saving": modbus.write_power_saving_mode,
#    "inverter/output_priority": modbus.write_output_priority,
    "inverter/hybrid_mode": modbus.write_hybrid_mode,
    "inverter/battery_priority": modbus.write_battery_discharge_enabled,
    "pv/power_priority": modbus.write_pv_power_priority_set,
    "inverter/enable_danger": lambda x: "update_value",
    "inverter/reset": modbus.write_reset,
    "inverter/clear_statistics": modbus.write_restore_factory_setting,
    "inverter/clear_errors": modbus.write_restore_factory_setting,
}

mqtt_config: dict[str, dict[str, any]] = {
    "system/build_time": {
        "enabled": system_enabled,
        "value": modbus.read_register_str,
        "args": {
            "register": 0x021, 
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Build Time",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/serial_number": {
        "enabled": system_enabled,
        "value": modbus.read_register_str,
        "args": {
            "register": 0x035, 
            "clean" : True
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Serial Number",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/read_minor_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x00A, 
            "integer": True
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Minor Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/app_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x014, 
            "scale" : 1e-2,
            "prefix" : "v"
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "App Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/bootloader_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x015, 
            "scale" : 1e-2,
            "prefix" : "v"
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Bootloader Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/control_panel_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x016, 
            "scale" : 1e-2,
            "prefix" : "v"
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Control Panel Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/power_amplifier_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x017, 
            "scale" : 1e-2,
            "prefix" : "v"
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Power Amplifier Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/rs485_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x01C, 
            "scale" : 1e-2,
            "prefix" : "v"
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/model": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x01B, 
            "integer" : True
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Model",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    "system/rs485_address": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x01A, 
            "integer" : True
        },
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 Address",
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
            "name": "Battery SOC",
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
            "name": "Battery Voltage",
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
            "name": "Battery Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "battery/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["battery/current"]["last_value"]
            * mqtt_config["battery/voltage"]["last_value"],
            1,
        ),
        "interval": battery_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Battery Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "battery/temperature": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_temperature,
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Battery Temperature",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
        },
    },
    "battery/charge_state": {
        "enabled": battery_enabled,
        "value": modbus.read_charging_state,
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Charge State",
            "icon": "mdi:information",
        },
    },
    ############ PV1 #####################
    "pv1/voltage": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv1_voltage,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "pv1/current": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv1_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },

    "pv1/power": {
        "enabled": pv_mpp_trackers >= 1,
        "value": modbus.read_pv1_charge_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ PV2 #####################
    "pv2/voltage": {
        "enabled": pv_mppt_trackers >= 2,
        "value": modbus.read_pv2_voltage,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "pv2/current": {
        "enabled": pv_mppt_trackers >= 2,
        "value": modbus.read_pv2_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },

    "pv2/power": {
        "enabled": pv_mpp_trackers >= 2,
        "value": modbus.read_pv2_charge_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ PV #####################

    "pv/total_power": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv_total_power,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV Total Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "pv/charging_current": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv_charging_current,
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV Charging Current",
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
            "name": "Grid Voltage A",
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
            "name": "Grid Current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
  #If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    "ct/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_active_power_a,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "CT Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "home/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x240,
            "unit": "W"
        },
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/apparent_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_apparent_power_a,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "grid/frequency": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_frequency,
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Frequency",
            "icon": "mdi:pulse",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
        },
    },
    "grid/power_a": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["ct/power_a"]["last_value"])
            - float(mqtt_config["home/power_a"]["last_value"]),
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Power A",
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
            "name": "Grid Voltage B",
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
            "name": "Grid Current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
#If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    "ct/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_grid_active_power_b,
        "interval": grid_interval,
        "last_update": None,

        "last_value": 0,
        "config": {
            "name": "CT Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },

    "home/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x241,
            "unit": "W"
        },
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/apparent_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_grid_apparent_power_b,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "grid/power_b": {
        "enabled": split_phase >= 2,
        "value": lambda: round(
            float(mqtt_config["ct/power_b"]["last_value"])
            - float(mqtt_config["home/power_b"]["last_value"]),
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Power B",
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
            "name": "Grid Voltage C",
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
            "name": "Grid Current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
#If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    "ct/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_grid_active_power_c,
        "interval": grid_interval,
        "last_update": None,

        "last_value": 0,
        "config": {
            "name": "CT Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "home/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x242,
            "unit": "W"
        },
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/apparent_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_grid_apparent_power_c,
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "grid/power_c": {
        "enabled": split_phase >= 3,
        "value": lambda: round(
            float(mqtt_config["ct/power_c"]["last_value"])
            - float(mqtt_config["home/power_c"]["last_value"]),
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Power C",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "ct/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["ct/power_a"]["last_value"]
            + mqtt_config["ct/power_b"]["last_value"]
            + mqtt_config["ct/power_c"]["last_value"],
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "CT Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "home/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["home/power_a"]["last_value"])
            + float(mqtt_config["home/power_b"]["last_value"])
            + float(mqtt_config["home/power_c"]["last_value"]),
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Home Load Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "grid/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["grid/apparent_power_a"]["last_value"]
            + mqtt_config["grid/apparent_power_b"]["last_value"]
            + mqtt_config["grid/apparent_power_c"]["last_value"],
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "grid/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["grid/power_a"]["last_value"]
            + mqtt_config["grid/power_b"]["last_value"]
            + mqtt_config["grid/power_c"]["last_value"],
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    ############ Inverter #####################
    "inverter/error": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args":
            {
                "register": 0x200,
                "integer": True,
                "format_str": "{:x}",
                "prefix" : "0x"
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Error Flags",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/failcode0": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args":
            {
                "register": 0x204,
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Fail Code 0",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/failcode1": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args":
            {
                "register": 0x205,
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Fail Code 1",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/failcode2": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args":
            {
                "register": 0x206,
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Fail Code 2",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/failcode3": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args":
            {
                "register": 0x207,
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Fail Code 3",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/grid_on_remain_time": {
        "enabled": True,
        #"value": modbus.read_grid_on_remain_time_state,
        "value": modbus.read_register_value,
        "args":
            {
                "register": 0x20F,
            },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Remaining Grid On Time",
            "icon": "mdi:information",
        },
    },
    "inverter/state": {
        "enabled": True,
        "value": modbus.read_machine_state,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter State",
            "icon": "mdi:information",
        },
    },
    "inverter/charging_power": {
        "enabled": True,
        "value": modbus.read_charging_power,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Charging Power",
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
            "name": "Bus Voltage",
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
            "name": "PBus Voltage",
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
            "name": "NBus Voltage",
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
            "name": "Inverter Frequency",
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
            "name": "Inverter Voltage A",
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
            "name": "Inverter Current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/apparent_power_a": {
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
            "name": "Inverter Apparent Power A",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "inverter/voltage_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_inverter_voltage_b,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Voltage B",
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
            "name": "Inverter Current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/apparent_power_b": {
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
            "name": "Inverter Apparent Power B",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "inverter/voltage_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_inverter_voltage_c,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Voltage C",
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
            "name": "Inverter Current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/apparent_power_c": {
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
            "name": "Inverter Apparent Power C",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "inverter/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: mqtt_config["inverter/apparent_power_a"]["last_value"]
        + mqtt_config["inverter/apparent_power_b"]["last_value"]
        + mqtt_config["inverter/apparent_power_c"]["last_value"],
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "inverter/parallel_current": {
        "enabled": True,
        "value": modbus.read_parallel_load_avg_current,
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Parallel Load Avg Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "inverter/auto_restart_on_overload": {
        "enabled": True,
        "value": modbus.read_auto_restart_on_overload,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Auto Restart on Overload",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/auto_restart_on_overheat": {
        "enabled": True,
        "value": modbus.read_auto_restart_on_overheat,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Auto Restart on Overheat",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    "inverter/auto_bypass_on_overload": {
        "enabled": True,
        "value": modbus.read_bypass_on_overload,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Auto Bypass on Overload",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    ############ Load ######################
    "load/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_current_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Current A",
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
        "last_value": 0,
        "config": {
            "name": "Load Active Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_active_power_a,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/apparent_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_apparent_power_a,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "load/grid_charging_current": {
        "enabled": split_phase >= 1,
        "value": modbus.read_grid_charging_current,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Grid Charging Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
        },
    },
    "load/ratio_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_load_ratio_a,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio A",
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
            "name": "Load Current B",
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
        "last_value": 0,
        "config": {
            "name": "Load Active Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_active_power_b,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/apparent_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_apparent_power_b,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "load/ratio_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_load_ratio_b,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio B",
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
            "name": "Load Current C",
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
        "last_value": 0,
        "config": {
            "name": "Load Active Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_active_power_c,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/apparent_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_apparent_power_c,
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    "load/ratio_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_load_ratio_c,
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
        },
    },
    "load/active_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["load/active_power_a"]["last_value"]
            + mqtt_config["load/active_power_b"]["last_value"]
            + mqtt_config["load/active_power_c"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Total Active Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/power": {
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
            "name": "Load Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
        },
    },
    "load/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            mqtt_config["load/apparent_power_a"]["last_value"]
            + mqtt_config["load/apparent_power_b"]["last_value"]
            + mqtt_config["load/apparent_power_c"]["last_value"],
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
        },
    },
    ############ Charging Configuration #####################
    "charging/pv_current_limit": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv_charging_current_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Current Limit For Charging",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "A",
            "device_class": "current",
            "entity_category": "config",
            "min": 0,
            "max": 200,
            "step": 0.1,
            "command_topic": "charging/pv_current_limit",
            "mode:": "box"
        },
    },
    "charging/rebulk_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_rebulk_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "ReBulk Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 14.4 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/rebulk_voltage",
            "mode:": "box"
        },
    },
    "charging/voltage_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_charge_limit_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Charge Voltage Limit (Soft)",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 14.6 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/voltage_limit",
            "mode:": "box"
        },
    },
    "charging/overvoltage_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_overvoltage_protection_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Overvoltage Protection Limit (Hard)",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/overvoltage_limit",
            "mode:": "box"
        },
    },
    "charging/equalization_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_equalization_voltage,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Battery Equalization Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
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
                "Solar First",
                "Utility First",
            ],
            "command_topic": "charging/source_priority",
        },
    },
    "charging/bms_communication": {
        "value": modbus.read_bms_communication_enabled,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "BMS Communication",
            "icon": "mdi:import",
            "options": [
                "Disable",
                "RS485",
                "CAN",
            ],
            "command_topic": "charging/bms_communication",
        },
    },
    "charging/charging_limit_mode": {
        "value": modbus.read_bms_charging_limit_current_mode_setting,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Charging Current Limit Mode",
            "icon": "mdi:import",
            "options": [
                "HMI Setting",
                "BMS Protocol",
                "Inverter Logic",
            ],
            "command_topic": "charging/charging_limit_mode",
        },
    },
    "charging/bms_protocol": {
        "value": modbus.read_bms_protocol,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "BMS Protocol",
            "icon": "mdi:import",
            "options": [
                "PACE",
                "RUDA",
                "AOGUAN",
                "OULITE",
                "CEF",
                "XINWANGDA",
                "DAQIN",
                "WOW",
                "PYL",
                "MIT",
                "XIX",
                "POL",
                "GUOX",
                "SMK",
                "VOL",
                "WES",
                "UZE_CAN",
                "PYL_CAN",
                "SGP",
                "GSL",
                "PYL2",
            ],
            "command_topic": "charging/bms_protocol",
        },
    },
    "charging/bulk_charge_time": {
        "enabled": True,
        "value": modbus.read_battery_bulk_charge_time,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Bulk Charge Time",
            "icon": "mdi:clock",
            "mode": "box",
            "min": 10, 
            "max": 900, 
            "step": 1,
            "entity_category": "config",
            "command_topic": "charging/bulk_charge_time",
        },
    },
    "charging/equalization_charge_delay_time": {
        "enabled": True,
        "value": modbus.read_battery_equalization_charge_delay_time,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Equalization Charge Delay Time",
            "icon": "mdi:clock",
        },
    },
    "charging/equalization_charge_interval": {
        "enabled": True,
        "value": modbus.read_battery_equalization_charge_interval,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Equalization Charge Interval",
            "icon": "mdi:clock",
        },
    },
    "charging/bulk_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_bulk_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Bulk Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 14.6 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/bulk_voltage",
        },
    },
    "charging/float_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_float_charge_voltage,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Battery Float Charge Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
        },
    },
    "charging/overdischarge_return_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_overdischarge_return_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Back From Overdischarge Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/overdischarge_return_voltage",
            "mode:": "box"
        },
    },
    "charging/undervoltage_warning_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_undervoltage_warning,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Undervoltage Warning",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/undervoltage_warning_voltage",
            "mode:": "box"
        },
    },
    "charging/overdischarge_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_overdischarge_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Overdischarge Limit (Soft)",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/undervoltage_warning_voltage",
            "mode:": "box"
        },
    },
    "charging/discharge_limit_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_discharge_limit_voltage,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Overdischarge Protection Limit (Hard)",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "entity_category": "config",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "command_topic": "charging/discharge_limit_voltage",
            "mode:": "box"
        },
    },
    "charging/stop_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_stop_state_of_charge,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery SOC Discharge Cutoff",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/stop_discharge_soc_limit",
            "mode:": "box"
        },
    },
    "charging/stop_grid_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_soc_switch_to_line,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Stop Load/Home Discharge Battery SOC",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/stop_grid_discharge_soc_limit",
            "mode:": "box"
        },
    },
    "charging/restart_grid_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_soc_switch_to_battery,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Restart Load/Home Discharge Battery SOC",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/restart_grid_discharge_soc_limit",
            "mode:": "box"
        },
    },
    "charging/stop_charging_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_stop_charging_soc_set,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery SOC Stop Charging",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/stop_charging_soc_limit",
            "mode:": "box"
        },
    },
    "charging/total_charging_current_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_total_charging_current_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Total Charging Current Limit",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "min": 0,
            "max": 200,
            "step": 0.1,
            "command_topic": "charging/total_charging_current_limit",
            "mode:": "box"
        },
    },
    "charging/stop_charging_current_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_stop_charging_current_limit,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Stop Charging Current Limit",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "min": 0,
            "max": 10,
            "step": 0.1,
            "command_topic": "charging/stop_charging_current_limit",
            "mode:": "box"
        },
    },
    "charging/equalization_enable": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_equalization_charging_enable,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Battery Equalization Enable",
        },
    },
    "charging/equalization_timeout": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_equalization_charge_timeout,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Battery Equalization Charge Timeout",
        },
    },
    "charging/last_equalization_time": {
        "enabled": battery_enabled,
        "value": modbus.read_total_last_equalization_charge_time,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Last Equalization Charge Time",
        },
    },
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
#    "inverter/output_priority": {
#        "value": modbus.read_output_priority,
#        "interval": general_interval,
#        "last_update": None,
#        "topic_type": "select",
#        "config": {
#            "name": "Output Priority",
#            "icon": "mdi:export",
#            "options": ["Solar First", "Utility First", "Solar/Battery/Utility"],
#            "command_topic": "inverter/output_priority",
#        },
#    },
   "inverter/hybrid_mode": {
        "value": modbus.read_hybrid_mode,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Hybrid Grid Mode",
            "icon": "mdi:export",
            "options": ["On Grid", "Limit Power to UPS", "Limit Power to Home"],
            "command_topic": "inverter/hybrid_mode",
        },
    },
    "inverter/battery_priority": {
        "value": modbus.read_battery_discharge_enabled,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Battery State Priority",
            "icon": "mdi:export",
            "options": [
                "Standby",
                "Battery Discharge For Load",
                "Battery Discharge For Home",
                "Battery Discharge For Grid",
            ],
            "command_topic": "inverter/battery_priority",
        },
    },
   "inverter/enable_danger": {
        "value": lambda: 
            (mqtt_config["inverter/enable_danger"]["last_value"]),
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "last_value": "Disabled",
        "config": {
            "name": "Enable Dangerous Operations",
            "icon": "mdi:export",
            "options": ["Disabled", "Enabled"],
            "command_topic": "inverter/enable_danger",
        },
    },
   "pv/power_priority": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_pv_power_priority_set,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "PV Power Priority Mode",
            "icon": "mdi:export",
            "options": ["Load Priority", "Charging Priority", "Grid Priority"],
            "command_topic": "pv/power_priority",
        },
    },
   "inverter/reset": {
        "value": 1,
        "topic_type": "button",
        "dangerous": True,
        "config": {
            "name": "Reset Inverter",
            "icon": "mdi:power-cycle",
            "command_topic": "inverter/reset",
        },
    },
   "inverter/clear_statistics": {
        "value": 2,
        "topic_type": "button",
        "dangerous": True,
        "config": {
            "name": "Clear Statistics",
            "icon": "mdi:power-cycle",
            "command_topic": "inverter/clear_statistics",
        },
    },
   "inverter/clear_errors": {
        "value": 3,
        "topic_type": "button",
        "dangerous": True,
        "config": {
            "name": "Clear Errors",
            "icon": "mdi:power-cycle",
            "command_topic": "inverter/clear_errors",
        },
    },
   "charging/time_charge_enabled": {
        "value": modbus.read_time_charge_enabled,
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Timed Charge Enabled",
            "icon": "mdi:export",
            "options": ["Disabled", "Enabled"],
            "command_topic": "charging/time_charge_enabled",
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
            "name": "Temperature Transformer",
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
            "name": "Temperature Ambient",
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
            "name": "Daily Generated Energy To Grid",
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
    "statistics/total_grid_generated_energy": {
        "value": modbus.read_total_grid_energy_total,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Generated Energy to Grid",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
    "statistics/total_pv_generated_energy": {
        "value": modbus.read_total_pv_generated_energy_total,
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Solar Generated Energy",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
        },
    },
}
