import os
from dotenv import load_dotenv
import modbus

load_dotenv()

device = {
    "name": os.getenv("MQTT_TOPIC"),
    "identifiers": [modbus.read_register_str(0x035, "Serial Number", clean=True)],
    "manufacturer": os.getenv("DEVICE_MANUFACTURER"),
    "serial_number": modbus.read_register_str(0x035, "Serial Number", clean=True),
    "model": modbus.read_register_value(0x01B, "Model", integer=True),
}

system_enabled: bool = True if os.getenv("PUBLISH_SYSTEM") == "true" else False
battery_enabled: bool = True if os.getenv("BATTERY_CONNECTED") == "true" else False

LEAD_ACID_BATTERY_TYPES: frozenset = frozenset({"User defined", "SLD", "FLD", "GEL"})

EQUALIZATION_TOPICS: list = [
    "charging/equalization_voltage",
    "charging/equalization_charge_delay_time",
    "charging/equalization_charge_interval",
    "charging/equalization_timeout",
    "charging/equalization_enable",
    "charging/equalization_immediately",
    "charging/last_equalization_time",
]

EQUALIZATION_AVAIL_TOPIC: str = f"{os.getenv('MQTT_TOPIC')}/equalization/availability"
try:
    simulate_parallel = int(os.getenv("PARALLEL")) if os.getenv("PARALLEL") else 0
except ValueError:
    simulate_parallel = 0
parallel: bool = True if os.getenv("PARALLEL") == "true" or simulate_parallel > 1 else False
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
    int(os.getenv("STATISTICS_INTERVAL")) if os.getenv("STATISTICS_INTERVAL") else 300000
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
    "charging/pv_current_limit": lambda v: modbus.write_register_value(0xE001, scale=0.1, value=v),  # 0xE001 PvChgCurrSet
    "charging/voltage_limit": lambda v: modbus.write_battery_voltage_register(0xE006, v),  # 0xE006 BatChgLimitVolt
    "charging/overvoltage_limit": lambda v: modbus.write_battery_voltage_register(0xE005, v),  # 0xE005 BatOverVolt
    "charging/bulk_charge_time": lambda v: modbus.write_register_value(0xE012, value=v),  # 0xE012 BatImprovChgTime
    "charging/bulk_voltage": lambda v: modbus.write_battery_voltage_register(0xE008, v),  # 0xE008 BatImprovChgVolt
    "charging/rebulk_voltage": lambda v: modbus.write_battery_voltage_register(0xE00A, v),  # 0xE00A BatImprovChgBackVolt
    "charging/overdischarge_return_voltage": lambda v: modbus.write_battery_voltage_register(0xE00B, v),  # 0xE00B BatOverDischgBackVolt
    "charging/undervoltage_warning_voltage": lambda v: modbus.write_battery_voltage_register(0xE00C, v),  # 0xE00C BatUnderVolt
    "charging/discharge_limit_voltage": lambda v: modbus.write_battery_voltage_register(0xE00E, v),  # 0xE00E BatDischgLimitVolt
    "charging/overdicharge_limit": lambda v: modbus.write_battery_voltage_register(0xE00D, v),  # 0xE00D BatOverDischgVolt
    "charging/stop_discharge_soc_limit": lambda v: modbus.write_register_value(0xE00F, value=v),  # 0xE00F BatStopSOC
    "charging/stop_grid_discharge_soc_limit": lambda v: modbus.write_register_value(0xE01F, value=v),  # 0xE01F BatSocSwToLine
    "charging/restart_grid_discharge_soc_limit": lambda v: modbus.write_register_value(0xE020, value=v),  # 0xE020 BatSocSwToBatt
    "charging/stop_charging_soc_limit": lambda v: modbus.write_register_value(0xE01D, value=v),  # 0xE01D StopChgSocSet
    "charging/total_charging_current_limit": lambda v: modbus.write_register_value(0xE20A, scale=0.1, value=v),  # 0xE20A MaxChgCurr
    "charging/stop_charging_current_limit": lambda v: modbus.write_register_value(0xE01C, scale=0.1, value=v),  # 0xE01C StopChgCurrSet
    "charging/source_priority": lambda v: modbus.write_lookup_register(0xE20F, modbus.CHARGING_SOURCE_PRIORITIES, v),  # 0xE20F ChgSourcePriority
    "charging/bms_communication": lambda v: modbus.write_lookup_register(0xE215, modbus.BMS_COMM_MODES, v),  # 0xE215 BmsCommEnable
    "charging/charging_limit_mode": lambda v: modbus.write_lookup_register(0xE025, modbus.BMS_CHARGE_LIMIT_MODES, v),  # 0xE025 BMSChgLCMode
    "charging/bms_protocol": lambda v: modbus.write_lookup_register(0xE21B, modbus.BMS_PROTOCOLS, v),  # 0xE21B Rs485BmsProtocol
    "charging/time_charge_enabled": lambda v: modbus.write_enabled_register(0xE02C, v),  # 0xE02C OnTimeChargeEn
    "charging/time_charge_1_soc_limit": lambda v: modbus.write_register_value(0xE03B, value=v),  # 0xE03B TimedChg1StopSOC
    "charging/time_charge_2_soc_limit": lambda v: modbus.write_register_value(0xE03C, value=v),  # 0xE03C TimedChg2StopSOC
    "charging/time_charge_3_soc_limit": lambda v: modbus.write_register_value(0xE03D, value=v),  # 0xE03D TimedChg3StopSOC
    "charging/time_charge_1_max_power": lambda v: modbus.write_register_value(0xE04A, value=v),  # 0xE04A TimedChg1MaxPower
    "charging/time_charge_2_max_power": lambda v: modbus.write_register_value(0xE04B, value=v),  # 0xE04B TimedChg2MaxPower
    "charging/time_charge_3_max_power": lambda v: modbus.write_register_value(0xE04C, value=v),  # 0xE04C TimedChg3MaxPower
    # 0xE04D TimedChgSource bit fields
    "charging/time_charge_1_grid_source": lambda v: modbus.write_bit_register(0xE04D, 0, v),
    "charging/time_charge_1_gen_source": lambda v: modbus.write_bit_register(0xE04D, 1, v),
    "charging/time_charge_2_grid_source": lambda v: modbus.write_bit_register(0xE04D, 2, v),
    "charging/time_charge_2_gen_source": lambda v: modbus.write_bit_register(0xE04D, 3, v),
    "charging/time_charge_3_grid_source": lambda v: modbus.write_bit_register(0xE04D, 4, v),
    "charging/time_charge_3_gen_source": lambda v: modbus.write_bit_register(0xE04D, 5, v),
    "charging/time_discharge_enabled": lambda v: modbus.write_enabled_register(0xE033, v),  # 0xE033 OnTimeDischgEn
    "charging/time_discharge_1_soc_limit": lambda v: modbus.write_register_value(0xE03E, value=v),  # 0xE03E TimedDchg1StopSOC
    "charging/time_discharge_2_soc_limit": lambda v: modbus.write_register_value(0xE03F, value=v),  # 0xE03F TimedDchg2StopSOC
    "charging/time_discharge_3_soc_limit": lambda v: modbus.write_register_value(0xE040, value=v),  # 0xE040 TimedDchg3StopSOC
    "charging/time_discharge_1_max_power": lambda v: modbus.write_register_value(0xE047, value=v),  # 0xE047 TimedDchg1MaxPower
    "charging/time_discharge_2_max_power": lambda v: modbus.write_register_value(0xE048, value=v),  # 0xE048 TimedDchg2MaxPower
    "charging/time_discharge_3_max_power": lambda v: modbus.write_register_value(0xE049, value=v),  # 0xE049 TimedDchg3MaxPower
    "inverter/power_saving": lambda v: modbus.write_enabled_register(0xE20C, v),  # 0xE20C PowerSavingMode
    #    "inverter/output_priority": lambda v: modbus.write_lookup_register(0xE204, modbus.OUTPUT_PRIORITIES, v),
    "inverter/hybrid_mode": lambda v: modbus.write_lookup_register(0xE037, modbus.HYBRID_MODES, v),  # 0xE037 InvToGridEn
    "inverter/generator_mode": lambda v: modbus.write_lookup_register(0xE21F, modbus.GEN_MODES, v),  # 0xE21F GenWorkMode
    "inverter/battery_priority": lambda v: modbus.write_lookup_register(0xE42A, modbus.BATTERY_DISCHARGE_MODES, v),  # 0xE42A BattForGridPowerEn
    "pv/power_priority": lambda v: modbus.write_lookup_register(0xE039, modbus.PV_PRIORITY_MODES, v),  # 0xE039 PvPowerPrioritySet
    "inverter/enable_danger": lambda x: "update_value",
    "charging/equalization_immediately": lambda v: modbus.write_register_value(0xDF0D, value=v),  # 0xDF0D BattEqualChgImmediate
    "inverter/reset": lambda v: modbus.write_register_value(0xDF01, value=v),  # 0xDF01 CmdMachineReset
    "inverter/clear_statistics": modbus.write_restore_factory_setting,  # 0xDF02 CmdRestoreFactorySetting
    "inverter/clear_errors": modbus.write_restore_factory_setting,  # 0xDF02 CmdRestoreFactorySetting
    # Time-schedule start/end times
    "charging/time_charge_1_start": lambda v: modbus.write_time_register(0xE026, v),  # 0xE026 ChargeStartTime1
    "charging/time_charge_2_start": lambda v: modbus.write_time_register(0xE028, v),  # 0xE028 ChargeStartTime2
    "charging/time_charge_3_start": lambda v: modbus.write_time_register(0xE02A, v),  # 0xE02A ChargeStartTime3
    "charging/time_charge_1_end": lambda v: modbus.write_time_register(0xE027, v),  # 0xE027 ChargeEndTime1
    "charging/time_charge_2_end": lambda v: modbus.write_time_register(0xE029, v),  # 0xE029 ChargeEndTime2
    "charging/time_charge_3_end": lambda v: modbus.write_time_register(0xE02B, v),  # 0xE02B ChargeEndTime3
    "charging/time_discharge_1_start": lambda v: modbus.write_time_register(0xE02D, v),  # 0xE02D DischgStartTime1
    "charging/time_discharge_2_start": lambda v: modbus.write_time_register(0xE02F, v),  # 0xE02F DischgStartTime2
    "charging/time_discharge_3_start": lambda v: modbus.write_time_register(0xE031, v),  # 0xE031 DischgStartTime3
    "charging/time_discharge_1_end": lambda v: modbus.write_time_register(0xE02E, v),  # 0xE02E DischgEndTime1
    "charging/time_discharge_2_end": lambda v: modbus.write_time_register(0xE030, v),  # 0xE030 DischgEndTime2
    "charging/time_discharge_3_end": lambda v: modbus.write_time_register(0xE032, v),  # 0xE032 DischgEndTime3
    # Battery parameter controls
    "charging/float_voltage": lambda v: modbus.write_battery_voltage_register(0xE009, v),  # 0xE009 BatFloatChgVolt
    "charging/equalization_voltage": lambda v: modbus.write_battery_voltage_register(0xE007, v),  # 0xE007 BatConstChgVolt
    "charging/equalization_charge_delay_time": lambda v: modbus.write_register_value(0xE011, value=v),  # 0xE011 BatConstChgTime
    "charging/equalization_charge_interval": lambda v: modbus.write_register_value(0xE013, value=v),  # 0xE013 BatConstChgGapTime
    "charging/equalization_timeout": lambda v: modbus.write_register_value(0xE023, value=v),  # 0xE023 BattEqualChgTimeout
    "charging/equalization_enable": lambda v: modbus.write_enabled_register(0xE206, v),  # 0xE206 BattEqualChgEnable
    "charging/grid_current_limit": lambda v: modbus.write_register_value(0xE005, scale=0.1, value=v),  # 0xE005 BatOverVolt
    "charging/lithium_active_current": lambda v: modbus.write_register_value(0xE024, scale=0.1, value=v),  # 0xE024 LiBattActiveCurrSet
    "battery/type": lambda v: modbus.write_lookup_register(0xE004, modbus.BATTERY_TYPES, v),  # 0xE004 BatTypeSet
    "battery/soc_low_alarm": lambda v: modbus.write_register_value(0xE01E, value=v),  # 0xE01E BatSocLowAlarm
    "battery/dc_switch_low_voltage": lambda v: modbus.write_battery_voltage_register(0xE01B, v),  # 0xE01B BatSwitchDcVolt
    "battery/voltage_switch_to_inverter": lambda v: modbus.write_battery_voltage_register(0xE022, v),  # 0xE022 BattVoltSwToInv
    "battery/overdischarge_delay_time": lambda v: modbus.write_register_value(0xE010, value=v),  # 0xE010 BatOverDischgDelayTime
    # Inverter controls
    "inverter/ac_voltage_range": lambda v: modbus.write_lookup_register(0xE20B, modbus.AC_VOLTAGE_RANGES, v),  # 0xE20B AcVoltRange
    "inverter/parallel_mode": lambda v: modbus.write_lookup_register(0xE201, modbus.PARALLEL_MODES, v),  # 0xE201 ParallMode
    "inverter/alarm_enabled": lambda v: modbus.write_enabled_register(0xE210, v),  # 0xE210 AlarmEnable
    "inverter/alarm_on_input_loss": lambda v: modbus.write_enabled_register(0xE211, v),  # 0xE211 AlarmEnWhenSourceLoss
    "inverter/auto_restart_on_overload": lambda v: modbus.write_enabled_register(0xE20D, v),  # 0xE20D AutoRestartOvLoad
    "inverter/auto_restart_on_overheat": lambda v: modbus.write_enabled_register(0xE20E, v),  # 0xE20E AutoRestartOvTemper
    "inverter/auto_bypass_on_overload": lambda v: modbus.write_enabled_register(0xE212, v),  # 0xE212 BypEnableWhenOvLoad
    "inverter/stop_on_bms_error": lambda v: modbus.write_enabled_register(0xE214, v),  # 0xE214 BmsErrStopEnable
    "inverter/dc_load_switch": lambda v: modbus.write_enabled_register(0xE216, v),  # 0xE216 DcLoadSwitch
    "inverter/power_off_on": lambda v: modbus.write_register_value(0xDF00, value=v),  # 0xDF00 CmdPowerOnOff
}


mqtt_config: dict[str, dict[str, any]] = {
    # 0x000A  MinorVersion
    "system/read_minor_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x00A, "integer": True},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Minor Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x0014  SoftWareVersion
    "system/app_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x014, "scale": 1e-2, "prefix": "v"},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "App Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x0015
    "system/bootloader_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x015, "scale": 1e-2, "prefix": "v"},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Bootloader Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x0016  HardWareVersion
    "system/control_panel_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x016, "scale": 1e-2, "prefix": "v"},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Control Panel Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x0017
    "system/power_amplifier_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x017, "scale": 1e-2, "prefix": "v"},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Power Amplifier Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x001A  Rs485Addr
    "system/rs485_address": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x01A, "integer": True},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 Address",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x001B  MachModelNum2
    "system/model": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x01B, "integer": True},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Model",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x001C  RS485Version
    "system/rs485_version": {
        "enabled": system_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x01C, "scale": 1e-2, "prefix": "v"},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "RS-485 Version",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x0021  CpuBuidTime
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
    # 0x0035  ProductSNStr
    "system/serial_number": {
        "enabled": system_enabled,
        "value": modbus.read_register_str,
        "args": {"register": 0x035, "clean": True},
        "last_update": None,
        "interval": system_interval,
        "config": {
            "name": "Serial Number",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    ############ Battery #####################
    # 0x0100  BatSoc
    "battery/soc": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0100, "integer": True},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Battery SOC",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "device_class": "battery",
            "state_class": "measurement",
        },
    },
    # 0x0101  BatVolt
    "battery/voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0101, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Battery Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0102  ChargeCurr
    "battery/current": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0102, "scale": 0.1, "signed": True},
        "interval": battery_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Battery Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0103  DeviceBatTemper
    "battery/temperature": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0103, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Battery Temperature",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    ############ PV1 #####################
    # 0x0107  Pv1Volt
    "pv1/voltage": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0107, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0108  Pv1Curr
    "pv1/current": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0108, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0109  Pv1ChargePower
    "pv1/power": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0109, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV1 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ PV #####################
    # 0x010A  PvTotalPower
    "pv/total_power": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x010A, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV Total Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x010B  ChargeState
    "battery/charge_state": {
        "enabled": battery_enabled,
        "value": modbus.read_lookup_register,
        "args": {"register": 0x010B, "lookup": modbus.CHARGING_STATES},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "Charge State",
            "icon": "mdi:information",
        },
    },
    # 0x010E  ChargePower
    "inverter/charging_power": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0x010E, "integer": True},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Charging Power",
            "icon": "mdi:battery-charging",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ PV2 #####################
    # 0x010F  Pv2Volt
    "pv2/voltage": {
        "enabled": pv_mppt_trackers >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x010F, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0110  Pv2Curr
    "pv2/current": {
        "enabled": pv_mppt_trackers >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x0110, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0111  Pv2ChargePower
    "pv2/power": {
        "enabled": pv_mppt_trackers >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x0111, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV2 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ BMS Cell Data #####################
    # 0x0112  BatBmsVolt
    "battery/bms_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0112, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Battery Voltage",
            "icon": "mdi:battery",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0113  BatBmsCurr
    "battery/bms_current": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0113, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Battery Current",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0114  BatBmsTemp
    "battery/bms_temperature": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0114, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "BMS Battery Temperature",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0115  BatBmsChgLimitVolt
    "battery/bms_charge_limit_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0115, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Charge Limit Voltage",
            "icon": "mdi:battery-arrow-up",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0116  BatBmsChgLimitCurr
    "battery/bms_charge_limit_current": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0116, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Charge Limit Current",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0117  BatBmsDchgLimitCurr
    "battery/bms_discharge_limit_current": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0117, "scale": 0.1},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Discharge Limit Current",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    ############ PV3 #####################
    # 0x011E  Pv3Volt
    "pv3/voltage": {
        "enabled": pv_mppt_trackers >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x011E, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV3 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x011F  Pv3Curr
    "pv3/current": {
        "enabled": pv_mppt_trackers >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x011F, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV3 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0120  Pv3Power
    "pv3/power": {
        "enabled": pv_mppt_trackers >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x0120, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV3 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ PV4 #####################
    # 0x0121  Pv4Volt
    "pv4/voltage": {
        "enabled": pv_mppt_trackers >= 4,
        "value": modbus.read_register_value,
        "args": {"register": 0x0121, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV4 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0122  Pv4Curr
    "pv4/current": {
        "enabled": pv_mppt_trackers >= 4,
        "value": modbus.read_register_value,
        "args": {"register": 0x0122, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV4 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0123  Pv4Power
    "pv4/power": {
        "enabled": pv_mppt_trackers >= 4,
        "value": modbus.read_register_value,
        "args": {"register": 0x0123, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV4 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ PV5 #####################
    # 0x0124  Pv5Volt
    "pv5/voltage": {
        "enabled": pv_mppt_trackers >= 5,
        "value": modbus.read_register_value,
        "args": {"register": 0x0124, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV5 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0125  Pv5Curr
    "pv5/current": {
        "enabled": pv_mppt_trackers >= 5,
        "value": modbus.read_register_value,
        "args": {"register": 0x0125, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV5 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0126  Pv5Power
    "pv5/power": {
        "enabled": pv_mppt_trackers >= 5,
        "value": modbus.read_register_value,
        "args": {"register": 0x0126, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV5 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ PV6 #####################
    # 0x0127  Pv6Volt
    "pv6/voltage": {
        "enabled": pv_mppt_trackers >= 6,
        "value": modbus.read_register_value,
        "args": {"register": 0x0127, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV6 Voltage",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0128  Pv6Curr
    "pv6/current": {
        "enabled": pv_mppt_trackers >= 6,
        "value": modbus.read_register_value,
        "args": {"register": 0x0128, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV6 Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0129  Pv6Power
    "pv6/power": {
        "enabled": pv_mppt_trackers >= 6,
        "value": modbus.read_register_value,
        "args": {"register": 0x0129, "integer": True},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV6 Power",
            "icon": "mdi:solar-power",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x0132  BmsMaxCellVolt
    "battery/bms_max_cell_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0132, "integer": True},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Max Cell Voltage",
            "icon": "mdi:battery-high",
            "unit_of_measurement": "mV",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0133  BmsMinCellVolt
    "battery/bms_min_cell_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0133, "integer": True},
        "interval": battery_interval,
        "last_update": None,
        "config": {
            "name": "BMS Min Cell Voltage",
            "icon": "mdi:battery-low",
            "unit_of_measurement": "mV",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0134  BmsMaxCellTemp
    "battery/bms_max_cell_temp": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0134, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "BMS Max Cell Temperature",
            "icon": "mdi:thermometer-high",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0135  BmsMinCellTemp
    "battery/bms_min_cell_temp": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0x0135, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "BMS Min Cell Temperature",
            "icon": "mdi:thermometer-low",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0200  CurrErrReg
    "inverter/error": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {
            "register": 0x200,
            "integer": True,
            "format_str": "{:x}",
            "prefix": "0x",
        },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Error Flags",
            "icon": "mdi:alert-circle",
            "entity_category": "diagnostic",
        },
    },
    # 0x0204  CurrFcode
    "inverter/failcode0": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args": {
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
    # 0x0205
    "inverter/failcode1": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args": {
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
    # 0x0206
    "inverter/failcode2": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args": {
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
    # 0x0207
    "inverter/failcode3": {
        "enabled": True,
        "value": modbus.read_failcode,
        "args": {
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
    # 0x020C  SysDateTime
    "inverter/system_datetime": {
        "value": modbus.read_datetime_register,
        "args": {"register": 0x020C},
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "System Date/Time",
            "icon": "mdi:clock",
        },
    },
    # 0x020F  GridOnRemainTime
    "inverter/grid_on_remain_time": {
        "enabled": True,
        # "value": modbus.read_register_value,
        "args": {"register": 0x020F, "integer": True},
        "value": modbus.read_register_value,
        "args": {
            "register": 0x20F,
        },
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Remaining Grid On Time",
            "icon": "mdi:information",
        },
    },
    # 0x0210  MachineState
    "inverter/state": {
        "enabled": True,
        "value": modbus.read_lookup_register,
        "args": {"register": 0x0210, "lookup": modbus.MACHINE_STATES},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter State",
            "icon": "mdi:information",
        },
    },
    # 0x0210  MachineState
    "inverter/power_off_on": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0x0210, "lookup": modbus.MACHINE_STATES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Inverter Power",
            "icon": "mdi:power",
            "state_off": 0,
            "state_on": 1,
            "payload_off": 0,
            "payload_on": 1,
            "command_topic": "inverter/power_off_on",
        },
    },
    # 0x0212  BusVoltSum
    "inverter/bus_voltage": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0x0212, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Bus Voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    ############ Grid #####################
    # 0x0213  GridVoltA
    "grid/voltage_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0213, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Voltage A",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0214  GridCurrA
    "grid/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0214, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0215  GridFreq
    "grid/frequency": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0215, "scale": 0.01},
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Frequency",
            "icon": "mdi:pulse",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
            "state_class": "measurement",
        },
    },
    # 0x0216  InvVoltA
    "inverter/voltage_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0216, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Voltage A",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0217  InvCurrA
    "inverter/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0217, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0218  InvFreq
    "inverter/frequency": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0218, "scale": 0.01},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Frequency",
            "icon": "mdi:sine-wave",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
            "state_class": "measurement",
        },
    },
    # 0x021E  LineChgCurr
    "load/grid_charging_current": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x021E, "scale": 0.1},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Grid Charging Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x021F  LoadRatioA
    "load/ratio_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x021F, "integer": True},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
            "state_class": "measurement",
        },
    },
    ############ Temperatures #####################
    # 0x0220  Tempera
    "temperature/dc_dc": {
        "value": modbus.read_register_value,
        "args": {"register": 0x0220, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature DC-DC",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0221  Temperb
    "temperature/dc_ac": {
        "value": modbus.read_register_value,
        "args": {"register": 0x0221, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature DC-AC",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0222  Temperc
    "temperature/transformer": {
        "value": modbus.read_register_value,
        "args": {"register": 0x0222, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature Transformer",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0223  Temperd
    "temperature/ambient": {
        "enabled": has_ambient_temperature,
        "value": modbus.read_register_value,
        "args": {"register": 0x0223, "scale": 0.1, "signed": True},
        "interval": temperature_interval,
        "last_update": None,
        "config": {
            "name": "Temperature Ambient",
            "icon": "mdi:thermometer",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
        },
    },
    # 0x0224  Ibuck1
    "pv/charging_current": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x0224, "scale": 0.1},
        "interval": pv_interval,
        "last_update": None,
        "config": {
            "name": "PV Charging Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0225  ParallCurrRms
    "inverter/parallel_current": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0x0225, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Parallel Load Avg Current",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0228  PBusVolt
    "inverter/pbus_voltage": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0x0228, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "PBus Voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x0229  NBusVolt
    "inverter/nbus_voltage": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0x0229, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "NBus Voltage",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x022A  GridVoltB
    "grid/voltage_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x022A, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Voltage B",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x022B  GridVoltC
    "grid/voltage_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x022B, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Voltage C",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x022C  InvVoltB
    "inverter/voltage_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x022C, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Voltage B",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x022D  InvVoltC
    "inverter/voltage_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x022D, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Voltage C",
            "icon": "mdi:lightning-bolt",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0x022E  InvCurrB
    "inverter/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x022E, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x022F  InvCurrC
    "inverter/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x022F, "scale": 0.1},
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Inverter Current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0236  LoadRatioB
    "load/ratio_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x0236, "integer": True},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
            "state_class": "measurement",
        },
    },
    # 0x0237  LoadRatioC
    "load/ratio_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x0237, "integer": True},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Ratio C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
            "state_class": "measurement",
        },
    },
    # 0x0238  GridCurrB
    "grid/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x0238, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # 0x0239  GridCurrC
    "grid/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x0239, "scale": 0.1},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    # If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    # 0x023A  GridActivePowerA
    "ct/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x023A, "signed": True, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "CT Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    # 0x023B  GridActivePowerB
    "ct/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x023B, "signed": True, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "CT Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    # 0x023C  GridActivePowerC
    "ct/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x023C, "signed": True, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "CT Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x023D  GridApparentPowerA
    "grid/apparent_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x023D, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    # 0x023E  GridApparentPowerB
    "grid/apparent_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x023E, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    # 0x023F  GridApparentPowerC
    "grid/apparent_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x023F, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Grid Apparent Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    # 0x0240  HomeLoadActivePowerA
    "home/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0x240, "unit": "W"},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x0241  HomeLoadActivePowerB
    "home/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_register_value,
        "args": {"register": 0x241, "unit": "W"},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x0242  HomeLoadActivePowerC
    "home/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_register_value,
        "args": {"register": 0x242, "unit": "W"},
        "interval": grid_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Home Load Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x024C  LoadRatioSum
    "load/parallel_ratio": {
        "enabled": parallel and simulate_parallel==0,
        "value": modbus.read_register_value,
        "args": {"register": 0x024C, "integer": True},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Parallel Load Ratio",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "%",
            "device_class": "percentage",
            "state_class": "measurement",
        },
    },
    ############ Inverter #####################
    # 0x024D  ParallelNum
    "inverter/num_parallel": {
        "enabled": parallel,
        "value": modbus.read_register_value,
        "args": {"register": 0x24D, "integer": True},
        "last_update": None,
        "interval": inverter_interval,
        "config": {
            "name": "Number of Parallel Inverters",
            "entity_category": "diagnostic",
            "icon": "mdi:information",
        },
    },
    # 0x024E  ParaUpsLoadPowersum
    "load/parallel_power": {
        "enabled": parallel,
        "value": lambda: round(modbus.read_parallel_load_active_power_sum() if simulate_parallel==0 else float(mqtt_config["load/power"]["last_value"])*simulate_parallel,
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Load Parallel Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x0250  ParaHomeLoadPowerSum
    "home/parallel_power": {
        "enabled": parallel,
        "value": lambda: round(modbus.read_parallel_home_active_power_sum() if simulate_parallel==0 else float(mqtt_config["home/power"]["last_value"])*simulate_parallel,
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Home Parallel Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # If you have CTs, this will report CT power, but othwerwise reports grid power, can get grid power in seperate endpoint by subtracting home load power which will be 0 with no CTs
    # 0x0252  ParaGridPowerSum
    "ct/parallel_power": {
        "enabled": parallel,
        "value": lambda: round(modbus.read_parallel_grid_active_power_sum() if simulate_parallel==0 else float(mqtt_config["ct/power"]["last_value"])*simulate_parallel,
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "CT Parallel Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    # 0x0254  ParaGenPortPowerSum
    "gen/parallel_power": {
        "enabled": parallel and simulate_parallel==0,
        "value": modbus.read_register_value,
        "args": {"register": 0x0254, "integer": True},
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Gen Parallel Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    ############ Charging Configuration #####################
    # 0xE001  PvChgCurrSet
    "charging/pv_current_limit": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_register_value,
        "args": {"register": 0xE001, "scale": 0.1},
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
            "mode:": "box",
        },
    },
    # 0xE003  BatRateVolt
    "battery/rated_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_rate_voltage,
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Battery Rated Voltage",
            "icon": "mdi:battery",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0xE004  BatTypeSet
    "battery/type": {
        "enabled": battery_enabled,
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE004, "lookup": modbus.BATTERY_TYPES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Battery Type",
            "icon": "mdi:battery-unknown",
            "options": list(modbus.BATTERY_TYPES.values()),
            "entity_category": "config",
            "command_topic": "battery/type",
        },
    },
    # 0xE005  BatOverVolt
    "charging/overvoltage_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE005},
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
            "mode:": "box",
        },
    },
    # 0xE005  BatOverVolt
    "charging/grid_current_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE005, "scale": 0.1},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Grid Charging Current Limit",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "min": 0,
            "max": 200,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "charging/grid_current_limit",
            "mode": "box",
        },
    },
    # 0xE006  BatChgLimitVolt
    "charging/voltage_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE006},
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
            "mode:": "box",
        },
    },
    # 0xE007  BatConstChgVolt
    "charging/equalization_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE007},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Equalization Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "charging/equalization_voltage",
            "mode": "box",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # 0xE008  BatImprovChgVolt
    "charging/bulk_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE008},
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
    # 0xE009  BatFloatChgVolt
    "charging/float_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE009},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Float Charge Voltage",
            "icon": "mdi:ray-vertex",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "charging/float_voltage",
            "mode": "box",
        },
    },
    # 0xE00A  BatImprovChgBackVolt
    "charging/rebulk_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE00A},
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
            "mode:": "box",
        },
    },
    # 0xE00B  BatOverDischgBackVolt
    "charging/overdischarge_return_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE00B},
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
            "mode:": "box",
        },
    },
    # 0xE00C  BatUnderVolt
    "charging/undervoltage_warning_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE00C},
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
            "mode:": "box",
        },
    },
    # 0xE00D  BatOverDischgVolt
    "charging/overdischarge_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE00D},
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
            "mode:": "box",
        },
    },
    # 0xE00E  BatDischgLimitVolt
    "charging/discharge_limit_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE00E},
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
            "mode:": "box",
        },
    },
    # 0xE00F  BatStopSOC
    "charging/stop_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE00F, "integer": True},
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
            "mode:": "box",
        },
    },
    # 0xE010  BatOverDischgDelayTime
    "battery/overdischarge_delay_time": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE010, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Over-discharge Delay Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "s",
            "min": 0,
            "max": 120,
            "step": 1,
            "entity_category": "config",
            "command_topic": "battery/overdischarge_delay_time",
            "mode": "box",
        },
    },
    # 0xE011  BatConstChgTime
    "charging/equalization_charge_delay_time": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0xE011, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Equalization Charge Delay Time",
            "icon": "mdi:clock",
            "unit_of_measurement": "min",
            "min": 0,
            "max": 900,
            "step": 1,
            "entity_category": "config",
            "command_topic": "charging/equalization_charge_delay_time",
            "mode": "box",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # 0xE012  BatImprovChgTime
    "charging/bulk_charge_time": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0xE012, "integer": True},
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
    # 0xE013  BatConstChgGapTime
    "charging/equalization_charge_interval": {
        "enabled": True,
        "value": modbus.read_register_value,
        "args": {"register": 0xE013, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Equalization Charge Interval",
            "icon": "mdi:clock",
            "unit_of_measurement": "d",
            "min": 0,
            "max": 255,
            "step": 1,
            "entity_category": "config",
            "command_topic": "charging/equalization_charge_interval",
            "mode": "box",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # 0xE01B  BatSwitchDcVolt
    "battery/dc_switch_low_voltage": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE01B},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery DC Switch Low Voltage",
            "icon": "mdi:battery-arrow-down",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "battery/dc_switch_low_voltage",
            "mode": "box",
        },
    },
    # 0xE01C  StopChgCurrSet
    "charging/stop_charging_current_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE01C, "scale": 0.1},
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
            "mode:": "box",
        },
    },
    # 0xE01D  StopChgSocSet
    "charging/stop_charging_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE01D, "integer": True},
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
            "mode:": "box",
        },
    },
    # 0xE01E  BatSocLowAlarm
    "battery/soc_low_alarm": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE01E, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery SOC Low Alarm",
            "icon": "mdi:battery-alert",
            "unit_of_measurement": "%",
            "device_class": "battery",
            "state_class": "measurement",
            "min": 0,
            "max": 100,
            "step": 1,
            "entity_category": "config",
            "command_topic": "battery/soc_low_alarm",
            "mode": "box",
        },
    },
    # 0xE01F  BatSocSwToLine
    "charging/stop_grid_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE01F, "integer": True},
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
            "mode:": "box",
        },
    },
    # 0xE020  BatSocSwToBatt
    "charging/restart_grid_discharge_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE020, "integer": True},
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
            "mode:": "box",
        },
    },
    # 0xE022  BattVoltSwToInv
    "battery/voltage_switch_to_inverter": {
        "enabled": battery_enabled,
        "value": modbus.read_battery_voltage_register,
        "args": {"register": 0xE022},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Voltage Switch To Inverter",
            "icon": "mdi:battery-charging",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "min": 9 * modbus.battery_rate,
            "max": 15.5 * modbus.battery_rate,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "battery/voltage_switch_to_inverter",
            "mode": "box",
        },
    },
    # 0xE023  BattEqualChgTimeout
    "charging/equalization_timeout": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE023, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Battery Equalization Charge Timeout",
            "icon": "mdi:clock-alert",
            "unit_of_measurement": "min",
            "min": 5,
            "max": 900,
            "step": 5,
            "entity_category": "config",
            "command_topic": "charging/equalization_timeout",
            "mode": "box",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # 0xE024  LiBattActiveCurrSet
    "charging/lithium_active_current": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE024, "scale": 0.1},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Lithium Battery Active Current",
            "icon": "mdi:current-dc",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "min": 0,
            "max": 20,
            "step": 0.1,
            "entity_category": "config",
            "command_topic": "charging/lithium_active_current",
            "mode": "box",
        },
    },
    # 0xE025  BMSChgLCMode
    "charging/charging_limit_mode": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE025, "lookup": modbus.BMS_CHARGE_LIMIT_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Charging Current Limit Mode",
            "icon": "mdi:import",
            "options": list(modbus.BMS_CHARGE_LIMIT_MODES.values()),
            "command_topic": "charging/charging_limit_mode",
        },
    },
    # 0xE026  ChargeStartTime1
    "charging/time_charge_1_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE026},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge Start Time 1",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_1_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE027  ChargeEndTime1
    "charging/time_charge_1_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE027},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge End Time 1",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_1_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE028  ChargeStartTime2
    "charging/time_charge_2_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE028},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge Start Time 2",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_2_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE029  ChargeEndTime2
    "charging/time_charge_2_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE029},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge End Time 2",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_2_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE02A  ChargeStartTime3
    "charging/time_charge_3_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE02A},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge Start Time 3",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_3_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE02B  ChargeEndTime3
    "charging/time_charge_3_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE02B},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Charge End Time 3",
            "icon": "mdi:clock",
            "command_topic": "charging/time_charge_3_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE02C  OnTimeChargeEn
    "charging/time_charge_enabled": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE02C},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Timed Charge Enabled",
            "icon": "mdi:export",
            "options": list(modbus.DISABLED_ENABLED.values()),
            "command_topic": "charging/time_charge_enabled",
        },
    },
    # 0xE02D  DischgStartTime1
    "charging/time_discharge_1_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE02D},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge Start Time 1",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_1_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE02E  DischgEndTime1
    "charging/time_discharge_1_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE02E},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge End Time 1",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_1_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE02F  DischgStartTime2
    "charging/time_discharge_2_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE02F},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge Start Time 2",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_2_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE030  DischgEndTime2
    "charging/time_discharge_2_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE030},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge End Time 2",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_2_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE031  DischgStartTime3
    "charging/time_discharge_3_start": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE031},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge Start Time 3",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_3_start",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE032  DischgEndTime3
    "charging/time_discharge_3_end": {
        "enabled": True,
        "value": modbus.read_time_register,
        "args": {"register": 0xE032},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "text",
        "config": {
            "name": "Discharge End Time 3",
            "icon": "mdi:clock",
            "command_topic": "charging/time_discharge_3_end",
            "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        },
    },
    # 0xE033  OnTimeDischgEn
    "charging/time_discharge_enabled": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE033},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Timed Discharge Enabled",
            "icon": "mdi:export",
            "options": list(modbus.DISABLED_ENABLED.values()),
            "command_topic": "charging/time_discharge_enabled",
        },
    },
    #    "inverter/output_priority": {
    #        "value": modbus.read_lookup_register,
    #        "args": {"register": 0xE204, "lookup": modbus.OUTPUT_PRIORITIES},
    #        "interval": general_interval,
    #        "last_update": None,
    #        "topic_type": "select",
    #        "config": {
    #            "name": "Output Priority",
    #            "icon": "mdi:export",
    #            "options": list(modbus.OUTPUT_PRIORITIES.values()),
    #            "command_topic": "inverter/output_priority",
    #        },
    #    },
    # 0xE037  InvToGridEn
    "inverter/hybrid_mode": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE037, "lookup": modbus.HYBRID_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Hybrid Grid Mode",
            "icon": "mdi:export",
            "options": list(modbus.HYBRID_MODES.values()),
            "command_topic": "inverter/hybrid_mode",
        },
    },
    # 0xE039  PvPowerPrioritySet
    "pv/power_priority": {
        "enabled": pv_mppt_trackers >= 1,
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE039, "lookup": modbus.PV_PRIORITY_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "PV Power Priority Mode",
            "icon": "mdi:export",
            "options": list(modbus.PV_PRIORITY_MODES.values()),
            "command_topic": "pv/power_priority",
        },
    },
    # 0xE03B  TimedChg1StopSOC
    "charging/time_charge_1_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE03B, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 1 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_charge_1_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE03C  TimedChg2StopSOC
    "charging/time_charge_2_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE03C, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 2 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_charge_2_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE03D  TimedChg3StopSOC
    "charging/time_charge_3_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE03D, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 3 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_charge_3_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE03E  TimedDchg1StopSOC
    "charging/time_discharge_1_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE03E, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 1 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_discharge_1_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE03F  TimedDchg2StopSOC
    "charging/time_discharge_2_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE03F, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 2 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_discharge_2_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE040  TimedDchg3StopSOC
    "charging/time_discharge_3_soc_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE040, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 3 SOC Limit",
            "icon": "mdi:battery",
            "unit_of_measurement": "%",
            "min": 0,
            "max": 100,
            "step": 1,
            "command_topic": "charging/time_discharge_3_soc_limit",
            "mode:": "box",
        },
    },
    # 0xE047  TimedDchg1MaxPower
    "charging/time_discharge_1_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE047, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 1 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_discharge_1_max_power",
            "mode:": "box",
        },
    },
    # 0xE048  TimedDchg2MaxPower
    "charging/time_discharge_2_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE048, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 2 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_discharge_2_max_power",
            "mode:": "box",
        },
    },
    # 0xE049  TimedDchg3MaxPower
    "charging/time_discharge_3_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE049, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Discharge 3 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_discharge_3_max_power",
            "mode:": "box",
        },
    },
    # 0xE04A  TimedChg1MaxPower
    "charging/time_charge_1_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE04A, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 1 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_charge_1_max_power",
            "mode:": "box",
        },
    },
    # 0xE04B  TimedChg2MaxPower
    "charging/time_charge_2_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE04B, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 2 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_charge_2_max_power",
            "mode:": "box",
        },
    },
    # 0xE04C  TimedChg3MaxPower
    "charging/time_charge_3_max_power": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE04C, "integer": True},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "number",
        "config": {
            "name": "Timed Charge 3 Max Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "min": 0,
            "max": 12000,
            "step": 1,
            "command_topic": "charging/time_charge_3_max_power",
            "mode:": "box",
        },
    },
    # 0xE201  ParallMode
    "inverter/parallel_mode": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE201, "lookup": modbus.PARALLEL_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Parallel Mode",
            "icon": "mdi:information",
            "options": list(modbus.PARALLEL_MODES.values()),
            "entity_category": "config",
            "command_topic": "inverter/parallel_mode",
        },
    },
    # 0xE206  BattEqualChgEnable
    "charging/equalization_enable": {
        "enabled": battery_enabled,
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE206},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Battery Equalization Enable",
            "icon": "mdi:battery-sync",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/equalization_enable",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # "battery/shutdown_voltage": {},

    # 0xE208  OutputVoltSet
    "inverter/output_voltage_set": {
        "value": modbus.read_register_value,
        "args": {"register": 0xE208, "scale": 0.1},
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Output Voltage Set",
            "icon": "mdi:flash-outline",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
        },
    },
    # 0xE209  OutputFreqSet
    "inverter/output_frequency_set": {
        "value": modbus.read_register_value,
        "args": {"register": 0xE209, "scale": 0.01},
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Output Frequency Set",
            "icon": "mdi:pulse",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
            "state_class": "measurement",
        },
    },
    # 0xE20A  MaxChgCurr
    "charging/total_charging_current_limit": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xE20A, "scale": 0.1},
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
            "mode:": "box",
        },
    },
    # 0xE20B  AcVoltRange
    "inverter/ac_voltage_range": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE20B, "lookup": modbus.AC_VOLTAGE_RANGES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "AC Voltage Range",
            "icon": "mdi:information",
            "options": list(modbus.AC_VOLTAGE_RANGES.values()),
            "entity_category": "config",
            "command_topic": "inverter/ac_voltage_range",
        },
    },
    # 0xE20C  PowerSavingMode
    "inverter/power_saving": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE20C},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Power Saving",
            "icon": "mdi:leaf",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/power_saving",
        },
    },
    # 0xE20D  AutoRestartOvLoad
    "inverter/auto_restart_on_overload": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE20D},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Auto Restart on Overload",
            "icon": "mdi:alert-circle",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/auto_restart_on_overload",
        },
    },
    # 0xE20E  AutoRestartOvTemper
    "inverter/auto_restart_on_overheat": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE20E},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Auto Restart on Overheat",
            "icon": "mdi:alert-circle",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/auto_restart_on_overheat",
        },
    },
    # 0xE20F  ChgSourcePriority
    "charging/source_priority": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE20F, "lookup": modbus.CHARGING_SOURCE_PRIORITIES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Charging Source Priority",
            "icon": "mdi:import",
            "options": list(modbus.CHARGING_SOURCE_PRIORITIES.values()),
            "command_topic": "charging/source_priority",
        },
    },
    # 0xE210  AlarmEnable
    "inverter/alarm_enabled": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE210},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Alarm Enabled",
            "icon": "mdi:bell",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/alarm_enabled",
        },
    },
    # 0xE211  AlarmEnWhenSourceLoss
    "inverter/alarm_on_input_loss": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE211},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Alarm On Input Loss",
            "icon": "mdi:bell-alert",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/alarm_on_input_loss",
        },
    },
    # 0xE212  BypEnableWhenOvLoad
    "inverter/auto_bypass_on_overload": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE212},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Auto Bypass on Overload",
            "icon": "mdi:alert-circle",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/auto_bypass_on_overload",
        },
    },
    # 0xE214  BmsErrStopEnable
    "inverter/stop_on_bms_error": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE214},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Stop On BMS Error",
            "icon": "mdi:battery-alert",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/stop_on_bms_error",
        },
    },
    # 0xE215  BmsCommEnable
    "charging/bms_communication": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE215, "lookup": modbus.BMS_COMM_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "BMS Communication",
            "icon": "mdi:import",
            "options": list(modbus.BMS_COMM_MODES.values()),
            "command_topic": "charging/bms_communication",
        },
    },
    # 0xE216  DcLoadSwitch
    "inverter/dc_load_switch": {
        "value": modbus.read_enabled_register,
        "args": {"register": 0xE216},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "DC Load Switch",
            "icon": "mdi:toggle-switch",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "inverter/dc_load_switch",
        },
    },
    # 0xE21B  Rs485BmsProtocol
    "charging/bms_protocol": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE21B, "lookup": modbus.BMS_PROTOCOLS},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "BMS Protocol",
            "icon": "mdi:import",
            "options": list(modbus.BMS_PROTOCOLS.values()),
            "command_topic": "charging/bms_protocol",
        },
    },
    # Unclear on purpose of this register
    #"inverter/gen_charge_disabled": {
    #    "value": modbus.read_register_value,
    #    "args": {"register": 0xE21A, "integer": True},
    #    "interval": general_interval,
    #    "last_update": None,
    #    "config": {
    #        "name": "Gen Charge Disabled",
    #    },
    #},
    # 0xE21F  GenWorkMode
    "inverter/generator_mode": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE21F, "lookup": modbus.GEN_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Generator Work Mode",
            "icon": "mdi:export",
            "options": list(modbus.GEN_MODES.values()),
            "command_topic": "inverter/generator_mode",
        },
    },
    # 0xE42A  BattForGridPowerEn
    "inverter/battery_priority": {
        "value": modbus.read_lookup_register,
        "args": {"register": 0xE42A, "lookup": modbus.BATTERY_DISCHARGE_MODES},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "config": {
            "name": "Battery State Priority",
            "icon": "mdi:export",
            "options": list(modbus.BATTERY_DISCHARGE_MODES.values()),
            "command_topic": "inverter/battery_priority",
        },
    },
    # 0xF02A  EnergyStatisticsDay
    "statistics/last_day_energy": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF02A, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Last Day Energy Statistics",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    ############ Statistics Configuration #####################
    # 0xF02C  GeneratEnergyToGridToday
    "statistics/daily_generated_energy_to_grid": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF02C, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Generated Energy To Grid",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF02D  BatChgAHToday
    "statistics/daily_battery_charged": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF02D, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Battery Charged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF02E  BatDischgAHToday
    "statistics/daily_battery_discharged": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF02E, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Battery Discharged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF02F  GeneratEnergyToday
    "statistics/daily_pv_production": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF02F, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily PV Power Generated",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF030  UsedEnergyToday
    "statistics/daily_load_consumed": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF030, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF031  WorkDaysTotal
    "statistics/operating_days": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF031, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Operating Days",
            "icon": "mdi:calendar",
            "unit_of_measurement": "d",
            "state_class": "total_increasing",
        },
    },
    # 0xF032  GridEnergyTotal
    "statistics/total_grid_generated_energy": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF032, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Generated Energy to Grid",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    ############ Additional Statistics #####################
    # 0xF034  BatChgAHTotal
    "statistics/total_battery_charged": {
        "enabled": battery_enabled,
        "value": modbus.read_long_register,
        "args": {"register": 0xF034},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Battery Charged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF036  BatDischgAHTotal
    "statistics/total_battery_discharged": {
        "enabled": battery_enabled,
        "value": modbus.read_long_register,
        "args": {"register": 0xF036, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Battery Discharged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF038  GeneratEnergyTotal
    "statistics/total_pv_generated_energy": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF038, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Solar Generated Energy",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF03A  UsedEnergyTotal
    "statistics/total_load_consumed": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF03A, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF03C  LineChgEnergyTday
    "statistics/daily_grid_charged": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF03C, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Battery Charging",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF03D  LoadConsumLineTday
    "statistics/daily_grid_consumed": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF03D, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF03E  InvWorkTimeToday
    "statistics/daily_inverter_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF03E, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Inverter Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "min",
        },
    },
    # 0xF03F  LineWorkTimeTodya
    "statistics/daily_grid_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF03F, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "min",
        },
    },
    # 0xF040  PowerOnTime
    "statistics/power_on_time": {
        "value": modbus.read_datetime_register,
        "args": {"register": 0xF040},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Power On Time",
            "icon": "mdi:clock-start",
        },
    },
    # 0xF043  LastEquaChgTime
    "charging/last_equalization_time": {
        "enabled": battery_enabled,
        "value": modbus.read_datetime_register,
        "args": {"register": 0xF043},
        "interval": general_interval,
        "last_update": None,
        "config": {
            "name": "Last Equalization Charge Time",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
        },
    },
    # 0xF046  LineChgEnergyTotal
    "statistics/total_grid_charged": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF046},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Grid Battery Charging",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF048  LoadConsumLineTotal
    "statistics/total_grid_consumed": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF048, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Grid Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF04A  InvWorkTimeTotal
    "statistics/total_inverter_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF04A, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Inverter Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "h",
            "state_class": "total_increasing",
        },
    },
    # 0xF04B  LineWorkTimeTotal
    "statistics/total_grid_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF04B, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Grid Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "h",
            "state_class": "total_increasing",
        },
    },
    # 0xF04C  LineChgKwHTday
    "statistics/daily_grid_charging_kwh": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF04C, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Grid Battery Charging kWh",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    ############ Battery kWh Statistics #####################
    # 0xF04E  BatDischgkWhToday
    "statistics/daily_battery_discharged_kwh": {
        "enabled": battery_enabled,
        "value": modbus.read_register_value,
        "args": {"register": 0xF04E, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Battery Discharged kWh",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF050  BatChgkWhTotal
    "statistics/total_battery_charged_kwh": {
        "enabled": battery_enabled,
        "value": modbus.read_long_register,
        "args": {"register": 0xF050, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Battery Charged kWh",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF052  BatDischgkWhTotal
    "statistics/total_battery_discharged_kwh": {
        "enabled": battery_enabled,
        "value": modbus.read_long_register,
        "args": {"register": 0xF052, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Battery Discharged kWh",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF054  LineChgkWhTotal
    "statistics/total_grid_charged_kwh": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF054, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Grid Charged kWh",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    ############ Generator Statistics #####################
    # 0xF056  GenLoadConsumToday
    "statistics/daily_gen_load_consumed": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF056, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Generator Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF057  GenChgkWhToday
    "statistics/daily_gen_charged": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF057, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Generator Battery Charged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF058  GenLoadConsumTotal
    "statistics/total_gen_load_consumed": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF058, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Generator Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF05A  GenChgkWhTotal
    "statistics/total_gen_charged": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF05A, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Generator Battery Charged",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF05C  GenWorkTimeToday
    "statistics/daily_gen_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF05C, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Generator Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "h",
            "state_class": "total_increasing",
        },
    },
    # 0xF05D  GenWorkTimeTotal
    "statistics/total_gen_work_time": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF05D, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Generator Work Time",
            "icon": "mdi:timer",
            "unit_of_measurement": "h",
            "state_class": "total_increasing",
        },
    },
    ############ Home Load Statistics #####################
    # 0xF05E  HomdLoadConsumTday
    "statistics/daily_home_load_consumed": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF05E, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Daily Home Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF060  HomdLoadConsumTotal
    "statistics/total_home_load_consumed": {
        "value": modbus.read_long_register,
        "args": {"register": 0xF060, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Total Home Load Consumed",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    "battery/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["battery/current"]["last_value"])
            * float(mqtt_config["battery/voltage"]["last_value"]),
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
            "state_class": "measurement",
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
            "state_class": "measurement",
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
            "state_class": "measurement",
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
            "state_class": "measurement",
        },
    },
    "ct/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["ct/power_a"]["last_value"])
            + float(mqtt_config["ct/power_b"]["last_value"])
            + float(mqtt_config["ct/power_c"]["last_value"]),
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "CT Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
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
        "last_value": 0,
        "config": {
            "name": "Home Load Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "grid/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["grid/apparent_power_a"]["last_value"])
            + float(mqtt_config["grid/apparent_power_b"]["last_value"])
            + float(mqtt_config["grid/apparent_power_c"]["last_value"]),
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    "grid/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["grid/power_a"]["last_value"])
            + float(mqtt_config["grid/power_b"]["last_value"])
            + float(mqtt_config["grid/power_c"]["last_value"]),
            1,
        ),
        "interval": grid_interval,
        "last_update": None,
        "config": {
            "name": "Grid Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "inverter/apparent_power_a": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["inverter/voltage_a"]["last_value"])
            * float(mqtt_config["inverter/current_a"]["last_value"]),
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
            "state_class": "measurement",
        },
    },
    "inverter/apparent_power_b": {
        "enabled": split_phase >= 2,
        "value": lambda: round(
            float(mqtt_config["inverter/voltage_b"]["last_value"])
            * float(mqtt_config["inverter/current_b"]["last_value"]),
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
            "state_class": "measurement",
        },
    },
    "inverter/apparent_power_c": {
        "enabled": split_phase >= 3,
        "value": lambda: round(
            float(mqtt_config["inverter/voltage_c"]["last_value"])
            * float(mqtt_config["inverter/current_c"]["last_value"]),
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
            "state_class": "measurement",
        },
    },
    "inverter/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["inverter/apparent_power_a"]["last_value"])
            + float(mqtt_config["inverter/apparent_power_b"]["last_value"])
            + float(mqtt_config["inverter/apparent_power_c"]["last_value"]),
            1,
        ),
        "interval": inverter_interval,
        "last_update": None,
        "config": {
            "name": "Inverter Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    ############ Load ######################
    "load/current_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0219, "scale": 0.1},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Current A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    "load/active_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x021B},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Active Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x021B},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/apparent_power_a": {
        "enabled": split_phase >= 1,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x021C},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power A",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    "load/current_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0230, "scale": 0.1},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Current B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    "load/active_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0232},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Active Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0232},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/apparent_power_b": {
        "enabled": split_phase >= 2,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0234},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power B",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    "load/current_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0231, "scale": 0.1},
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Current C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
        },
    },
    "load/active_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0233},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Active Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0233},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/apparent_power_c": {
        "enabled": split_phase >= 3,
        "value": modbus.read_clamped_register,
        "args": {"register": 0x0235},
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Apparent Power C",
            "icon": "mdi:current-ac",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    "load/active_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["load/active_power_a"]["last_value"])
            + float(mqtt_config["load/active_power_b"]["last_value"])
            + float(mqtt_config["load/active_power_c"]["last_value"]),
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Total Active Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["load/power_a"]["last_value"])
            + float(mqtt_config["load/power_b"]["last_value"])
            + float(mqtt_config["load/power_c"]["last_value"]),
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "last_value": 0,
        "config": {
            "name": "Load Total Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
        },
    },
    "load/apparent_power": {
        "enabled": split_phase >= 1,
        "value": lambda: round(
            float(mqtt_config["load/apparent_power_a"]["last_value"])
            + float(mqtt_config["load/apparent_power_b"]["last_value"])
            + float(mqtt_config["load/apparent_power_c"]["last_value"]),
            1,
        ),
        "interval": load_interval,
        "last_update": None,
        "config": {
            "name": "Load Total Apparent Power",
            "icon": "mdi:flash",
            "unit_of_measurement": "VA",
            "device_class": "apparent_power",
            "state_class": "measurement",
        },
    },
    "inverter/enable_danger": {
        "value": lambda: (mqtt_config["inverter/enable_danger"]["last_value"]),
        "interval": general_interval,
        "last_update": None,
        "topic_type": "select",
        "last_value": "Disabled",
        "config": {
            "name": "Enable Dangerous Operations",
            "icon": "mdi:export",
            "options": list(modbus.DISABLED_ENABLED.values()),
            "command_topic": "inverter/enable_danger",
        },
    },
    "charging/equalization_immediately": {
        "value": 1,
        "topic_type": "button",
        "config": {
            "name": "Start Equalization Now",
            "icon": "mdi:battery-sync",
            "command_topic": "charging/equalization_immediately",
            "availability_topic": EQUALIZATION_AVAIL_TOPIC,
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
    ############ Timed Charge Source Selection (0xE04D) #####################
    "charging/time_charge_1_grid_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 0},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 1 Grid/AC Source",
            "icon": "mdi:transmission-tower",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_1_grid_source",
        },
    },
    "charging/time_charge_1_gen_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 1},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 1 Generator Source",
            "icon": "mdi:engine",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_1_gen_source",
        },
    },
    "charging/time_charge_2_grid_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 2},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 2 Grid/AC Source",
            "icon": "mdi:transmission-tower",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_2_grid_source",
        },
    },
    "charging/time_charge_2_gen_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 3},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 2 Generator Source",
            "icon": "mdi:engine",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_2_gen_source",
        },
    },
    "charging/time_charge_3_grid_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 4},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 3 Grid/AC Source",
            "icon": "mdi:transmission-tower",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_3_grid_source",
        },
    },
    "charging/time_charge_3_gen_source": {
        "enabled": battery_enabled,
        "value": modbus.read_bit_register,
        "args": {"register": 0xE04D, "bit": 5},
        "interval": general_interval,
        "last_update": None,
        "topic_type": "switch",
        "config": {
            "name": "Timed Charge 3 Generator Source",
            "icon": "mdi:engine",
            "entity_category": "config",
            "state_off": "Disabled",
            "state_on": "Enabled",
            "payload_off": "Disabled",
            "payload_on": "Enabled",
            "command_topic": "charging/time_charge_3_gen_source",
        },
    },

    ############ 7-Day History (F000–F028) #####################
    # 0xF000  PV Production Yesterday
    "statistics/pv_production_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF000, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF001  PV Production 2 Days Ago
    "statistics/pv_production_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF001, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF002  PV Production 3 Days Ago
    "statistics/pv_production_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF002, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF003  PV Production 4 Days Ago
    "statistics/pv_production_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF003, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF004  PV Production 5 Days Ago
    "statistics/pv_production_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF004, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF005  PV Production 6 Days Ago
    "statistics/pv_production_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF005, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF006  PV Production 7 Days Ago
    "statistics/pv_production_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF006, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "PV Production — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF007  Battery Charged Yesterday
    "statistics/battery_charged_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF007, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF008  Battery Charged 2 Days Ago
    "statistics/battery_charged_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF008, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF009  Battery Charged 3 Days Ago
    "statistics/battery_charged_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF009, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00A  Battery Charged 4 Days Ago
    "statistics/battery_charged_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00A, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00B  Battery Charged 5 Days Ago
    "statistics/battery_charged_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00B, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00C  Battery Charged 6 Days Ago
    "statistics/battery_charged_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00C, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00D  Battery Charged 7 Days Ago
    "statistics/battery_charged_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00D, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Charged — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00E  Battery Discharged Yesterday
    "statistics/battery_discharged_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00E, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF00F  Battery Discharged 2 Days Ago
    "statistics/battery_discharged_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF00F, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF010  Battery Discharged 3 Days Ago
    "statistics/battery_discharged_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF010, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF011  Battery Discharged 4 Days Ago
    "statistics/battery_discharged_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF011, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF012  Battery Discharged 5 Days Ago
    "statistics/battery_discharged_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF012, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF013  Battery Discharged 6 Days Ago
    "statistics/battery_discharged_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF013, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF014  Battery Discharged 7 Days Ago
    "statistics/battery_discharged_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF014, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Battery Discharged — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF015  Grid Battery Charged Yesterday
    "statistics/grid_battery_charged_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF015, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF016  Grid Battery Charged 2 Days Ago
    "statistics/grid_battery_charged_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF016, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF017  Grid Battery Charged 3 Days Ago
    "statistics/grid_battery_charged_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF017, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF018  Grid Battery Charged 4 Days Ago
    "statistics/grid_battery_charged_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF018, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF019  Grid Battery Charged 5 Days Ago
    "statistics/grid_battery_charged_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF019, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF01A  Grid Battery Charged 6 Days Ago
    "statistics/grid_battery_charged_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01A, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF01B  Grid Battery Charged 7 Days Ago
    "statistics/grid_battery_charged_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01B, "integer": True},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Grid Battery Charged — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "Ah",
            "state_class": "total_increasing",
        },
    },
    # 0xF01C  Load Consumed Yesterday
    "statistics/load_consumed_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01C, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF01D  Load Consumed 2 Days Ago
    "statistics/load_consumed_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01D, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF01E  Load Consumed 3 Days Ago
    "statistics/load_consumed_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01E, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF01F  Load Consumed 4 Days Ago
    "statistics/load_consumed_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF01F, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF020  Load Consumed 5 Days Ago
    "statistics/load_consumed_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF020, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF021  Load Consumed 6 Days Ago
    "statistics/load_consumed_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF021, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF022  Load Consumed 7 Days Ago
    "statistics/load_consumed_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF022, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF023  Load Consumed From Grid Yesterday
    "statistics/load_consumed_from_grid_d0": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF023, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — Yesterday",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF024  Load Consumed From Grid 2 Days Ago
    "statistics/load_consumed_from_grid_d1": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF024, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 2 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF025  Load Consumed From Grid 3 Days Ago
    "statistics/load_consumed_from_grid_d2": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF025, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 3 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF026  Load Consumed From Grid 4 Days Ago
    "statistics/load_consumed_from_grid_d3": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF026, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 4 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF027  Load Consumed From Grid 5 Days Ago
    "statistics/load_consumed_from_grid_d4": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF027, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 5 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF028  Load Consumed From Grid 6 Days Ago
    "statistics/load_consumed_from_grid_d5": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF028, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 6 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
    # 0xF029  Load Consumed From Grid 7 Days Ago
    "statistics/load_consumed_from_grid_d6": {
        "value": modbus.read_register_value,
        "args": {"register": 0xF029, "scale": 0.1},
        "interval": statistics_interval,
        "last_update": None,
        "config": {
            "name": "Load Consumed From Grid — 7 Days Ago",
            "icon": "mdi:chart-bar",
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    },
}
