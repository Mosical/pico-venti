"""Handle interactions with SHT4x devices over i2c. Based off of Sinsiron Datasheet as well
their example python code modified for micropython
https://github.com/Sensirion/python-i2c-sht4x/tree/master/sensirion_i2c_sht4x

TODO: Package this as a separate package as there is no supported micropython library for the sht4x
"""
import time
import struct

from machine import I2C
from hardware_drivers import sht4x_mode


def _crc8_check(reading: int) -> int:
    """Calculate the CRC8 value from the reading for comparison against the returned CRC value
    Based on Table 6 in
    https://www.digikey.com/en/htmldatasheets/production/7348237/0/0/1/sek-sht40-ad1b-sensors

    Args:
        reading (int): Value read from the SHT4x representing either the temperature or humidity

    Returns:
        int: calculated CRC8
    """
    initial = 0xFF
    polynomial = 0x31
    buffer = struct.pack(">H", reading)
    crc = initial
    for byte in buffer:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
    crc &= 0xFF
    return crc


def _calculate_temp(temp: int) -> float:
    """Convert the sensor output of the temperature into degrees Celcius using the formula on page
    10 of https://www.digikey.com/en/htmldatasheets/production/7348237/0/0/1/sek-sht40-ad1b-sensors

    Args:
        temp (int): Temperature int unpacked from raw sensor output bytes

    Returns:
        float: Temperature reading converted to Celsius
    """
    return ((temp * 175.0) / 65535.0) - 45.0


def _calculate_rh(hum: int) -> float:
    """Convert the sensor output of the relative humidity into degrees Celcius using the formula on
    page 10 of
    https://www.digikey.com/en/htmldatasheets/production/7348237/0/0/1/sek-sht40-ad1b-sensors

    Args:
        hum (int): Humidity int unpacked from raw sensor output bytes

    Returns:
        float: Relative Humidity reading
    """
    return ((hum * 125.0) / 65535.0) - 6.0


class SHT4X:
    """I2C control class for interacting with SHT4X sensors

    Able to perform the following:
        1. Accepts a mode and confirms it is a valid mode to set the sensor to
        2. Perform TX operation based on the selected mode
        3. Waits a variable amount of time based on selected mode
        4. Perform RX operation to read response based on selected mode
        5. Use CRC8 values to confirm RX reading
        6. Convert bytes from RX into human readable output
    """

    def __init__(self, i2c: I2C, address: int = 0x44):
        """Create the SHT4X object used to control and read from an SHT4X sensor

        Example:
            ```
            from machine import Pin, I2C

            i2c = I2C(0, scl=Pin(1), sda=Pin(0))
            sht4x = sht4x_driver.SHT4X(i2c)
            sht4x.reset()

            while True:
                reading = sht4x.get_readings('high_precision')
                print(f"Temp: {reading[0]:.1f}")
                print(f"RH: {reading[1]:.1f}")
            ```

        Args:
            i2c (I2C): i2c object used to interact with the sht4x
            address (int, optional): i2c address of the sht4x
            Usually not configurable, check the datasheet for the correct value. Defaults to 0x44.
        """
        self.i2c = i2c
        self.i2c_address = address
        # Define the structure of the sensor readings
        # Sensor readings are: (Temp reading, Temp CRC, RH Reading, RH CRC)
        # See page 9 of
        # https://www.digikey.com/en/htmldatasheets/production/7348237/0/0/1/sek-sht40-ad1b-sensors
        self.rx_struct = ">HBHB"
        self.rx_size = struct.calcsize(self.rx_struct)
        self.modes = sht4x_mode.define_modes()

    def _confirm_mode(self, requested_mode: str) -> None:
        """Check if the requested mode exists

        Args:
            requested_mode (str): mode requested by SHT4X `get_readings` call

        Raises:
            AttributeError: error explaining that the requested mode is not valid
        """
        if not self.modes.get(requested_mode):
            raise AttributeError(f"Invalid mode {requested_mode} was attempted to be set")

    def _tx(self, mode: sht4x_mode.SensorMode) -> None:
        """Perform TX operation sending the command_hex as bytes and waiting the read_delay length

        Args:
            mode (SensorMode): Requested mode SensorMode object
        """
        self.i2c.writeto(self.i2c_address, bytes([mode.command_hex]), False)
        time.sleep(mode.read_delay)

    async def _rx_check(self, rx_data: bytes, setting: str) -> tuple[int, int]:
        """Use the `_crc8_check` calculation to confirm that both the temperature and relative
        humidity readings are valid and attempt to get them again if they were

        TODO: Currently this will recursively attempt this infinitely may want to throw an error
        if the CRC check fails enough times

        Args:
            rx_data (bytes): bytes read from the SHT4X
            setting (str): mode the reading was taken with, only used if the CRC check fails

        Returns:
            tuple[int, int]: Temperature and Relative Humidity raw value read from the SHT4X
        """
        temp, temp_crc, rel_h, rh_crc = struct.unpack(self.rx_struct, rx_data)
        if _crc8_check(temp) != temp_crc or _crc8_check(rel_h) != rh_crc:
            self.reset()
            await self.get_readings(setting)
        return temp, rel_h

    def reset(self) -> None:
        """Perform soft reset operation of the SHT4X Sensor"""
        mode = self.modes["reset"]
        self._tx(mode)

    def get_serial(self) -> int:
        """Read the serial number of the SHT4X

        Returns:
            int: integer representing the unique serial number of the SHT4X sensor
        """
        mode = self.modes["serial"]
        serial_struct = ">I"
        serial_size = struct.calcsize(serial_struct)
        self._tx(mode)
        serial = self.i2c.readfrom(self.i2c_address, serial_size, False)
        assert isinstance(serial_number := struct.unpack(serial_struct, serial)[0], int)
        return serial_number

    async def get_readings(self, setting: str) -> tuple[float, float]:
        """Get temperature and relative humidity readings converted into human readable values based
        on the mode selected

        Args:
            setting (str): mode to use when getting the values

        Returns:
            tuple[float, float]: Temperature as degrees Celsius and Relative Humidity value
        """
        self._confirm_mode(setting)
        mode = self.modes[setting]
        self._tx(mode)
        rx_data = self.i2c.readfrom(self.i2c_address, self.rx_size, False)
        temp, hum = await self._rx_check(rx_data, setting)
        temp_c = _calculate_temp(temp)
        rel_h = _calculate_rh(hum)
        return temp_c, rel_h
