"""Creates a more human readable representation of the 'modes' available for the SHT4x sensors"""
from ucollections import namedtuple

SensorMode = namedtuple("SensorMode", ("command_hex", "read_delay"))


def define_modes() -> dict[str, SensorMode]:
    """Define all of the available modes to control a SHT4X i2c sensor

    Based on:
    https://github.com/Sensirion/python-i2c-sht4x/blob/master/sensirion_i2c_sht4x/commands.py

    Table of each command and explanations available here:
    https://www.digikey.com/en/htmldatasheets/production/7348237/0/0/1/sek-sht40-ad1b-sensors

    The modes are a dict labeling them with a human readable name and a tuple.
    The tuple is a named tuple to improve readability

    SensorMode defines what is needed to communicate over i2c to be used by the driver
    command_hex: defines what bytes to send to the SHT4X (in hex)
    read_delay: defines a wait time between sending the command (tx) and reading from the SHT4x (rx)

    Returns:
        Dict[str, SensorMode[int, float]]: Available commands for i2c SHT4X
    """
    modes = {
        "high_precision": SensorMode(command_hex=0xFD, read_delay=0.01),
        "medium_precision": SensorMode(command_hex=0xF6, read_delay=0.005),
        "low_precision": SensorMode(command_hex=0xE0, read_delay=0.002),
        "high_heat_long": SensorMode(command_hex=0x39, read_delay=1.1),
        "high_heat_short": SensorMode(command_hex=0x32, read_delay=0.11),
        "mid_heat_long": SensorMode(command_hex=0x2F, read_delay=1.1),
        "mid_heat_short": SensorMode(command_hex=0x24, read_delay=0.11),
        "low_heat_long": SensorMode(command_hex=0x1E, read_delay=1.1),
        "low_heat_short": SensorMode(command_hex=0x15, read_delay=0.11),
        "reset": SensorMode(command_hex=0x94, read_delay=0.01),
        "serial": SensorMode(command_hex=0x89, read_delay=0.01),
    }
    return modes
