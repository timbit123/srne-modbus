import os
import minimalmodbus
import traceback
import struct
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

modbus_address: int = (
    int(os.getenv("MODBUS_ADDRESS")) if os.getenv("MODBUS_ADDRESS") else 0
)
modbus_instrument = os.getenv("MODBUS_DEVICE")
print("using address %d on device %s"%(modbus_address,modbus_instrument))
instr = minimalmodbus.Instrument(modbus_instrument, modbus_address)
instr.serial.baudrate = 9600
instr.serial.timeout = 1
#instr.debug = True


def debug(msg):
    if os.getenv("DEBUG") == "true":
        print("[{}] {}".format(datetime.now(), msg))

############ Generic Register Functions #####################

def read_register_str(register:int, name:str, clean:bool = False, prefix:str = ""):
    try:
      result = instr.read_string(register, 20)
    except:
      return None
    if clean:
        result = "".join([char for char in result if char != "\x00"])
    result = prefix + result
    debug(name + ": " + result)
    return result

def read_register_value(register:int, name:str, unit:str = "", scale:float = 1.0, prefix:str = "", integer:bool = False, format_str:str ="{:.2f}"):
    try:
      result = instr.read_register(register)
    except:
      return None
    result = float(result) * scale
    if integer:
        format_str = "{:d}" if format_str == "{:.2f}" else format_str
        result = int(result)
    result = prefix + format_str.format(result)
    debug(name + ": " + result + unit)
    return result

#################### P01 DC Data Area ##################


############ Battery #####################
def read_battery_soc():
    try:
      result = instr.read_register(0x100)
    except:
      return None
    debug("Battery SOC: " + str(result) + "%")
    return result


def read_battery_voltage():
    try:
      result = instr.read_register(0x101)
    except:
      return None
    result = result / 10
    debug("Battery Voltage: " + str(result) + "V")
    return result


def read_battery_current():
    try:
      result = instr.read_register(0x102, signed=True)
    except:
      return None
    result = result / 10
    debug("Battery Current: " + str(result) + "A")
    return result


def read_battery_temperature():
    try:
      result = instr.read_register(0x103, signed=True)
    except:
      return None
    result = result / 10
    debug("Battery Temperature: " + str(result) + "°C")
    return result


############## PV #########################
def read_pv1_voltage():
    try:
      result = instr.read_register(0x107)
    except:
      return None
    result = result / 10
    debug("PV1 Voltage: " + str(result) + "V")
    return result


def read_pv1_current():
    try:
      result = instr.read_register(0x108)
    except:
      return None
    result = result / 10
    debug("PV1 Current: " + str(result) + "A")
    return result


def read_pv1_charge_power():
    try:
      result = instr.read_register(0x109)
    except:
      return None
    debug("PV1 Charge Power: " + str(result) + "W")
    return result


def read_pv_total_power():
    try:
      result = instr.read_register(0x10A)
    except:
      return None
    debug("PV Total Power: " + str(result) + "W")
    return result


def read_charging_state():
    key = 0
    try:
      key = int(instr.read_register(0x010B))
    except:
      return None
    charging_states = {
        0: "Not Charging",
        1: "Quick Charge",
        2: "Constant Voltage Charge",
        4: "Float Charge",
        6: "Battery Activation",
        8: "Fully Charged",
    }
    if key in charging_states:
            value = charging_states[key]
            debug("Charging State: " + value)
            return value

    debug(f"Unknown charging state: {key}")
    return "Unknown"


def read_charging_power():
    # PV charging power + AC charging power
    try:
      result = instr.read_register(0x10E)
    except:
      return None
    debug("Charging Power: " + str(result) + "W")
    return result


def read_pv2_voltage():
    try:
      result = instr.read_register(0x10F)
    except:
      return None
    result = result / 10
    debug("PV2 Voltage: " + str(result) + "V")
    return result


def read_pv2_current():
    try:
      result = instr.read_register(0x110)
    except:
      return None
    result = result / 10
    debug("PV2 Current: " + str(result) + "A")
    return result


def read_pv2_charge_power():
    try:
      result = instr.read_register(0x111)
    except:
      return None
    debug("PV2 Charge Power: " + str(result) + "W")
    return result


#################### P02 Inverter Data Area ##################


def read_system_date_time():
    try:
      results = instr.read_registers(0x20C, 3)
    except:
      return None
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
    try:
        instr.write_registers(0x20C, data)
    except:
        return None
    debug(f"System Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")


def read_grid_on_remain_time_state():
    try:
      result = instr.read_register(0x20F)
    except:
      return None
    debug("Grid On/Remain Time State:", result)
    return result


def read_machine_state():
    key = 5
    try:
      key = int(instr.read_register(0x210))
    except:
      return None
    machine_states = {
        0: "Initialization",
        1: "Standby state",
        2: "AC power operation",
        3: "Inverter operation",
    }

    if key in machine_states:
        value = machine_states[key]
        debug("Machine State: " + value)
        return value

    debug(f"Unknown machine state: {key}")
    return "Unknown"


def read_bus_voltage():
    try:
      result = instr.read_register(0x212)
    except:
      return None
    result = result / 10
    debug("Bus Voltage: " + str(result) + "V")
    return result


def read_grid_voltage_a():
    try:
      result = instr.read_register(0x213)
    except:
      return None
    result = result / 10
    debug("Grid Voltage A: " + str(result) + "V")
    return result


def read_grid_current_a():
    try:
      result = instr.read_register(0x214)
    except:
      return None
    result = result / 10
    debug("Grid Current A: " + str(result) + "A")
    return result


def read_grid_frequency():
    try:
      result = instr.read_register(0x215)
    except:
      return None
    result = result / 100
    debug("Grid Frequency: " + str(result) + "Hz")
    return result


def read_inverter_voltage_a():
    try:
      result = instr.read_register(0x216)
    except:
      return None
    result = result / 10
    debug("Inverter Voltage A: " + str(result) + "V")
    return result


def read_inverter_current_a():
    try:
      result = instr.read_register(0x217)
    except:
      return None
    result = result / 10
    debug("Inverter Current A: " + str(result) + "A")
    return result


def read_inverter_frequency():
    try:
      result = instr.read_register(0x218)
    except:
      return None
    result = result / 100
    debug("Inverter Frequency: " + str(result) + "Hz")
    return result


def read_load_current_a():
    try:
      result = instr.read_register(0x219)
    except:
      return None
    result = result / 10
    debug("Load Current A: " + str(result) + "A")
    return result


def read_load_active_power_a():
    try:
      result = instr.read_register(0x21B)
    except:
      return None
    result = result
    debug("Load Active Power A: " + str(result) + "W")
    return result


def read_load_apparent_power_a():
    try:
      result = instr.read_register(0x21C)
    except:
      return None
    result = result
    debug("Load Apparent Power VA: " + str(result) + "VA")
    return result


def read_grid_charging_current():
    try:
      result = instr.read_register(0x21E)
    except:
      return None
    result = result / 10
    debug("Grid Charging Current: " + str(result) + "A")
    return result


def read_load_ratio_a():
    try:
      result = instr.read_register(0x21F)
    except:
      return None
    debug("Load Ratio A: " + str(result) + "%")
    return result


def read_temperature_dc_dc():
    try:
      result = instr.read_register(0x220, signed=True)
    except:
      return None
    result = result / 10
    debug("Temperature DC-DC: " + str(result) + "C")
    return result


def read_temperature_dc_ac():
    try:
      result = instr.read_register(0x221, signed=True)
    except:
      return None
    result = result / 10
    debug("Temperature DC-AC: " + str(result) + "C")
    return result


def read_temperature_transformer():
    try:
      result = instr.read_register(0x222, signed=True)
    except:
      return None
    result = result / 10
    debug("Temperature Transformer: " + str(result) + "C")
    return result


def read_temperature_ambient():
    # Sensor not always available
    try:
      result = instr.read_register(0x223, signed=True)
    except:
      return None
    result = result / 10
    debug("Temperature Ambient: " + str(result) + "C")
    return result


def read_pv_charging_current():
    try:
      result = instr.read_register(0x224)
    except:
      return None
    result = result / 10
    debug("PV Charging Current: " + str(result) + "A")
    return result


def read_parallel_load_avg_current():
    try:
      result = instr.read_register(0x225)
    except:
      return None
    result = result / 10
    debug("Parallel Load Avg Current: " + str(result) + "A")
    return result


def read_pbus_voltage():
    try:
      result = instr.read_register(0x228)
    except:
      return None
    result = result / 10
    debug("PBus Voltage: " + str(result) + "V")
    return result


def read_nbus_voltage():
    try:
      result = instr.read_register(0x229)
    except:
      return None
    result = result / 10
    debug("NBus Voltage: " + str(result) + "V")
    return result


def read_grid_voltage_b():
    try:
      result = instr.read_register(0x22A)
    except:
      return None
    result = result / 10
    debug("Grid Voltage B: " + str(result) + "V")
    return result


def read_grid_voltage_c():
    try:
      result = instr.read_register(0x22B)
    except:
      return None
    result = result / 10
    debug("Grid Voltage C: " + str(result) + "V")
    return result


def read_inverter_voltage_b():
    try:
      result = instr.read_register(0x22C)
    except:
      return None
    result = result / 10
    debug("Inverter Voltage B: " + str(result) + "V")
    return result


def read_inverter_voltage_c():
    try:
      result = instr.read_register(0x22D)
    except:
      return None
    result = result / 10
    debug("Inverter Voltage C: " + str(result) + "V")
    return result


def read_inverter_current_b():
    try:
      result = instr.read_register(0x22E)
    except:
      return None
    result = result / 10
    debug("Inverter Current B: " + str(result) + "A")
    return result


def read_inverter_current_c():
    try:
      result = instr.read_register(0x22F)
    except:
      return None
    result = result / 10
    debug("Inverter Current C: " + str(result) + "A")
    return result


def read_load_current_b():
    try:
      result = instr.read_register(0x230)
    except:
      return None
    result = result / 10
    debug("Load Current B: " + str(result) + "A")
    return result


def read_load_current_c():
    try:
      result = instr.read_register(0x231)
    except:
      return None
    result = result / 10
    debug("Load Current C: " + str(result) + "A")
    return result


def read_load_active_power_b():
    try:
      result = instr.read_register(0x232)
    except:
      return None
    debug("Load Active Power B: " + str(result) + "W")
    return result


def read_load_active_power_c():
    try:
      result = instr.read_register(0x233)
    except:
      return None
    debug("Load Active Power C: " + str(result) + "W")
    return result


def read_load_apparent_power_b():
    try:
      result = instr.read_register(0x234)
    except:
      return None
    debug("Load Apparent Power B: " + str(result) + "VA")
    return result


def read_load_apparent_power_c():
    try:
      result = instr.read_register(0x235)
    except:
      return None
    debug("Load Apparent Power C: " + str(result) + "VA")
    return result


def read_load_ratio_b():
    try:
      result = instr.read_register(0x236)
    except:
      return None
    debug("Load Ratio B: " + str(result) + "%")
    return result


def read_load_ratio_c():
    try:
      result = instr.read_register(0x237)
    except:
      return None
    debug("Load Ratio C: " + str(result) + "%")
    return result


def read_grid_current_b():
    try:
      result = instr.read_register(0x238)
    except:
      return None
    result = result / 10
    debug("Grid Current B: " + str(result) + "A")
    return result


def read_grid_current_c():
    try:
      result = instr.read_register(0x239)
    except:
      return None
    result = result / 10
    debug("Grid Current C: " + str(result) + "A")
    return result


def read_grid_active_power_a():
    # keep consistent with battery power convention
    # positive value when inverter is consuming power from the grid
    # negative value when inverter is exporting power to the grid
    try:
      result = -instr.read_register(0x23A, signed=True)
    except:
      return None
    debug("Grid Active Power A: " + str(result) + "W")
    return result


def read_grid_active_power_b():
    # keep consistent with battery power convention
    # positive value when inverter is consuming power from the grid
    # negative value when inverter is exporting power to the grid
    try:
      result = -instr.read_register(0x23B, signed=True)
    except:
      return None
    debug("Grid Active Power B: " + str(result) + "W")
    return result


def read_grid_active_power_c():
    # keep consistent with battery power convention
    # positive value when inverter is consuming power from the grid
    # negative value when inverter is exporting power to the grid
    try:
      result = -instr.read_register(0x23C, signed=True)
    except:
      return None
    debug("Grid Active Power C: " + str(result) + "W")
    return result


def read_grid_apparent_power_a():
    try:
      result = instr.read_register(0x23D)
    except:
      return None
    debug("Grid Apparent Power A: " + str(result) + "VA")
    return result


def read_grid_apparent_power_b():
    try:
      result = instr.read_register(0x23E)
    except:
      return None
    debug("Grid Apparent Power B: " + str(result) + "VA")
    return result


def read_grid_apparent_power_c():
    try:
      result = instr.read_register(0x23F)
    except:
      return None
    debug("Grid Apparent Power C: " + str(result) + "VA")
    return result


def read_home_load_active_power_a():
    result = instr.read_register(0x240)
    debug("Home Load Active Power A: " + str(result) + "W")
    return result


def read_home_load_active_power_b():
    result = instr.read_register(0x241)
    debug("Home Load Active Power B: " + str(result) + "W")
    return result


def read_home_load_active_power_c():
    result = instr.read_register(0x242)
    debug("Home Load Active Power C: " + str(result) + "W")
    return result


#################### P03 Device Control Area ##################


def write_power_off_on(value):
    # 0: Off, 1: On
    try:
        instr.write_register(0xDF00, int(value))
    except:
        return None
    debug("Power " + ("Off" if value == 0 else "On"))
    return True


def write_reset(value):
    # 1: Reset
    try:
        instr.write_register(0xDF01, int(value))
    except:
        return None
    debug("Reset")
    return True


def write_restore_factory_setting(value):
    # 1: Restore Factory Setting
    # 2: Clear statistics
    # 3: Clear errors

    #This seems like a bad idea to enable
    #if value == "1":
    #    try:
    #        instr.write_register(0xDF02, 0xAA)
    #    except:
    #        return None
    #    debug("Restore Factory Setting")
    if value == "2":
        try:
            instr.write_register(0xDF02, 0xBB)
        except:
            return None
        debug("Clear statistics")
    elif value == "3":
        try:
            instr.write_register(0xDF02, 0xCC)
        except:
            return None
        debug("Clear errors")
    return True


def write_battery_equal_charging_immediately(value):
    try:
        instr.write_register(0xDF0D, int(value))
    except:
        return None
    debug("Battery Equal Charging Immediately: " + str(value))
    return True


#################### P05 Setting Area for Battery-related Parameters ##################
def read_pv_charging_current_limit():
    # documentation says max 150A but mine returned 200A...
    # TODO: check the documentation
    try:
      result = instr.read_register(0xE001)
    except:
      return None
    result = result / 10
    debug("Charging Current Limit: " + str(result) + "A")
    return result


def write_pv_charging_current_limit(value):
    try:
        instr.write_register(0xE001, int(float(value) * 10))
    except:
        return None
    debug("Charging Current Limit set to: " + str(value))
    return True


def read_battery_rate_voltage():
    # not sure why you would chnge this value though
    # most inverter cannot do all voltages 12v/24V/36v/48v
    # This data need to be pulled on start to configure other configuration
    try:
      result = instr.read_register(0xE003)
    except:
      return None
    debug("Battery Rate Voltage: " + str(result) + "V")
    return result


def read_battery_type_set():
    try:
      result = instr.read_register(0xE004)
    except:
      return None
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
    try:
        instr.write_register(0xE004, int(value))
    except:
        return None
    return True


## TODO: maybe at some point we want to init and pull this before anything else
battery_rate: float = read_battery_rate_voltage() / 12


def read_battery_overvoltage_protection_voltage():
    try:
      result = instr.read_register(0xE005)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Overcharge Protection Voltage: " + str(result) + "V")
    return result

def write_battery_overvoltage_protection_voltage(value: str):
    if len(value) == 0:
        return
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE005, value)
    except:
        return None
    return True


def read_battery_charge_limit_voltage():
    try:
      result = instr.read_register(0xE006)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Charge Limit Voltage: " + str(result) + "V")
    return result


def write_battery_charge_limit_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE006, value)
    except:
        return None
    return True


def read_battery_equalization_voltage():
    try:
      result = instr.read_register(0xE007)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Charge Equalization Voltage: " + str(result) + "V")
    return result


def write_battery_equalization_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE007, value)
    except:
        return None
    return True


def read_battery_bulk_voltage():
    try:
      result = instr.read_register(0xE008)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Bulk Voltage: " + str(result) + "V")
    return result


def write_battery_bulk_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE008, value)
    except:
        return None
    return True


def read_battery_float_charge_voltage():
    try:
      result = instr.read_register(0xE009)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Float Charge Voltage: " + str(result) + "V")
    return result


def write_battery_float_charge_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE009, value)
    except:
        return None
    return True


def read_battery_rebulk_voltage():
    try:
      result = instr.read_register(0xE00A)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery ReBulk Voltage: " + str(result) + "V")
    return result


def write_battery_rebulk_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE00A, value)
    except:
        return None
    return True


def read_battery_overdischarge_return_voltage():
    try:
      result = instr.read_register(0xE00B)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Overdischarge Return Voltage: " + str(result) + "V")
    return result


def write_battery_overdischarge_return_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE00B, value)
    except:
        return None
    return True


def read_battery_undervoltage_warning():
    try:
      result = instr.read_register(0xE00C)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Undervoltage Warning Voltage: " + str(result) + "V")
    return result


def write_battery_undervoltage_warning(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE00C, value)
    except:
        return None
    return True


def read_battery_overdischarge_limit():
    try:
      result = instr.read_register(0xE00D)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Overdischarge Warning Voltage: " + str(result) + "V")
    return result


def write_battery_overdischarge_limit(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE00D, value)
    except:
        return None
    return True


def read_battery_discharge_limit_voltage():
    try:
      result = instr.read_register(0xE00E)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Discharge Limit Voltage: " + str(result) + "V")
    return result


def write_battery_discharge_limit_voltage(value: str):
    if len(value) == 0:
        return None
    value = int(float(value) / battery_rate * 10)
    try:
        instr.write_register(0xE00E, value)
    except:
        return None
    return True


def read_battery_stop_state_of_charge():
    try:
      result = instr.read_register(0xE00F)
    except:
      return None
    debug("Battery Stop State of Charge Voltage: " + str(result) + "%")
    return result


def write_battery_stop_state_of_charge(value: str):
    if len(value) == 0:
        return None
    try:
        instr.write_register(0xE00F, int(value))
    except:
        return None
    return True


def read_battery_overdischarge_delay_time():
    try:
      result = instr.read_register(0xE010)
    except:
      return None
    debug("Battery Overdischarge Delay Time: " + str(result) + "s")
    return result


def write_battery_overdischarge_delay_time(value: str):
    if len(value) == 0:
        return None
    try:
        instr.write_register(0xE010, int(value))
    except:
        return None
    return True


def read_battery_equalization_charge_delay_time():
    try:
      result = instr.read_register(0xE011)
    except:
      return None
    debug("Battery Equalization Charge Delay Time: " + str(result) + "min")
    return result


def write_battery_equalization_charge_delay_time(value: str):
    if len(value) == 0:
        return None
    try:
        instr.write_register(0xE011, int(value))
    except:
        return None
    return True


def read_battery_bulk_charge_time():
    try:
      result = instr.read_register(0xE012)
    except:
      return None
    debug("Battery Bulk Charge Time: " + str(result) + "min")
    return result


def write_battery_bulk_charge_time(value: str):
    if len(value) == 0:
        return None
    try:
        instr.write_register(0xE012, int(value))
    except:
        return None
    return True


def read_battery_equalization_charge_interval():
    try:
      result = instr.read_register(0xE013)
    except:
      return None
    debug("Battery Equalization Charge Interval: " + str(result) + "days")
    return result


def write_battery_equalization_charge_interval(value: str):
    try:
        instr.write_register(0xE013, int(value))
    except:
        return None
    return True


def read_battery_dc_switch_low_voltage():
    try:
      result = instr.read_register(0xE01B)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Switch Load to AC when low voltage: " + str(result) + "V")
    return result


def write_battery_dc_switch_low_voltage(value: str):
    value = float(value) / battery_rate * 10
    try:
        instr.write_register(0xE01B, int(value))
    except:
        return None
    return True


def read_stop_charging_current_limit():
    """
    Only the lithium battery is effective, and when the current of constant-voltage charging state is lower than this value, the charging is stopped.
    """
    try:
      result = instr.read_register(0xE01C)
    except:
      return None
    result = result / 10
    debug("Stop charging when current below: " + str(result) + "A")
    return result


def write_stop_charging_current_limit(value: str):
    value = float(value) * 10
    try:
        instr.write_register(0xE01C, int(value))
    except:
        return None
    return True


def read_stop_charging_soc_set():
    """
    When the SOC capacity is greater than or equal to this value, charging is stopped, and it is valid for BMS communication.
    """
    try:
      result = instr.read_register(0xE01D)
    except:
      return None
    debug("Stop Charging SOC Set: " + str(result) + "%")
    return result


def write_stop_charging_soc_set(value: str):
    try:
        instr.write_register(0xE01D, int(value))
    except:
        return None
    return True


def read_battery_soc_low_alarm():
    try:
      result = instr.read_register(0xE01E)
    except:
      return None
    debug("Battery SOC Low Alarm: " + str(result) + "%")
    return result


def write_battery_soc_low_alarm(value: str):
    try: 
        instr.write_register(0xE01E, int(value))
    except:
        return None
    return True


def read_battery_soc_switch_to_line():
    try:
      result = instr.read_register(0xE01F)
    except:
      return None
    debug("Battery SOC Switch load to AC when below: " + str(result) + "%")
    return result


def write_battery_soc_switch_to_line(value: str):
    try:
        instr.write_register(0xE01F, int(value))
    except:
        return None
    return True


def read_battery_soc_switch_to_battery():
    try:
      result = instr.read_register(0xE020)
    except:
      return None
    debug("Battery SOC Switch back to Battery: " + str(result) + "%")
    return result


def write_battery_soc_switch_to_battery(value: str):
    try: 
        instr.write_register(0xE020, int(value))
    except:
        return None
    return True


def read_battery_voltage_switch_to_inverter():
    """
    When the battery voltage is higher than the judged point, the inverter is switched back.
    """
    try:
      result = instr.read_register(0xE022)
    except:
      return None
    result = (result / 10) * battery_rate
    debug("Battery Voltage Switch to Inverter: " + str(result) + "V")
    return result


def write_battery_voltage_switch_to_inverter(value: str):
    value = float(value) / battery_rate * 10
    try:
        instr.write_register(0xE022, int(value))
    except:
        return None
    return True


def read_battery_equalization_charge_timeout():
    try:
      result = instr.read_register(0xE023)
    except:
      return None
    debug("Battery Equalization Charge Timeout: " + str(result) + "min")
    return result


def write_battery_equalization_charge_timeout(value: str):
    """
    steps = 5
    """
    try:
        instr.write_register(0xE023, int(value))
    except:
        return None
    return True


def read_lithium_battery_active_current_set():
    try:
      result = instr.read_register(0xE024)
    except:
      return None
    result = result / 10
    debug("Lithium Battery Active Current Set: " + str(result) + "A")
    return result


def write_lithium_battery_active_current_set(value: str):
    value = float(value) * 10
    try:
        instr.write_register(0xE024, int(value))
    except:
        return None
    return True


def read_bms_charging_limit_current_mode_setting():
    try:
      result = instr.read_register(0xE025)
    except:
      return None
    setting = {
        0: "HMI Setting",
        1: "BMS Protocol",
        2: "Inverter Logic",
    }
    if result in setting: 
        debug("BMS Charging Limit Current Mode: " + setting[result])
        return setting[result]
    return result


def write_bms_charging_limit_current_mode_setting(value):
    setting = {
            "HMI Setting" : 0,
            "BMS Protocol": 1,
            "Inverter Logic":2,
    }
    if value in setting:
        int_value = setting[value]
        try:
            instr.write_register(0xE025, int_value)
        except:
            return None
    else:
        return None
    return True

def read_bms_protocol():
    try:
      result = instr.read_register(0xE21B)
    except:
      return None
    setting = {
        0: "PACE",
        1: "RUDA",
        2: "AOGUAN",
        3: "OULITE",
        4: "CEF",
        5: "XINWANGDA",
        6: "DAQIN",
        7: "WOW",
        8: "PYL",
        9: "MIT",
        10: "XIX",
        11: "POL",
        12: "GUOX",
        13: "SMK",
        14: "VOL",
        15: "WES",
        17: "UZE_CAN",
        18: "PYL_CAN",
        100: "SGP",
        101: "GSL",
        102: "PYL2",
    }
    if result in setting: 
        debug("BMS Protocol: " + setting[result])
        return setting[result]
    return result


def write_bms_protocol(value):
    setting = {
        "PACE": 0,
        "RUDA": 1,
        "AOGUAN": 2,
        "OULITE": 3,
        "CEF": 4,
        "XINWANGDA": 5,
        "DAQIN": 6,
        "WOW": 7,
        "PYL": 8,
        "MIT": 9,
        "XIX": 10,
        "POL": 11,
        "GUOX": 12,
        "SMK": 13,
        "VOL": 14,
        "WES": 15,
        "UZE_CAN": 17,
        "PYL_CAN": 18,
        "SGP": 100,
        "GSL": 101,
        "PYL2": 102,
    }
    if value in setting:
        int_value = setting[value]
        try:
            instr.write_register(0xE21B, int_value)
        except:
            return None
    else:
        return None
    return True

def read_charge_start_time_1():
    # Hours and minutes: 23h*256+59min=5,947
    try:
      result = instr.read_register(0xE026)
    except:
      return None
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
    try:
        instr.write_register(0xE026, combined)
    except:
        return None
    debug("Charge Start Time 1 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_charge_end_time_1():
    try:
      result = instr.read_register(0xE027)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_1(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE027, combined)
    except:
        return None
    debug("Charge End Time 1 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_charge_start_time_2():
    try:
      result = instr.read_register(0xE028)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge Start Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_start_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE028, combined)
    except:
        return None
    debug("Charge Start Time 2 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_charge_end_time_2():
    try:
      result = instr.read_register(0xE029)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE029, combined)
    except:
        return None
    debug("Charge End Time 2 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_charge_start_time_3():
    try:
      result = instr.read_register(0xE02A)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge Start Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_start_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE02A, combined)
    except:
        return None
    debug("Charge Start Time 3 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_charge_end_time_3():
    try:
      result = instr.read_register(0xE02B)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Charge End Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_charge_end_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE02B, combined)
    except:
        return None
    debug("Charge End Time 3 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_time_charge_enabled():
    # 0:Disabled, 1:Enabled
    try:
      result = instr.read_register(0xE02C)
    except:
      return None
    enabled = "Enabled" if int(result) else "Disabled"
    debug("Charge Time Enabled: " + enabled)
    return enabled

def write_time_charge_enabled(value: str):
    priority = {
        "Disabled": 0,
        "Enabled": 1,
    }
    if value in priority:
        int_value = priority[value]
        try:
            instr.write_register(0xE02C, int_value)
        except:
            return None
    else:
        return None
    return True

def read_discharge_start_time_1():
    # Hours and minutes: 23h*256+59min=5,947
    try:
      result = instr.read_register(0xE02D)
    except:
      return None
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
    try:
        instr.write_register(0xE02D, combined)
    except:
        return None
    debug("Discharge Start Time 1 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_discharge_end_time_1():
    try:
      result = instr.read_register(0xE02E)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 1: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_1(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE02E, combined)
    except:
        return None
    debug("Discharge End Time 1 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_discharge_start_time_2():
    try:
      result = instr.read_register(0xE02F)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge Start Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_start_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE02F, combined)
    except:
        return None
    debug("Discharge Start Time 2 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_discharge_end_time_2():
    try:
      result = instr.read_register(0xE030)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 2: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_2(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE030, combined)
    except:
        return None
    debug("Discharge End Time 2 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_discharge_start_time_3():
    try:
      result = instr.read_register(0xE031)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge Start Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_start_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE031, combined)
    except:
        return None
    debug("Discharge Start Time 3 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_discharge_end_time_3():
    try:
      result = instr.read_register(0xE032)
    except:
      return None
    hours = (result & 0xFF00) >> 8
    minutes = result & 0x00FF
    debug("Discharge End Time 3: " + str(hours) + "h" + str(minutes) + "min")
    return f"{hours}:{minutes}"


def write_discharge_end_time_3(value: str):
    hours, minutes = map(int, value.split(":"))
    combined = (hours << 8) | minutes
    try:
        instr.write_register(0xE032, combined)
    except:
        return None
    debug("Discharge End Time 3 set to " + str(hours) + "h" + str(minutes) + "min")
    return True


def read_time_discharge_enabled():
    # 0:Disabled, 1:Enabled
    try:
      result = instr.read_register(0xE033)
    except:
      return None
    debug("Charge Time Enabled: " + str(result))
    return result


def read_pv_power_priority_set():
    try:
      result = instr.read_register(0xE039)
    except:
      return None
    priority_mode = {0: "Load Priority", 1: "Charging Priority", 2: "Grid Priority"}
    if result in priority_mode: 
        debug("PV Priority Mode: " + priority_mode[result])
        return priority_mode[result]
    return result


def write_pv_power_priority_set(value: str):
    priority_mode = {"Load Priority" : 0, "Charging Priority" : 1, "Grid Priority" : 2}
    if value in priority_mode:
        int_value = priority_mode[value]
        try:
            instr.write_register(0xE039, int_value)
        except:
            return None
    else:
        return None
    return True


#################### P07 User Setting Area for Inverter Parameters ##################
def read_rs485_address_set():
    try:
      result = instr.read_register(0xE200)
    except:
      return None
    debug(f"RS-485 Address Set: {result}")
    return result


def read_parallel_mode():
    try:
      result = instr.read_register(0xE201)
    except:
      return None
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
    try:
        instr.write_register(0xE201, int(value))
    except:
        return None
    return True

#This setting doesn't seem to do anything on HESP48120U200-H
def read_output_priority():
    try:
      result = instr.read_register(0xE204)
    except:
      return None
    output_priority = {0: "Solar First", 1: "Utility First", 2: "Solar/Battery/Utility"}
    if result in output_priority:
        debug("Output Priority: " + output_priority[result])
        return output_priority[result]

    return result


def write_output_priority(value: str):
    output_priority = {"Solar First": 0, "Utility First": 1, "Solar/Battery/Utility": 2}
    if value in output_priority:
        int_value = output_priority[value]
        try:
            instr.write_register(0xE204, int_value)
        except Exception:
            print(traceback.format_exc())
            pass
    else:
        return None
    return True

def read_hybrid_mode():
    try:
      result = instr.read_register(0xE037)
    except:
      return None
    hybrid_mode = {1: "On Grid", 2: "Limit Power to UPS", 3: "Limit Power to Home"}
    if result in hybrid_mode: 
        debug("Hyrbid Mode: " + hybrid_mode[result])
        return hybrid_mode[result]

    return result


def write_hybrid_mode(value: str):
    hybrid_mode = {"On Grid" : 1, "Limit Power to UPS" : 2, "Limit Power to Home" : 3}
    if value in hybrid_mode:
        int_value = hybrid_mode[value]
        try:
            instr.write_register(0xE037, int_value)
        except:
            return None
    else:
        return None
    return True

def read_grid_charging_current_limit():
    try:
      result = instr.read_register(0xE005)
    except:
      return None
    result = result / 10
    debug("Grid Charging Current Limit: " + str(result) + "A")
    return result


def write_grid_charging_current_limit(value: str):
    value = float(value) * 10
    try:
        instr.write_register(0xE005, int(value))
    except:
        return None
    return True


def read_battery_equalization_charging_enable():
    try:
      result = instr.read_register(0xE206)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Battery Equal Charging Enable: " + enable[result])
    return result


def write_battery_equalization_charging_enable(value: str):
    try:
        instr.write_register(0xE206, int(value))
    except:
        return None
    return True


def read_output_voltage_set():
    try:
      result = instr.read_register(0xE208)
    except:
      return None
    result = result / 10
    debug("Output Voltage Set: " + str(result) + "V")
    return result


def read_output_frequency_set():
    try:
      result = instr.read_register(0xE209)
    except:
      return None
    result = result / 100
    debug("Output Frequency Set: " + str(result) + "Hz")
    return result


def read_total_charging_current_limit():
    try:
      result = instr.read_register(0xE20A)
    except:
      return None
    result = result / 10
    debug("Total Charging Current Limit: " + str(result) + "A")
    return result


def write_total_charging_current_limit(value: str):
    value = float(value) * 10
    try:
        instr.write_register(0xE20A, int(value))
    except:
        return None
    return True


def read_ac_voltage_range():
    try:
      result = instr.read_register(0xE20B)
    except:
      return None
    range = {
        0: "Wide band (APL)",
        1: "Narrow band (UPS)",
    }
    debug("AC Voltage Range: " + range[result])
    return result


def write_ac_voltage_range(value: str):
    value = int(value)
    try:
        instr.write_register(0xE20B, value)
    except:
        return None
    return True


def read_power_saving_mode():
    try:
      result = instr.read_register(0xE20C)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Power Saving Mode: " + enable[result])
    return result


def write_power_saving_mode(value: str):
    print("power saving: " + value)
    try:
        instr.write_register(0xE20C, int(value))
    except:
        return None
    return True


def read_auto_restart_on_overload():
    try:
      result = instr.read_register(0xE20D)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Auto Restart On Overload: " + enable[result])
    return result


def write_auto_restart_on_overload(value: str):
    try:
        instr.write_register(0xE20D, int(value))
    except:
        return None
    return True


def read_auto_restart_on_overheat():
    try:
      result = instr.read_register(0xE20E)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Auto Restart On Overheat: " + enable[result])
    return result


def write_auto_restart_on_overheat(value: str):
    try:
        instr.write_register(0xE20E, int(value))
    except:
        return None
    return True


def read_charging_source_priority():
    try:
      result = instr.read_register(0xE20F)
    except:
      return None
    priority = {
        0: "Solar First",  # (AC power charging available when PV fails)",
        1: "Utility First",  # (PV charging available when AC fails)",
        2: "Solar and Utility Simultaneously",  # (AC power and PV charging at the same time, with PV priority)",
        3: "Solar Only",
    }
    if result in priority:
        debug("Charging Source Priority: " + priority[result])
        return priority[result]
    return result


def write_charging_source_priority(value: str):
    priority = {
        "Solar First": 0,  # (AC power charging available when PV fails)",
        "Utility First": 1,  # (PV charging available when AC fails)",
        "Solar and Utility Simultaneously": 2,  # (AC power and PV charging at the same time, with PV priority)",
        "Solar Only": 3,
    }
    if value in priority:
        int_value = priority[value]
        try:
            instr.write_register(0xE20F, int_value)
        except:
            return None
    else:
        return None
    return True


def read_alarm_enabled():
    try:
      result = instr.read_register(0xE210)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Alarm Enabled: " + enable[result])
    return result


def write_alarm_enabled(value: str):
    try:
        instr.write_register(0xE210, int(value))
    except:
        return None
    return True


def read_alarm_enabled_on_input_loss():
    try:
      result = instr.read_register(0xE211)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Alarm Enabled On Input Loss: " + enable[result])
    return result


def write_alarm_enabled_on_input_loss(value: str):
    try:
        instr.write_register(0xE211, int(value))
    except:
        return None
    return True


def read_bypass_on_overload():
    try:
      result = instr.read_register(0xE212)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Bypass On Overload: " + enable[result])
    return result


def write_bypass_on_overload(value: str):
    try:
        instr.write_register(0xE212, int(value))
    except:
        return None
    return True


def read_stop_on_bms_error_enabled():
    try:
      result = instr.read_register(0xE214)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("Stop On BMS Error Enabled: " + enable[result])
    return result


def write_stop_on_bms_error_enabled(value: str):
    try:
        instr.write_register(0xE214, int(value))
    except:
        return None
    return True


def read_bms_communication_enabled():
    try:
      result = instr.read_register(0xE215)
    except:
      return None
    enable = {
        0: "Disable",
        1: "RS485",
        2: "CAN",
    }
    if result in enable: 
        debug("BMS Communicaton: " + enable[result])
        return enable[result]
    return result

def write_bms_communication_enabled(value: str):
    enable = {
            "Disable" : 0, 
            "RS485" : 1, 
            "CAN" : 2
    }
    if value in enable:
        int_value = enable[value]
        try:
            instr.write_register(0xE215, int_value)
        except:
            return None
    else:
        return None
    return True

def read_dc_load_switch():
    try:
      result = instr.read_register(0xE216)
    except:
      return None
    enable = {0: "Disable", 1: "Enable"}
    debug("DC Load Switch: " + enable[result])
    return result


def write_dc_load_switch(value: str):
    value = int(value)
    try:
        instr.write_register(0xE216, value)
    except:
        return None
    return True


#################### P08 Setting Area for Inverter Grid-connection Parameters ###############


def read_battery_discharge_enabled():
    try:
      result = instr.read_register(0xE42A)
    except:
      return None
    priority = {
        0: "Standby",
        1: "Battery Discharge For Load",  # (PV charging available when AC fails)",
        2: "Battery Discharge For Home",  # (AC power and PV charging at the same time, with PV priority)",
        3: "Battery Discharge For Grid",
    }
    if result in priority:
        debug("Battery Discharge Enabled: " + priority[result])
        return priority[result]
    return result


def write_battery_discharge_enabled(value: str):
    priority = {
        "Standby": 0,  # (AC power charging available when PV fails)",
        "Battery Discharge For Load": 1,  # (PV charging available when AC fails)",
        "Battery Discharge For Home": 2,  # (AC power and PV charging at the same time, with PV priority)",
        "Battery Discharge For Grid": 3,
    }
    if value in priority:
        int_value = priority[value]
        try:
            instr.write_register(0xE42A, int_value)
        except:
            return None
    else:
        return None
    return True


#################### P09 Power Statistics Historical Data ##################
def read_total_pv_energy_last_7_days():
    # extract data from the last 7 days
    try:
      result = instr.read_registers(0xF000, 7)
    except:
      return None
    for i in range(len(result)):
        result[i] = result[i] / 10
    print("Total PV Energy Last 7 days: " + "kWh, ".join(map(str, result)) + "kWh")
    return result


def read_total_battery_charge_energy_last_7_days():
    try:
      result = instr.read_registers(0xF007, 7)
    except:
      return None
    print("Total Battery Charged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah")
    return result


def read_total_battery_discharge_energy_last_7_days():
    try:
      result = instr.read_registers(0xF00E, 7)
    except:
      return None
    print(
        "Total Battery Discharged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah"
    )
    return result


def read_total_line_charge_energy_last_7_days():
    try:
      result = instr.read_registers(0xF015, 7)
    except:
      return None
    print("Total Line Charged Last 7 days: " + "Ah, ".join(map(str, result)) + "Ah")
    return result


def read_total_load_consume_last_7_days():
    try:
      result = instr.read_registers(0xF01C, 7)
    except:
      return None
    for i in range(len(result)):
        result[i] = result[i] / 10
    print("Total Load Consume Last 7 days: " + "kWh, ".join(map(str, result)) + "kWh")
    return result


def read_total_load_consume_from_line_last_7_days():
    try:
      result = instr.read_registers(0xF023, 7)
    except:
      return None
    for i in range(len(result)):
        result[i] = result[i] / 10
    print(
        "Total Load Consume From Line Last 7 days: "
        + "kWh, ".join(map(str, result))
        + "kWh"
    )
    return result


def read_total_last_day_energy_statistics():

    try:
      result = instr.read_long(0xF02A, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    result = result / 10
    debug("Total Last Day Energy Statistics: " + str(result) + "kWh")
    return result


def read_total_generated_energy_to_grid_today():
    try:
      result = instr.read_register(0xF02C)
    except:
      return None
    result = result / 10
    debug("Total Generated Energy to Grid Today: " + str(result) + "kWh")
    return result


def read_total_battery_charged_today():
    try:
      result = instr.read_register(0xF02D)
    except:
      return None
    debug("Total Battery Charged Today: " + str(result) + "Ah")
    return result


def read_total_battery_discharged_today():
    try:
      result = instr.read_register(0xF02E)
    except:
      return None
    debug("Total Battery Discharged Today: " + str(result) + "Ah")
    return result


def read_total_pv_power_generated_today():
    try:
      result = instr.read_register(0xF02F)
    except:
      return None
    result = result / 10
    debug("Total PV Power Generated Today: " + str(result) + "kWh")
    return result


def read_total_load_consumed_today():
    try:
      result = instr.read_register(0xF030)
    except:
      return None
    result = result / 10
    debug("Total Load Consumed Today: " + str(result) + "kWh")
    return result


def read_total_operating_days():
    try:
      result = instr.read_register(0xF031)
    except:
      return None
    result = result / 10
    debug("Total Operating Days: " + str(result) + "days")
    return result


def read_total_grid_energy_total():
    try:
      result = instr.read_long(0xF032, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    debug(result)

    result = result / 10
    debug("Total Grid Energy: " + str(result) + "kWh")
    return result


def read_total_battery_charging_total():
    try:
      result = instr.read_long(0xF034, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    result = result
    debug("Total Battery Charging: " + str(result) + "Ah")
    return result


def read_total_battery_discharging_total():

    try:
      result = instr.read_long(0xF036, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
      result = result / 10
    except:
      return None
    result = result
    debug("Total Battery Discharging: " + str(result) + "Ah")
    return result


def read_total_pv_generated_energy_total():

    try:
      # Read two registers (4 bytes) starting at F038
      result = instr.read_long(0xF038, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    result = result / 10
    debug(f"Total PV Generated Energy: {result} kWh")
    return result


def read_total_load_consumption_total():
    try:
      result = instr.read_long(0xF03A, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    result = result / 10
    debug("Total Load consumption Energy: " + str(result) + "kWh")
    return result


def read_total_grid_charged_today():
    try:
      result = instr.read_register(0xF03C)
    except:
      return None
    debug("Total Grid Charged Today: " + str(result) + "Ah")
    return result


def read_total_grid_consumed_today():
    try:
      result = instr.read_register(0xF03D)
    except:
      return None
    result = result / 10
    debug("Total Load Consumed Today: " + str(result) + "kWh")
    return result


def read_total_inverter_worktime_today():
    try:
      result = instr.read_register(0xF03E)
    except:
      return None
    debug("Total Inverter Worktime Today: " + str(result) + "min")
    return result


def read_total_line_worktime_today():
    try:
      result = instr.read_register(0xF03F)
    except:
      return None
    debug("Total Line Worktime Today: " + str(result) + "min")
    return result


def read_total_power_on_time():
    try:
      results = instr.read_registers(0xF040, 3)
    except:
      return None

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


def read_total_last_equalization_charge_time():
    try:
      results = instr.read_registers(0xF043, 3)
    except:
      return None

    year = (results[0] >> 8) & 0xFF  # high byte
    month = results[0] & 0xFF  # Low byte
    day = (results[1] >> 8) & 0xFF  # high byte
    hour = results[1] & 0xFF  # Low byte
    minute = (results[2] >> 8) & 0xFF  # high byte
    second = results[2] & 0xFF  # Low byte

    debug(
        f"Last equalization charge time: 20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    )
    return f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


def read_total_grid_charged_total():
    try:
      result = instr.read_long(0xF046, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    debug("Total Grid Charged Total: " + str(result) + "Ah")
    return result


def read_total_grid_consumed_total():
    try:
      result = instr.read_long(0xF048, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
      return None
    result = result / 10
    debug("Total Load Consumed Total: " + str(result) + "kWh")
    return result


def read_total_inverter_work_time_total():
    try:
      result = instr.read_register(0xF04A)
    except:
      return None
    debug("Total Inverter Work Time Total: " + str(result) + "h")
    return result


def read_total_grid_work_time_total():
    try:
      result = instr.read_register(0xF04B)
    except:
      return None
    debug("Total Grid Work Time Total: " + str(result) + "h")
    return result


def read_total_grid_chrging_power_today():
    try:
      result = instr.read_register(0xF04C)
    except:
      return None
    result = result / 10
    debug("Total Load Consumed Total: " + str(result) + "kWh")
    return result


############# P10 Fault Record ########################
def read_errors():
    for i in range(32):
        try:
          results = instr.read_registers(0xF800 + (0x10 * i), 16)
        except:
          return None

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

def read_failcode(register:int, name:str):
    try:
      result = instr.read_register(register)
    except:
      return None

    error_code = result
    description = __error_lists(error_code)
    if error_code != 0: 
        print("Detected error in %s: Code %d: \"%s\""%(name,error_code,description))
    return description

def __error_lists(code: int):
    errors = {
        0: "No reported error",
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
        49: "Grid over voltage",
        50: "Grid under voltage",
        51: "Grid over frequency",
        52: "Grid under frequency",
        53: "Grid loss",
        54: "Grid DC current over",
        55: "Grid standard un init",
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
