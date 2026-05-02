import os
import math
import minimalmodbus
from datetime import datetime
from dotenv import load_dotenv
import pytz

load_dotenv()

modbus_address: int = (
    int(os.getenv("MODBUS_ADDRESS")) if os.getenv("MODBUS_ADDRESS") else 0
)
modbus_instrument = os.getenv("MODBUS_DEVICE")
print("using address %d on device %s" % (modbus_address, modbus_instrument))
instr = minimalmodbus.Instrument(modbus_instrument, modbus_address)
instr.serial.baudrate = 9600
instr.serial.timeout = float(os.getenv("MODBUS_TIMEOUT", "0.1"))
# instr.debug = True

_modbus_failures = 0
_MODBUS_FAILURE_THRESHOLD = 20


def _record_modbus_result(success: bool):
    global _modbus_failures
    if success:
        _modbus_failures = 0
    else:
        _modbus_failures += 1


def check_reconnect():
    """Reopen the serial port if too many consecutive modbus failures (e.g. USB disconnect)."""
    global instr, _modbus_failures
    if _modbus_failures < _MODBUS_FAILURE_THRESHOLD:
        return
    print(f"Modbus: {_modbus_failures} consecutive failures — attempting to reopen serial port")
    try:
        instr.serial.close()
    except Exception:
        pass
    try:
        instr = minimalmodbus.Instrument(modbus_instrument, modbus_address)
        instr.serial.baudrate = 9600
        instr.serial.timeout = float(os.getenv("MODBUS_TIMEOUT", "0.1"))
        _modbus_failures = 0
        print("Modbus serial port reopened successfully")
    except Exception as e:
        print(f"Modbus reconnect failed: {e}")
        _modbus_failures = _MODBUS_FAILURE_THRESHOLD  # keep trying each loop


def debug(msg):
    if os.getenv("DEBUG") == "true":
        print("[{}] {}".format(datetime.now(), msg))


def write_restore_factory_setting(value):
    # Register 0xDF02  CmdRestoreFactorySetting
    # 1: Restore Factory Setting
    # 2: Clear statistics
    # 3: Clear errors

    # This seems like a bad idea to enable
    # if value == "1":
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
    else:
        return None
    return True


def read_battery_rate_voltage():
    # Register 0xE003  BatRateVolt
    # not sure why you would chnge this value though
    # most inverter cannot do all voltages 12v/24V/36v/48v
    # This data need to be pulled on start to configure other configuration
    try:
        result = instr.read_register(0xE003)
    except:
        return None
    debug(f"Battery Rate Voltage: {result}V")
    return result


_batt_rate_voltage = read_battery_rate_voltage()
if _batt_rate_voltage is None:
    print("WARNING: could not read battery rate voltage; defaulting to 48 V")
    _batt_rate_voltage = 48
battery_rate: float = _batt_rate_voltage / 12


def read_errors():
    # Register 0xF800  FaultHistoryRecord00
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




############ Generic Register Functions #####################


def _format_scaled(result: float, scale: float) -> str:
    """Format a scaled register value: integer string for scale=1, decimal otherwise."""
    if scale == 1.0:
        return str(int(result))
    decimals = max(0, round(-math.log10(scale))) if scale != 0.0 else 0
    return f"{result:.{decimals}f}"


def read_register_str(register: int, name: str = "", clean: bool = False, prefix: str = ""):
    try:
        result = instr.read_string(register, 20)
    except:
        return None
    if clean:
        result = "".join([char for char in result if char != "\x00"])
    result = prefix + result
    if name:
        debug(f"{name}: {result}")
    return result


def read_register_value(
    register: int,
    name: str = "",
    unit: str = "",
    scale: float = 1.0,
    prefix: str = "",
    integer: bool = False,
    signed: bool = False,
    format_str: str = "",
):
    """Generic single-register read.  format_str is auto-derived from scale when empty."""
    try:
        result = instr.read_register(register, signed=signed)
    except:
        _record_modbus_result(False)
        return None
    _record_modbus_result(True)
    result = float(result) * scale
    if format_str:
        if integer:
            result = int(result)
        value = prefix + format_str.format(result)
    elif integer:
        value = prefix + str(int(result))
    else:
        value = prefix + _format_scaled(result, scale)
    if name:
        debug(f"{name}: {value}{unit}")
    return value


#################### P01 DC Data Area ##################


############ Battery #####################


def read_clamped_register(register: int, scale: float = 1.0, name: str = "") -> str | None:
    """Read a signed register and clamp to zero if negative.
    Used for load current/power registers that can transiently read negative."""
    try:
        result = max(0, instr.read_register(register, signed=True))
    except:
        _record_modbus_result(False)
        return None
    _record_modbus_result(True)
    result = float(result) * scale
    value = _format_scaled(result, scale)
    if name:
        debug(f"{name}: {value}")
    return value


def write_register_value(register: int, value: str, scale: float = 1.0) -> bool | None:
    """Generic single-register write.  value is the human-readable string from MQTT.
    The raw register value written is int(round(float(value) / scale))."""
    if not value and value != 0:
        return None
    try:
        raw = int(round(float(value) / scale))
        instr.write_register(register, raw)
    except:
        return None
    return True


def read_battery_voltage_register(register: int, name: str = "") -> str | None:
    """Read a battery voltage register. Raw register value = actual_volts * 10 / battery_rate.
    Returns the actual voltage as a formatted string."""
    return read_register_value(register, name=name, scale=battery_rate / 10)


def write_battery_voltage_register(register: int, value: str) -> bool | None:
    """Write a battery voltage register. Raw register value = actual_volts * 10 / battery_rate.
    Accepts the actual voltage as a human-readable string."""
    return write_register_value(register, value, scale=battery_rate / 10)


############ Parallel Inverter Power Sums (P02 0x024E-0x0254) #####################


def read_parallel_load_active_power_sum() -> int | None:
    # Register 0x024E  ParaUpsLoadPowersum – sum of UPS/load active power across all parallel units
    try:
        return instr.read_register(0x024E, signed=True)
    except:
        return None


def read_parallel_home_active_power_sum() -> int | None:
    # Register 0x0250  ParaHomeLoadPowerSum – sum of home-load active power across all parallel units
    try:
        return instr.read_register(0x0250)
    except:
        return None


def read_parallel_grid_active_power_sum() -> int | None:
    # Register 0x0252  ParaGridPowerSum – positive = consuming from grid, negative = exporting
    try:
        return -instr.read_register(0x0252, signed=True)
    except:
        return None


############ Lookup Table Constants #####################

CHARGING_STATES: dict = {0: "Not Charging", 1: "Quick Charge", 2: "Constant Voltage Charge", 4: "Float Charge", 6: "Battery Activation", 8: "Fully Charged"}
MACHINE_STATES: dict = {0: "Initialization", 1: "Standby state", 2: "AC power operation", 3: "Inverter operation"}
BATTERY_TYPES: dict = {0: "User defined", 1: "SLD", 2: "FLD", 3: "GEL", 4: "LFP 14 cells", 5: "LFP 15 cells", 6: "LFP 16 cells", 7: "LFP 7 cells", 8: "LFP 8 cells", 9: "LFP 9 cells", 10: "Ternary lithium 7 cells", 11: "Ternary lithium 8 cells", 12: "Ternary lithium 13 cells", 13: "Ternary lithium 14 cells", 14: "No Battery"}
BMS_CHARGE_LIMIT_MODES: dict = {0: "HMI Setting", 1: "BMS Protocol", 2: "Inverter Logic"}
HYBRID_MODES: dict = {1: "On Grid", 2: "Limit Power to UPS", 3: "Limit Power to Home", 4: "AC Coupling"}
PV_PRIORITY_MODES: dict = {0: "Load Priority", 1: "Charging Priority", 2: "Grid Priority"}
PARALLEL_MODES: dict = {0: "Single machine", 1: "Single-phase parallel", 2: "Two-phase parallel", 3: "Two-phase parallel 120", 4: "Two-phase parallel 180", 5: "Three-phase A", 6: "Three-phase B", 7: "Three-phase C"}
OUTPUT_PRIORITIES: dict = {0: "Solar First", 1: "Utility First", 2: "Solar/Battery/Utility"}
AC_VOLTAGE_RANGES: dict = {0: "Wide band (APL)", 1: "Narrow band (UPS)"}
CHARGING_SOURCE_PRIORITIES: dict = {0: "Solar First", 1: "Utility First", 2: "Solar and Utility Simultaneously", 3: "Solar Only"}
BMS_COMM_MODES: dict = {0: "Disable", 1: "RS485", 2: "CAN"}
BMS_PROTOCOLS: dict = {0: "PACE", 1: "RUDA", 2: "AOGUAN", 3: "OULITE", 4: "CEF", 5: "XINWANGDA", 6: "DAQIN", 7: "WOW", 8: "PYL", 9: "MIT", 10: "XIX", 11: "POL", 12: "GUOX", 13: "SMK", 14: "VOL", 15: "WES", 17: "UZE_CAN", 18: "PYL_CAN", 100: "SGP", 101: "GSL", 102: "PYL2"}
GEN_MODES: dict = {0: "Generator Mode", 1: "Micro Inverter Mode", 2: "Smart Load Mode"}
DISABLED_ENABLED: dict = {0: "Disabled", 1: "Enabled"}
BATTERY_DISCHARGE_MODES: dict = {0: "Standby", 1: "Battery Discharge For Load", 2: "Battery Discharge For Home", 3: "Battery Discharge For Grid"}

# Pre-computed reverse maps so write_lookup_register never rebuilds on each call
_REVERSE_LOOKUPS: dict = {
    id(d): {v: k for k, v in d.items()}
    for d in [
        CHARGING_STATES, MACHINE_STATES, BATTERY_TYPES, BMS_CHARGE_LIMIT_MODES,
        HYBRID_MODES, PV_PRIORITY_MODES, PARALLEL_MODES, OUTPUT_PRIORITIES,
        AC_VOLTAGE_RANGES, CHARGING_SOURCE_PRIORITIES, BMS_COMM_MODES,
        BMS_PROTOCOLS, GEN_MODES, DISABLED_ENABLED, BATTERY_DISCHARGE_MODES,
    ]
}


def read_lookup_register(register: int, lookup: dict, name: str = "") -> str | None:
    """Read a register and return the human-readable string from the lookup dict.
    Falls back to the raw integer string if the value is not in the dict."""
    try:
        result = instr.read_register(register)
    except:
        return None
    value = lookup.get(result, str(result))
    if name:
        debug(f"{name}: {value}")
    return value


def write_lookup_register(register: int, lookup: dict, value: str) -> bool | None:
    """Write a register by reverse-looking up the integer for a string value.
    Uses the same int→string lookup dict as read_lookup_register."""
    reverse = _REVERSE_LOOKUPS.get(id(lookup)) or {v: k for k, v in lookup.items()}
    if value not in reverse:
        return None
    try:
        instr.write_register(register, reverse[value])
    except:
        return None
    return True

def read_time_register(register: int, name: str = "") -> str | None:
    """Read a time register packed as (hours << 8) | minutes. Returns 'HH:MM'."""
    try:
        result = instr.read_register(register)
    except:
        return None
    hours   = (result >> 8) & 0xFF
    minutes =  result       & 0xFF
    value   = f"{hours:02d}:{minutes:02d}"
    if name:
        debug(f"{name}: {value}")
    return value


def write_time_register(register: int, value: str) -> bool | None:
    """Write a time register packed as (hours << 8) | minutes. Accepts 'HH:MM'."""
    try:
        hours, minutes = map(int, value.split(":"))
        instr.write_register(register, (hours << 8) | minutes)
    except:
        return None
    return True


def read_enabled_register(register: int, name: str = "") -> str | None:
    """Read a register where 0 = Disabled and 1 = Enabled. Returns the string."""
    return read_lookup_register(register, DISABLED_ENABLED, name)


def write_enabled_register(register: int, value: str) -> bool | None:
    """Write a register that accepts 'Enabled' (writes 1) or 'Disabled' (writes 0)."""
    return write_lookup_register(register, DISABLED_ENABLED, value)


def read_bit_register(register: int, bit: int, name: str = "") -> str | None:
    """Read a single bit from a register. Returns 'Enabled' (1) or 'Disabled' (0).
    Performs a full register read; use for packed bit-field registers like TimedChgSource."""
    try:
        result = instr.read_register(register)
    except:
        return None
    value = "Enabled" if (result >> bit) & 1 else "Disabled"
    if name:
        debug(f"{name} bit {bit}: {value}")
    return value


def write_bit_register(register: int, bit: int, value: str) -> bool | None:
    """Set or clear a single bit in a register via read-modify-write.
    Accepts 'Enabled' (sets the bit) or 'Disabled' (clears the bit)."""
    try:
        raw = instr.read_register(register)
        if value == "Enabled":
            raw |= (1 << bit)
        else:
            raw &= ~(1 << bit)
        instr.write_register(register, raw)
    except:
        return None
    return True


def read_long_register(register: int, scale: float = 1.0, name: str = "") -> str | None:
    """Read a 32-bit little-endian value from two consecutive registers.
    Returns a formatted string after applying scale."""
    try:
        result = instr.read_long(register, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except:
        _record_modbus_result(False)
        return None
    _record_modbus_result(True)
    result = float(result) * scale
    value = _format_scaled(result, scale)
    if name:
        debug(f"{name}: {value}")
    return value


def read_datetime_register(register: int, name: str = "") -> str | None:
    """Read three consecutive registers encoding an SRNE packed datetime.
    Format per register: high byte = first field, low byte = second field.
    Registers: [year|month, day|hour, minute|second]. Returns 'YYYY-MM-DD HH:MM:SS'."""
    try:
        results = instr.read_registers(register, 3)
    except:
        _record_modbus_result(False)
        return None
    _record_modbus_result(True)
    year   = (results[0] >> 8) & 0xFF
    month  =  results[0]       & 0xFF
    day    = (results[1] >> 8) & 0xFF
    hour   =  results[1]       & 0xFF
    minute = (results[2] >> 8) & 0xFF
    second =  results[2]       & 0xFF
    value  = f"20{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    if name:
        debug(f"{name}: {value}")
    return value

def write_system_date_time():
    # Get the current system date and time using datetime.now()

    tz = os.getenv("TIMEZONE")
    timezone = pytz.timezone(tz) if tz else None
    now = datetime.now(timezone)

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


def read_failcode(register: int, name: str):
    try:
        result = instr.read_register(register)
    except:
        return None

    error_code = result
    description = __error_lists(error_code)
    if error_code != 0:
        print('Detected error in %s: Code %d: "%s"' % (name, error_code, description))
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
        10: "AFCI Fault/Boost overcurrent (software protection)",
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
        63: "BMS alarm low battery",
    }
    return errors[code]
