import os
import minimalmodbus
from datetime import datetime

modbus_addess: int = (
    int(os.getenv("MODBUS_ADDRESS")) if os.getenv("MODBUS_ADDRESS") else 0
)
instr = minimalmodbus.Instrument("/dev/ttyUSB0", 1)
instr.serial.baudrate = 9600
instr.serial.timeout = 1
# instr.debug = True


def debug(msg):
    if os.getenv("DEBUG") == "true":
        print("[{}] {}".format(datetime.now(), msg))


######### System Information #############
def read_cpu_build_time():
    result = instr.read_string(0x021, 20)
    debug("Build Time: " + result)
    return result


def read_serial_number():
    result = instr.read_string(0x035, 20)
    debug("Serial Number: " + result)
    cleaned_result = "".join([char for char in result if char != "\x00"])
    return cleaned_result


def read_minor_version():
    result = instr.read_register(0x00A)
    debug("Minor Version: " + str(result))
    return result


def read_app_version():
    result = instr.read_registers(0x014, 2)
    app_version_str = "v{:.2f}".format(result[0] / 100)
    debug("App Version: " + app_version_str)
    return app_version_str


def read_bootloader_version():
    result = instr.read_registers(0x014, 2)
    bootloader_version_str = "v{:.2f}".format(result[1] / 100)
    debug("Bootloader: " + bootloader_version_str)
    return bootloader_version_str


def read_control_panel_version():
    result = instr.read_registers(0x016, 2)
    control_panel_version_str = "v{:.2f}".format(result[0] / 100)
    debug("Control Panel Version: " + control_panel_version_str)
    return control_panel_version_str


def read_power_amplifier_version():
    result = instr.read_registers(0x016, 2)
    power_amplifier_board_version = "v{:.2f}".format(result[1] / 100)
    debug("Power Amplifier Board Version: " + power_amplifier_board_version)
    return power_amplifier_board_version


def read_rs485_address():
    result = instr.read_register(0x01A)
    debug("RS485 Address: " + str(result))
    return result


def read_model():
    result = instr.read_register(0x01B)
    debug("Model: " + str(result))
    return result


def read_rs485_version():
    result = instr.read_register(0x01C)
    rs485_version_str = "v{:.2f}".format(result / 100)
    debug("RS485 Version: " + rs485_version_str)
    return rs485_version_str


#################### P01 DC Data Area ##################


############ Battery #####################
def read_battery_soc():
    result = instr.read_register(0x100)
    debug("Battery SOC: " + str(result) + "%")
    return result


def read_battery_voltage():
    result = instr.read_register(0x101)
    result = result / 10
    debug("Battery Voltage: " + str(result) + "V")
    return result


def read_battery_current():
    result = instr.read_register(0x102, signed=True)
    result = result / 10
    debug("Battery Current: " + str(result) + "A")
    return result


def read_battery_temperature():
    result = instr.read_register(0x103, signed=True)
    result = result / 10
    debug("Battery Temperature: " + str(result) + "°C")
    return result


############## PV #########################
def read_pv1_voltage():
    result = instr.read_register(0x107)
    result = result / 10
    debug("PV1 Voltage: " + str(result) + "V")
    return result


def read_pv1_current():
    result = instr.read_register(0x108)
    result = result / 10
    debug("PV1 Current: " + str(result) + "A")
    return result


def read_pv1_charge_power():
    result = instr.read_register(0x109)
    debug("PV1 Charge Power: " + str(result) + "W")
    return result


def read_pv_total_power():
    result = instr.read_register(0x10A)
    debug("PV Total Power: " + str(result) + "W")
    return result


def read_charging_state():
    result = instr.read_register(0x010B)
    charging_states = {
        0: "Not Charging",
        1: "Quick Charge",
        2: "Constant Voltage Charge",
        4: "Float Charge",
        6: "Battery Activation",
        8: "Fully Charged",
    }

    state = result
    for key, value in charging_states.items():
        if int(state) == key:
            debug("Charging State: " + value)
            return key

    debug(f"Unknown charging state: {result}")
    return result


def read_charging_power():
    # PV charging power + AC charging power
    result = instr.read_register(0x10E)
    debug("Charging Power: " + str(result) + "W")
    return result


def read_pv2_voltage():
    result = instr.read_register(0x10F)
    result = result / 10
    debug("PV2 Voltage: " + str(result) + "V")
    return result


def read_pv2_current():
    result = instr.read_register(0x110)
    result = result / 10
    debug("PV2 Current: " + str(result) + "A")
    return result


def read_pv2_charge_power():
    result = instr.read_register(0x111)
    debug("PV2 Charge Power: " + str(result) + "W")
    return result


#################### P02 Inverter Data Area ##################


def read_system_date_time():
    results = instr.read_registers(0x20C, 3)
    year = (results[0] >> 8) & 0xFF  # high byte
    month = results[0] & 0xFF  # Low byte
    day = (results[1] >> 8) & 0xFF  # high byte
    hour = results[1] & 0xFF  # Low byte
    minute = (results[2] >> 8) & 0xFF  # high byte
    second = results[2] & 0xFF  # Low byte

    debug(results)
    debug(
        f"System Date/Time: 20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    )

    return f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


def write_system_date_time():
    # Get the current system date and time using datetime.now()
    now = datetime.now()

    year = now.year - 2000  # Convert the year to match the expected format
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second

    data = [
        int(year << 8) + int(month),
        int(day << 8) + int(hour),
        int(minute << 8) + int(second),
    ]
    instr.write_registers(0x20C, data)
    debug(f"System Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")


def read_grid_on_remain_time_state():
    result = instr.read_register(0x20F)
    debug("Grid On/Remain Time State:", result)
    return result


def read_machine_state():
    result = instr.read_register(0x210)
    machine_states = {
        0: "Initialization",
        1: "Standby state",
        2: "AC power operation",
        3: "Inverter operation",
    }

    for key, value in machine_states.items():
        if int(result) == key:
            debug("Machine State: " + value)
            return key

    debug(f"Unknown machine state: {result}")
    return result


def read_bus_voltage():
    result = instr.read_register(0x212)
    result = result / 10
    debug("Bus Voltage: " + str(result) + "V")
    return result


def read_grid_voltage_a():
    result = instr.read_register(0x213)
    result = result / 10
    debug("Grid Voltage A: " + str(result) + "V")
    return result


def read_grid_current_a():
    result = instr.read_register(0x214)
    result = result / 10
    debug("Grid Current A: " + str(result) + "A")
    return result


def read_grid_frequency():
    result = instr.read_register(0x215)
    result = result / 100
    debug("Grid Frequency: " + str(result) + "Hz")
    return result


def read_inverter_voltage_a():
    result = instr.read_register(0x216)
    result = result / 10
    debug("Inverter Voltage A: " + str(result) + "V")
    return result


def read_inverter_current_a():
    result = instr.read_register(0x217)
    result = result / 10
    debug("Inverter Current A: " + str(result) + "A")
    return result


def read_inverter_frequency():
    result = instr.read_register(0x218)
    result = result / 100
    debug("Inverter Frequency: " + str(result) + "Hz")
    return result


def read_load_current_a():
    result = instr.read_register(0x219)
    result = result / 10
    debug("Load Current A: " + str(result) + "A")
    return result


def read_load_active_power_a():
    result = instr.read_register(0x21B)
    result = result
    debug("Load Active Power A: " + str(result) + "W")
    return result


def read_load_reactive_power_a():
    result = instr.read_register(0x21B)
    result = result
    debug("Load Apparent Power VA: " + str(result) + "VA")
    return result


def read_grid_charging_current():
    result = instr.read_register(0x21E)
    result = result / 10
    debug("Grid Charging Current: " + str(result) + "A")
    return result


def read_load_ratio_a():
    result = instr.read_register(0x21F)
    debug("Load Ratio A: " + str(result) + "%")
    return result


def read_temperature_dc_dc():
    result = instr.read_register(0x220, signed=True)
    result = result / 10
    debug("Temperature DC-DC: " + str(result) + "C")
    return result


def read_temperature_dc_ac():
    result = instr.read_register(0x221, signed=True)
    result = result / 10
    debug("Temperature DC-AC: " + str(result) + "C")
    return result


def read_temperature_transformer():
    result = instr.read_register(0x222, signed=True)
    result = result / 10
    debug("Temperature Transformer: " + str(result) + "C")
    return result


def read_temperature_ambient():
    # Sensor not always available
    result = instr.read_register(0x223, signed=True)
    result = result / 10
    debug("Temperature Ambient: " + str(result) + "C")
    return result


def read_pv_charging_current():
    result = instr.read_register(0x224)
    result = result / 10
    debug("PV Charging Current: " + str(result) + "A")
    return result


def read_parallel_load_avg_current():
    result = instr.read_register(0x225)
    result = result / 10
    debug("Parallel Load Avg Current: " + str(result) + "A")
    return result


def read_pbus_voltage():
    result = instr.read_register(0x228)
    result = result / 10
    debug("PBus Voltage: " + str(result) + "V")
    return result


def read_nbus_voltage():
    result = instr.read_register(0x229)
    result = result / 10
    debug("NBus Voltage: " + str(result) + "V")
    return result


def read_grid_voltage_b():
    result = instr.read_register(0x22A)
    result = result / 10
    debug("Grid Voltage B: " + str(result) + "V")
    return result


def read_grid_voltage_c():
    result = instr.read_register(0x22B)
    result = result / 10
    debug("Grid Voltage C: " + str(result) + "V")
    return result


def read_inverter_voltage_b():
    result = instr.read_register(0x22C)
    result = result / 10
    debug("Inverter Voltage B: " + str(result) + "V")
    return result


def read_inverter_voltage_c():
    result = instr.read_register(0x22D)
    result = result / 10
    debug("Inverter Voltage C: " + str(result) + "V")
    return result


def read_inverter_current_b():
    result = instr.read_register(0x22E)
    result = result / 10
    debug("Inverter Current B: " + str(result) + "A")
    return result


def read_inverter_current_c():
    result = instr.read_register(0x22F)
    result = result / 10
    debug("Inverter Current C: " + str(result) + "A")
    return result


def read_load_current_b():
    result = instr.read_register(0x230)
    result = result / 10
    debug("Load Current B: " + str(result) + "A")
    return result


def read_load_current_c():
    result = instr.read_register(0x231)
    result = result / 10
    debug("Load Current C: " + str(result) + "A")
    return result


def read_load_active_power_b():
    result = instr.read_register(0x232)
    debug("Load Active Power B: " + str(result) + "W")
    return result


def read_load_active_power_c():
    result = instr.read_register(0x233)
    debug("Load Active Power C: " + str(result) + "W")
    return result


def read_load_reactive_power_b():
    result = instr.read_register(0x234)
    debug("Load Reactive Power B: " + str(result) + "VA")
    return result


def read_load_reactive_power_c():
    result = instr.read_register(0x235)
    debug("Load Reactive Power C: " + str(result) + "VA")
    return result


def read_load_ratio_b():
    result = instr.read_register(0x236)
    debug("Load Ratio B: " + str(result) + "%")
    return result


def read_load_ratio_c():
    result = instr.read_register(0x237)
    debug("Load Ratio C: " + str(result) + "%")
    return result


def read_grid_current_b():
    result = instr.read_register(0x238)
    result = result / 10
    debug("Grid Current B: " + str(result) + "A")
    return result


def read_grid_current_c():
    result = instr.read_register(0x239)
    result = result / 10
    debug("Grid Current C: " + str(result) + "A")
    return result


def read_grid_active_power_a():
    # negative value when inverter is consuming power from the grid
    # positive value when inverter is exporting power to the grid
    result = instr.read_register(0x23A, signed=True)
    debug("Grid Active Power A: " + str(result) + "W")
    return result


def read_grid_active_power_b():
    # negative value when inverter is consuming power from the grid
    # positive value when inverter is exporting power to the grid
    result = instr.read_register(0x23B, signed=True)
    debug("Grid Active Power B: " + str(result) + "W")
    return result


def read_grid_active_power_c():
    # negative value when inverter is consuming power from the grid
    # positive value when inverter is exporting power to the grid
    result = instr.read_register(0x23C, signed=True)
    debug("Grid Active Power C: " + str(result) + "W")
    return result


def read_grid_reactive_power_a():
    result = instr.read_register(0x23D)
    debug("Grid Reactive Power A: " + str(result) + "VA")
    return result


def read_grid_reactive_power_b():
    result = instr.read_register(0x23E)
    debug("Grid Reactive Power B: " + str(result) + "VA")
    return result


def read_grid_reactive_power_c():
    result = instr.read_register(0x23F)
    debug("Grid Reactive Power C: " + str(result) + "VA")
    return result


#################### P03 Device Control Area ##################


def write_power_off_on(value):
    # 0: Off, 1: On
    instr.write_register(0xDF00, int(value))
    debug("Power " + ("Off" if value == 0 else "On"))


def write_reset(value):
    # 1: Reset
    instr.write_register(0xDF01, int(value))
    debug("Reset")


def write_restore_factory_setting(value):
    # 1: Restore Factory Setting
    # 2: Clear statistics
    # 3: Clear errors

    if value == "1":
        instr.write_register(0xDF02, 0xAA)
        debug("Restore Factory Setting")
    elif value == "2":
        instr.write_register(0xDF02, 0xBB)
        debug("Clear statistics")
    elif value == "3":
        instr.write_register(0xDF02, 0xCC)
        debug("Clear errors")


def write_battery_equal_charging_immediately(value):
    instr.write_register(0xDF0D, int(value))
    debug("Battery Equal Charging Immediately: " + str(value))


#################### P05 Setting Area for Battery-related Parameters ##################
def read_pv_charging_current_limit():
    # documentation says max 150A but mine returned 200A...
    # TODO: check the documentation
    result = instr.read_register(0xE001)
    result = result / 10
    debug("PV Charging Current Limit: " + str(result) + "A")
    return result


def write_pv_charging_current_limit(value):
    result = instr.write_register(0xE001, int(float(value) * 10))
    debug("PV Charging Current Limit set to: " + str(value))
    return result


def read_battery_rate_voltage():
    # not sure why you would chnge this value though
    # most inverter cannot do all voltages 12v/24V/36v/48v
    # This data need to be pulled on start to configure other configuration
    result = instr.read_register(0xE003)
    debug("Battery Rate Voltage: " + str(result) + "V")
    return result


def read_battery_type_set():
    result = instr.read_register(0xE004)
    battery_types = {
        0: "User defined",
        1: "SLD",
        2: "FLD",
        3: "GEL",
        4: "LFP 14 cells",
        5: "LFP 15 cells",
        6: "LFP 16 cells",
        7: "LFP 7 cells",
        8: "LFP 8 cells",
        9: "LFP 9 cells",
        10: "Ternary lithium 7 cells",
        11: "Ternary lithium 8 cells",
        12: "Ternary lithium 13 cells",
        13: "Ternary lithium 14 cells",
        14: "No Battery",
    }

    state = result
    for key, value in battery_types.items():
        if int(state) == key:
            debug("Battery type: " + value)
            return key
    debug("Battery type not recognized.")
    return result


def write_battery_type_set(value: str):
    instr.write_register(0xE004, int(value))


## TODO: maybe at some point we want to init and pull this before anything else
battery_rate: float = read_battery_rate_voltage() / 12


def read_battery_overcharge_protection_voltage():
    result = instr.read_register(0xE005)
    result = (result / 10) * battery_rate
    debug("Battery Overcharge Protection Voltage: " + str(result) + "V")
    return result


def write_battery_overcharge_protection_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE005, value)


def read_battery_charge_limit_voltage():
    result = instr.read_register(0xE006)
    result = (result / 10) * battery_rate
    debug("Battery Charge Limit Voltage: " + str(result) + "V")
    return result


def write_battery_charge_limit_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE006, value)


def read_battery_balancing_voltage():
    result = instr.read_register(0xE007)
    result = (result / 10) * battery_rate
    debug("Battery Charge Balancing Voltage: " + str(result) + "V")
    return result


def write_battery_balancing_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)

    instr.write_register(0xE007, value)


def read_battery_overcharge_voltage():
    result = instr.read_register(0xE008)
    result = (result / 10) * battery_rate
    debug("Battery Overcharge Voltage: " + str(result) + "V")
    return result


def write_battery_overcharge_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE008, value)


def read_battery_float_charge_voltage():
    result = instr.read_register(0xE009)
    result = (result / 10) * battery_rate
    debug("Battery Float Charge Voltage: " + str(result) + "V")
    return result


def write_battery_float_charge_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE009, value)


def read_battery_charging_return_voltage():
    result = instr.read_register(0xE00A)
    result = (result / 10) * battery_rate
    debug("Battery Charging Return Voltage: " + str(result) + "V")
    return result


def write_battery_charging_return_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE00A, value)


def read_battery_overdischarge_return_voltage():
    result = instr.read_register(0xE00B)
    result = (result / 10) * battery_rate
    debug("Battery Overdischarge Return Voltage: " + str(result) + "V")
    return result


def write_battery_overdischarge_return_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE00B, value)


def read_battery_undervoltage_warning():
    result = instr.read_register(0xE00C)
    result = (result / 10) * battery_rate
    debug("Battery Undervoltage Warning Voltage: " + str(result) + "V")
    return result


def write_battery_undervoltage_warning(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE00C, value)


def read_battery_overdischarge_warning():
    result = instr.read_register(0xE00D)
    result = (result / 10) * battery_rate
    debug("Battery Overdischarge Warning Voltage: " + str(result) + "V")
    return result


def write_battery_overdischarge_warning(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE00D, value)


def read_battery_discharge_limit_voltage():
    result = instr.read_register(0xE00E)
    result = (result / 10) * battery_rate
    debug("Battery Discharge Limit Voltage: " + str(result) + "V")
    return result


def write_battery_discharge_limit_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    instr.write_register(0xE00E, value)


def read_battery_stop_state_of_charge():
    result = instr.read_register(0xE00F)
    debug("Battery Stop State of Charge Voltage: " + str(result) + "%")
    return result


def write_battery_stop_state_of_charge(value: str):
    if len(value) == 0:
        return
    instr.write_register(0xE00F, int(value))


def read_battery_overdischarge_delay_time():
    result = instr.read_register(0xE010)
    debug("Battery Overdischarge Delay Time: " + str(result) + "s")
    return result


def write_battery_overdischarge_delay_time(value: str):
    if len(value) == 0:
        return
    instr.write_register(0xE010, int(value))


def read_battery_balancing_charge_time():
    result = instr.read_register(0xE011)
    debug("Battery Balancing Charge Time: " + str(result) + "min")
    return result


def write_battery_balancing_charge_time(value: str):
    if len(value) == 0:
        return
    instr.write_register(0xE011, int(value))


def read_battery_improve_charge_time():
    result = instr.read_register(0xE012)
    debug("Battery Improve Charge Time: " + str(result) + "min")
    return result


def write_battery_improve_charge_time(value: str):
    if len(value) == 0:
        return
    instr.write_register(0xE012, int(value))


def read_battery_balancing_charge_interval():
    result = instr.read_register(0xE013)
    debug("Battery Balancing Charge Interval: " + str(result) + "days")
    return result


def write_battery_balancing_charge_interval(value: str):
    instr.write_register(0xE013, int(value))


def read_battery_dc_switch_low_voltage():
    result = instr.read_register(0xE01B)
    result = (result / 10) * battery_rate
    debug("Battery Switch Load to AC when low voltage: " + str(result) + "V")
    return result


def write_battery_dc_switch_low_voltage(value: str):
    value = float(value) / battery_rate * 10
    instr.write_register(0xE01B, int(value))


def read_stop_charging_current_set():
    """
    Only the lithium battery is effective, and when the current of constant-voltage charging state is lower than this value, the charging is stopped.
    """
    result = instr.read_register(0xE01C)
    result = result / 10
    debug("Stop charging when current below: " + str(result) + "A")
    return result


def write_stop_charging_current_set(value: str):
    value = float(value) * 10
    instr.write_register(0xE01C, int(value))


def read_stop_charging_soc_set():
    """
    When the SOC capacity is greater than or equal to this value, charging is stopped, and it is valid for BMS communication.
    """
    result = instr.read_register(0xE01D)
    debug("Stop Charging SOC Set: " + str(result) + "%")
    return result


def write_stop_charging_soc_set(value: str):
    instr.write_register(0xE01D, int(value))


def read_battery_soc_low_alarm():
    result = instr.read_register(0xE01E)
    debug("Battery SOC Low Alarm: " + str(result) + "%")
    return result


def write_battery_soc_low_alarm(value: str):
    instr.write_register(0xE01E, int(value))


def read_battery_soc_switch_to_line():
    result = instr.read_register(0xE01F)
    debug("Battery SOC Switch load to AC when below: " + str(result) + "%")
    return result


def write_battery_soc_switch_to_line(value: str):
    instr.write_register(0xE01F, int(value))


def read_battery_soc_switch_to_battery():
    result = instr.read_register(0xE020)
    debug("Battery SOC Switch back to Battery: " + str(result) + "%")
    return result


def write_battery_soc_switch_to_battery(value: str):
    instr.write_register(0xE020, int(value))


def read_battery_voltage_switch_to_inverter():
    """
    When the battery voltage is higher than the judged point, the inverter is switched back.
    """
    result = instr.read_register(0xE022)
    result = (result / 10) * battery_rate
    debug("Battery Voltage Switch to Inverter: " + str(result) + "V")
    return result


def write_battery_voltage_switch_to_inverter(value: str):
    value = float(value) / battery_rate * 10
    instr.write_register(0xE022, int(value))


def read_battery_balancing_charge_timeout():
    result = instr.read_register(0xE023)
    debug("Battery Balancing Charge Timeout: " + str(result) + "min")
    return result


def write_battery_balancing_charge_timeout(value: str):
    """
    steps = 5
    """
    instr.write_register(0xE023, int(value))


def read_lithium_battery_active_current_set():
    result = instr.read_register(0xE024)
    result = result / 10
    debug("Lithium Battery Active Current Set: " + str(result) + "A")
    return result


def write_lithium_battery_active_current_set(value: str):
    value = float(value) * 10
    instr.write_register(0xE024, int(value))


def read_bms_charging_limit_current_mode_setting():
    """
    TODO: need to find the correct value
    0: HMI setting
    1: BMS protocol
    2: Inverter logic
    """
    result = instr.read_register(0xE025)
    debug("BMS Charging Limit Current Mode: " + str(result))
    return result


def write_bms_charging_limit_current_mode_setting(value):
    instr.write_register(0xE025, int(value))
    debug("BMS Charging Limit Current Mode: " + str(value))


def read_charge_start_time_1():
    # Hours and minutes: 23h*256+59min=5,947
    result = instr.read_register(0xE026)
    ## extract hours and minutes from the register value
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge Start Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_start_time_1(value: str):
    ## split value from :
    hours, minutes = map(int, value.split(":"))
    ## combine hours and minutes into a single 16-bit integer
    combined = (hours << 8) | minutes
    ## write the combined value to the register
    instr.write_register(0xE026, combined)
    debug("Charge Start Time 1 set to " + str(hours) + "h" + str(minutes) + "min")


def read_charge_end_time_1():
    result = instr.read_register(0xE027)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_1(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE027, combined)
    debug("Charge End Time 1 set to " + str(hours) + "h" + str(minutes) + "min")


def read_charge_start_time_2():
    result = instr.read_register(0xE028)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge Start Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_start_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE028, combined)
    debug("Charge Start Time 2 set to " + str(hours) + "h" + str(minutes) + "min")


def read_charge_end_time_2():
    result = instr.read_register(0xE029)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE029, combined)
    debug("Charge End Time 2 set to " + str(hours) + "h" + str(minutes) + "min")


def read_charge_start_time_3():
    result = instr.read_register(0xE02A)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge Start Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_start_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE02A, combined)
    debug("Charge Start Time 3 set to " + str(hours) + "h" + str(minutes) + "min")


def read_charge_end_time_3():
    result = instr.read_register(0xE02B)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE02B, combined)
    debug("Charge End Time 3 set to " + str(hours) + "h" + str(minutes) + "min")


def read_time_charge_enabled():
    # 0:Disabled, 1:Enabled
    result = instr.read_register(0xE02C)
    debug("Charge Time Enabled: " + str(result))
    return result


def read_discharge_start_time_1():
    # Hours and minutes: 23h*256+59min=5,947
    result = instr.read_register(0xE02D)
    ## extract hours and minutes from the register value
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge Start Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_start_time_1(value: str):
    ## split value from :
    hours, minutes = map(int, value.split(":"))
    ## combine hours and minutes into a single 16-bit integer
    combined = (hours << 8) | minutes
    ## write the combined value to the register
    instr.write_register(0xE02D, combined)
    debug("Discharge Start Time 1 set to " + str(hours) + "h" + str(minutes) + "min")


def read_discharge_end_time_1():
    result = instr.read_register(0xE02E)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_1(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE02E, combined)
    debug("Discharge End Time 1 set to " + str(hours) + "h" + str(minutes) + "min")


def read_discharge_start_time_2():
    result = instr.read_register(0xE02F)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge Start Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_start_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE02F, combined)
    debug("Discharge Start Time 2 set to " + str(hours) + "h" + str(minutes) + "min")


def read_discharge_end_time_2():
    result = instr.read_register(0xE030)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE030, combined)
    debug("Discharge End Time 2 set to " + str(hours) + "h" + str(minutes) + "min")


def read_discharge_start_time_3():
    result = instr.read_register(0xE031)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge Start Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_start_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE031, combined)
    debug("Discharge Start Time 3 set to " + str(hours) + "h" + str(minutes) + "min")


def read_discharge_end_time_3():
    result = instr.read_register(0xE032)
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    instr.write_register(0xE032, combined)
    debug("Discharge End Time 3 set to " + str(hours) + "h" + str(minutes) + "min")


def read_time_discharge_enabled():
    # 0:Disabled, 1:Enabled
    result = instr.read_register(0xE02C)
    debug("Charge Time Enabled: " + str(result))
    return result


def read_pv_power_priority_set():
    result = instr.read_register(0xE039)
    priority_mode = {0: "Charging priority", 1: "Load priority"}
    debug("PV Power Priority Set: " + priority_mode[result])
    return result


def write_pv_power_priority_set(value: str):
    instr.write_register(0xE039, int(value))


#################### P07 User Setting Area for Inverter Parameters ##################
def read_rs485_address_set():
    result = instr.read_register(0xE200)
    debug(f"RS-485 Address Set: {result}")
    return result


def read_parallel_mode():
    result = instr.read_register(0xE201)
    parallel_mode = {
        0: "Single machine",
        1: "Single-phase parallel",
        2: "Two-phase parallel",
        3: "Two-phase parallel 120",
        4: "Two-phase parallel 180",
        5: "Three-phase A",
        6: "Three-phase B",
        7: "Three-phase C",
    }
    debug("Parallel Mode: " + parallel_mode[result])
    return result


def write_parallel_mode(value: str):
    instr.write_register(0xE201, int(value))


def read_output_priority():
    result = instr.read_register(0xE204)
    output_priority = {0: "Solar first", 1: "Utility first", 2: "Solar/Battery/Utility"}
    if result in output_priority:
        debug("Output Priority: " + output_priority[result])
        return output_priority[result]

    return result


def write_output_priority(value: str):
    print(value)
    output_priority = {"Solar first": 0, "Utility first": 1, "Solar/Battery/Utility": 2}
    if value in output_priority:
        int_value = output_priority[value]
        print(int_value)
        instr.write_register(0xE204, int_value)


def read_grid_charging_current_limit():
    result = instr.read_register(0xE005)
    result = result / 10
    debug("Grid Charging Current Limit: " + str(result) + "A")
    return result


def write_grid_charging_current_limit(value: str):
    value = float(value) * 10
    instr.write_register(0xE005, int(value))


def read_battery_balance_charging_enable():
    result = instr.read_register(0xE206)
    enable = {0: "Disable", 1: "Enable"}
    debug("Battery Equal Charging Enable: " + enable[result])
    return result


def write_battery_balance_charging_enable(value: str):
    instr.write_register(0xE206, int(value))


def read_output_voltage_set():
    result = instr.read_register(0xE208)
    result = result / 10
    debug("Output Voltage Set: " + str(result) + "V")
    return result


def read_output_frequency_set():
    result = instr.read_register(0xE209)
    result = result / 100
    debug("Output Frequency Set: " + str(result) + "Hz")
    return result


def read_total_charging_current_limit():
    result = instr.read_register(0xE20A)
    result = result / 10
    debug("Total Charging Current Limit: " + str(result) + "A")
    return result


def write_total_charging_current_limit(value: str):
    value = float(value) * 10
    instr.write_register(0xE20A, int(value))


def read_ac_voltage_range():
    result = instr.read_register(0xE20B)
    range = {
        0: "Wide band (APL)",
        1: "Narrow band (UPS)",
    }
    debug("AC Voltage Range: " + range[result])
    return result


def write_ac_voltage_range(value: str):
    value = int(value)
    instr.write_register(0xE20B, value)


def read_power_saving_mode():
    result = instr.read_register(0xE20C)
    enable = {0: "Disable", 1: "Enable"}
    debug("Power Saving Mode: " + enable[result])
    return result


def write_power_saving_mode(value: str):
    print("power saving: " + value)
    instr.write_register(0xE20C, int(value))


def read_auto_restart_on_overload():
    result = instr.read_register(0xE20D)
    enable = {0: "Disable", 1: "Enable"}
    debug("Auto Restart On Overload: " + enable[result])
    return result


def write_auto_restart_on_overload(value: str):
    instr.write_register(0xE20D, int(value))


def read_auto_restart_on_overheat():
    result = instr.read_register(0xE20E)
    enable = {0: "Disable", 1: "Enable"}
    debug("Auto Restart On Overheat: " + enable[result])
    return result


def write_auto_restart_on_overheat(value: str):
    instr.write_register(0xE20E, int(value))


def read_charging_source_priority():
    result = instr.read_register(0xE20F)
    priority = {
        0: "Solar first",  # (AC power charging available when PV fails)",
        1: "Utility first",  # (PV charging available when AC fails)",
        2: "Solar and utility simultaneously",  # (AC power and PV charging at the same time, with PV priority)",
        3: "Solar only",
    }
    if result in priority:
        debug("Charging Source Priority: " + priority[result])
        return priority[result]
    return result


def write_charging_source_priority(value: str):
    priority = {
        "Solar first": 0,  # (AC power charging available when PV fails)",
        "Utility first": 1,  # (PV charging available when AC fails)",
        "Solar and utility simultaneously": 2,  # (AC power and PV charging at the same time, with PV priority)",
        "Solar only": 3,
    }
    if value in priority:
        int_value = priority[value]
        instr.write_register(0xE20F, int_value)


def read_alarm_enabled():
    result = instr.read_register(0xE210)
    enable = {0: "Disable", 1: "Enable"}
    debug("Alarm Enabled: " + enable[result])
    return result


def write_alarm_enabled(value: str):
    instr.write_register(0xE210, int(value))


def read_alarm_enabled_on_input_loss():
    result = instr.read_register(0xE211)
    enable = {0: "Disable", 1: "Enable"}
    debug("Alarm Enabled On Input Loss: " + enable[result])
    return result


def write_alarm_enabled_on_input_loss(value: str):
    instr.write_register(0xE211, int(value))


def read_bypass_on_overload():
    result = instr.read_register(0xE212)
    enable = {0: "Disable", 1: "Enable"}
    debug("Bypass On Overload: " + enable[result])
    return result


def write_bypass_on_overload(value: str):
    instr.write_register(0xE212, int(value))


def read_stop_on_bms_error_enabled():
    result = instr.read_register(0xE214)
    enable = {0: "Disable", 1: "Enable"}
    debug("Stop On BMS Error Enabled: " + enable[result])
    return result


def write_stop_on_bms_error_enabled(value: str):
    instr.write_register(0xE214, int(value))


def read_bms_communication_enabled():
    result = instr.read_register(0xE215)
    enable = {
        0: "Disable",
        1: "485-BMS enabled",
        2: "CAN-BMS enabled",
    }
    debug("BMS Communication: " + enable[result])
    return result


def write_bms_communication_enabled(value: str):
    instr.write_register(0xE215, int(value))


def read_dc_load_switch():
    result = instr.read_register(0xE216)
    enable = {0: "Disable", 1: "Enable"}
    debug("DC Load Switch: " + enable[result])
    return result


def write_dc_load_switch(value: str):
    value = int(value)
    instr.write_register(0xE216, value)


#################### P08 Setting Area for Inverter Grid-connection Parameters ###############


def read_battery_discharge_enabled():
    result = instr.read_register(0xE42A)
    priority = {
        0: "Standby",
        1: "Battery discharge for Load",  # (PV charging available when AC fails)",
        2: "Battery discharge for home",  # (AC power and PV charging at the same time, with PV priority)",
        3: "Battery discharge for grid",
    }
    if result in priority:
        debug("Battery Discharge Enabled: " + priority[result])
        return priority[result]
    return result


def write_battery_discharge_enabled(value: str):
    priority = {
        "Standby": 0,  # (AC power charging available when PV fails)",
        "Battery discharge for Load": 1,  # (PV charging available when AC fails)",
        "Battery discharge for home": 2,  # (AC power and PV charging at the same time, with PV priority)",
        "Battery discharge for grid": 3,
    }
    if value in priority:
        int_value = priority[value]
        instr.write_register(0xE42A, int_value)


#################### P09 Power Statistics Historical Data ##################
def read_total_pv_energy_last_7_days():
    # extract data from the last 7 days
    result = instr.read_registers(0xF000, 7)
    for i in range(len(result)):
        result[i] = result[i] / 10
    print("Total PV Energy Last 7 days: " + "kWh, ".join(map(str, result)) + "kWh")
    return result


def read_total_battery_charge_energy_last_7_days():
    result = instr.read_registers(0xF007, 7)
    print("Total Battery Charged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah")
    return result


def read_total_battery_discharge_energy_last_7_days():
    result = instr.read_registers(0xF00E, 7)
    print(
        "Total Battery Discharged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah"
    )
    return result


def read_total_line_charge_energy_last_7_days():
    result = instr.read_registers(0xF015, 7)
    print("Total Line Charged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah")
    return result


def read_total_load_consume_last_7_days():
    result = instr.read_registers(0xF01C, 7)
    for i in range(len(result)):
        result[i] = result[i] / 10
    print("Total Load Consume Last 7 days: " + "kWh, ".join(map(str, result)) + "kWh")
    return result


def read_total_load_consume_from_line_last_7_days():
    result = instr.read_registers(0xF023, 7)
    for i in range(len(result)):
        result[i] = result[i] / 10
    print(
        "Total Load Consume From Line Last 7 days: "
        + "kWh, ".join(map(str, result))
        + "kWh"
    )
    return result


def read_total_last_day_energy_statistics():
    result = instr.read_long(0xF02A, byteorder=1)
    result = result / 10
    debug("Total Last Day Energy Statistics : " + str(result) + "kWh")
    return result


def read_total_generated_energy_to_grid_today():
    result = instr.read_register(0xF02C)
    result = result / 10
    debug("Total Generated Energy to Grid Today: " + str(result) + "kWh")
    return result


def read_total_battery_charged_today():
    result = instr.read_register(0xF02D)
    debug("Total Battery Charged Today: " + str(result) + "Ah")
    return result


def read_total_battery_discharged_today():
    result = instr.read_register(0xF02E)
    debug("Total Battery Discharged Today: " + str(result) + "Ah")
    return result


def read_total_pv_power_generated_today():
    result = instr.read_register(0xF02F)
    result = result / 10
    debug("Total PV Power Generated Today: " + str(result) + "kWh")
    return result


def read_total_load_consumed_today():
    result = instr.read_register(0xF030)
    result = result / 10
    debug("Total Load Consumed Today: " + str(result) + "kWh")
    return result


def read_total_operating_days():
    result = instr.read_register(0xF031)
    result = result / 10
    debug("Total Operating Days: " + str(result) + "days")
    return result


def read_total_grid_energy_total():
    result = instr.read_long(0xF032, byteorder=1)
    debug(result)
    result = result / 10
    debug("Total Grid Energy: " + str(result) + "kWh")
    return result


def read_total_battery_charging_total():
    result = instr.read_long(0xF034, byteorder=1)
    result = result
    debug("Total Battery Charging: " + str(result) + "Ah")
    return result


def read_total_battery_discharging_total():
    result = instr.read_long(0xF036, byteorder=1)
    result = result
    debug("Total Battery Discharging: " + str(result) + "Ah")
    return result


def read_total_pv_generated_energy_total():
    result = instr.read_long(0xF038, byteorder=1)
    result = result / 10
    debug("Total PV Generated Energy: " + str(result) + "kWh")
    return result


def read_total_load_consumption_total():
    result = instr.read_long(0xF03A, byteorder=1)
    result = result / 10
    debug("Total Load consumption Energy: " + str(result) + "kWh")
    return result


def read_total_grid_charged_today():
    result = instr.read_register(0xF03C)
    debug("Total Grid Charged Today: " + str(result) + "Ah")
    return result


def read_total_grid_consumed_today():
    result = instr.read_register(0xF03D)
    result = result / 10
    debug("Total Load Consumed Today: " + str(result) + "kWh")
    return result


def read_total_inverter_worktime_today():
    result = instr.read_register(0xF03E)
    debug("Total Inverter Worktime Today: " + str(result) + "min")
    return result


def read_total_line_worktime_today():
    result = instr.read_register(0xF03F)
    debug("Total Line Worktime Today: " + str(result) + "min")
    return result


def read_total_power_on_time():
    results = instr.read_registers(0xF040, 3)

    year = (results[0] >> 8) & 0xFF  # high byte
    month = results[0] & 0xFF  # Low byte
    day = (results[1] >> 8) & 0xFF  # high byte
    hour = results[1] & 0xFF  # Low byte
    minute = (results[2] >> 8) & 0xFF  # high byte
    second = results[2] & 0xFF  # Low byte

    debug(
        f"Power on time: 20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    )
    return f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


def read_total_last_balancing_charge_time():
    results = instr.read_registers(0xF043, 3)

    year = (results[0] >> 8) & 0xFF  # high byte
    month = results[0] & 0xFF  # Low byte
    day = (results[1] >> 8) & 0xFF  # high byte
    hour = results[1] & 0xFF  # Low byte
    minute = (results[2] >> 8) & 0xFF  # high byte
    second = results[2] & 0xFF  # Low byte

    debug(
        f"Last balancing charge time: 20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    )
    return f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


def read_total_grid_charged_total():
    result = instr.read_long(0xF046, byteorder=1)
    debug("Total Grid Charged Total: " + str(result) + "Ah")
    return result


def read_total_grid_consumed_today():
    result = instr.read_long(0xF048, byteorder=1)
    result = result / 10
    debug("Total Load Consumed Total: " + str(result) + "kWh")
    return result


def read_total_inverter_work_time_total():
    result = instr.read_register(0xF04A)
    debug("Total Inverter Work Time Total: " + str(result) + "h")
    return result


def read_total_grid_work_time_total():
    result = instr.read_register(0xF04B)
    debug("Total Grid Work Time Total: " + str(result) + "h")
    return result


def read_total_grid_chrging_power_today():
    result = instr.read_register(0xF04C)
    result = result / 10
    debug("Total Load Consumed Total: " + str(result) + "kWh")
    return result


############# P10 Fault Record ########################
def read_errors():
    for i in range(32):
        results = instr.read_registers(0xF800 + (0x10 * i), 16)

        error_code = results[0]
        if error_code == 0:
            break
        description = __error_lists(error_code)
        year = (results[1] >> 8) & 0xFF  # high byte
        month = results[1] & 0xFF  # Low byte
        day = (results[2] >> 8) & 0xFF  # high byte
        hour = results[2] & 0xFF  # Low byte
        minute = (results[3] >> 8) & 0xFF  # high byte
        second = results[3] & 0xFF  # Low byte

        date = (
            f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        )

        data = results[4::]

        print(error_code, description, date, data)


def __error_lists(code: int):
    errors = {
        1: "Battery undervoltage alarm",
        2: "Battery discharge average current overcurrent (software protection)",
        3: "Battery not-connected alarm",
        4: "Battery undervoltage stop discharge alarm",
        5: "Battery overcurrent (hardware protection)",
        6: "Charging overvoltage protection",
        7: "Bus overvoltage (hardware protection)",
        8: "Bus overvoltage (software protection)",
        9: "PV overvoltage protection",
        10: "Boost overcurrent (software protection)",
        11: "Boost overcurrent (hardware protection)",
        12: "Master-slave HES communcation failure",
        13: "Bypass overload protection",
        14: "Inverter overload protection",
        15: "Inverter overcurrent hardware protection",
        16: "Requesting a shutdown fault from the chip",
        17: "Inverter short-circuit protection",
        18: "Bus soft start failure",
        19: "Buck heat sink over temperature protection",
        20: "Inverter AC output with load or AC charging radiator over-temperature protection",
        21: "Fan blockage or faulure fault",
        22: "Memory failure",
        23: "Model setting error",
        24: "Positive and negative bus voltage imbalance",
        25: "Bustbar short circuit",
        26: "Inverter AC output backfeed to bypass AC output",
        28: "Utility input phase error",
        29: "Low bus voltage protection",
        30: "Alarm given when battery capacity rate is lower than 10% (setting BMS to enable validity)",
        31: "Alarm given when battery capacity rate is lower than 5% (setting BMS to enable validity)",
        32: "Inverter stops when battery capacity is low (setting BMS to enable validity)",
        34: "CAN communcation fault in parallel operation",
        35: "Parallel ID (communcation address) setting error",
        37: "Parallel current sharing fault",
        38: "Large battery voltage difference in parallel mode",
        39: "Inconsistent AC input source in parallel mode",
        40: "Hardware synchronization signal error in parallel mode",
        41: "Inverter DC voltage error",
        42: "Inconsistent system firmware version in parallel mode",
        43: "Parallel line connection error in parallel mode",
        44: "No serial number set at factory",
        45: 'item "Parallel" setting error',
        49: "Selects the local corresponding grod standard (Grid over voltage)",
        50: "Selects the local corresponding grod standard (Grid under voltage)",
        51: "Selects the local corresponding grod standard (Grid over frequency)",
        52: "Selects the local corresponding grod standard (Grid under frequency)",
        53: "Selects the local corresponding grod standard (Grid loss)",
        54: "Selects the local corresponding grod standard (Grid DC current over)",
        55: "Selects the local corresponding grod standard (Grid standard un init)",
        56: "PV1+, PV2+, PV- abnormally low impedance to ground",
        57: "System leakage current exceeds limit",
        58: "BMS communication failure",
        59: "BMS secondary fault",
        60: "BMS alarm battery low temperature",
        61: "BMS alarm battery over temperature",
        62: "BMS alarm battery over current",
        63: "BMS alaram low battery",
    }
    return errors[code]
