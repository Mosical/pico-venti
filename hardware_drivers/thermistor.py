"""Micropython driver for thermistors wired in a voltage divider circuit. Not sure if anything
different would be needed for a PTC thermistor, this is only tested with NTC thermistors"""
import asyncio
from math import log
from machine import ADC


def _average(readings: list[int]) -> float:
    """Get an average value from a list of integers

    Args:
        readings (list[int]): list of integers to average

    Returns:
        float: average value of the list
    """
    return sum(readings) / len(readings)


class Thermistor:
    """Class to handle NTC thermistors"""

    def __init__(self, pin: ADC):
        """Prepares a thermistor object to be used to read the temperature. Use `thermistor_specs()`
        method if any of the defaults here do not match the datasheet of the thermistor in use.

        Example:
            ```
            from machine import Pin, ADC
            from thermistor import Thermistor

            # On a raspberry pi pico Pin 28 is ADC 2, setting pin28 to Pin.IN improved the reading
            # accuracy in my testing. Machine.ADC setup will vary by microcontroller
            pin = Pin(28, Pin.IN)
            adc = ADC(2)

            thermistor = Thermistor(adc)
            temp = thermistor.ntc()
            ```

        Args:
            pin (ADC): machine.ADC object used to read the thermistor voltage divider circuit
        """
        self.pin = pin
        self.nominal_temp = 25
        self.b_coefficient = 3950
        self.nominal_resistor = 10000
        self.extenal_resistor = 10000
        self.max_reading = 65535  # 2^16-1 The highest value that can be returned by ADC.read_u16()

    async def _read_adc(self, num_readings: int) -> float:
        """Read the ADC input for a number of times to get a value with less jitter. The default is
        10 readings, with .1s in between giving a temperature reading approximately every second
        when looped

        Args:
            num_readings (int): number of readings to take and average

        Returns:
            float: averaged reading from the ADC
        """
        readings = []
        for _ in range(num_readings):
            readings.append(self.pin.read_u16())
            await asyncio.sleep(0.1)
        return _average(readings)

    def _calculate_resistance(self, reading: float) -> float:
        """Calculate the resistance based on the ADC reading. ADC is a range from 0 to 2^16 -1
        which is the highest value for a 16 (u16) bit unsigned int. 0 would be no signal or no
        voltage which would require an infinite resistance. 65535 would be reference voltage, 3.3V
        for many microcontrollers which would require zero resistance

        Based on the equation for calculating input voltage from ADC reading
            ADC = V*(2^16)/Vref
        And the equation for output voltage of a voltage divider circuit
            V = (R/R+R0)Vref
        Voltage output from the voltage divider is the input voltage of the ADC, combined and solved
        for Thermistor resistance
            R = R0/((2^16/ADC)-1)

        Args:
            reading (float): average readings from the ADC

        Returns:
            float: Calculated resistance
        """
        return self.extenal_resistor / ((self.max_reading / reading) - 1)

    def _steinhart_hart(self, resistance: float) -> float:
        """Use the Steinhart-Hart equation to calculate the temperature based on the variable
        resistance read from the thermistor

        Equation used is 1/T = 1/T0 + ln(R/R0)/B

        Where T0 is the reference temp, R is the measured resistance, R0 is the reference/nominal
        resistance value, and B is the beta coefficent of the thermistor. All reference values
        should come from the thermistor datasheet

        Return value is converted to Celsius

        Args:
            resistance (float): resistance calculated from the average ADC readings

        Returns:
            float: Temperature measured by the thermistor in celsius
        """
        inv_t0 = 1 / (self.nominal_temp + 273.15)
        nat_log = log((resistance / self.nominal_resistor)) / self.b_coefficient
        inv_temp = inv_t0 + nat_log
        temp = 1 / inv_temp
        return temp - 273.15

    def thermistor_specs(
        self,
        temp: int = 25,
        beta: int = 3950,
        nominal_resist: int = 10000,
        const_resist: int = 10000,
    ) -> None:
        """Method to change the values used in calculating the temperature from the reading of the
        voltage divider circuit. If the default values are correct there is no need to call this
        method. All inputs default to the same values as the class, only pass the values that must
        be updated. The default values should be standard for basic NTC thermistors

        Args:
            temp (int, optional): Nominal temperature from thermistor datasheet. Defaults to 25.
            beta (int, optional): steinhart-hart beta coefficient of thermistor. Defaults to 3950.
            nominal_resist (int, optional): Nominal resistance of the thermistor Defaults to 10000.
            const_resist (int, optional): resistance of constant resistor. Defaults to 10000.
        """
        self.nominal_temp = temp
        self.b_coefficient = beta
        self.nominal_resistor = nominal_resist
        self.extenal_resistor = const_resist

    async def ntc(self, readings: int = 10) -> float:
        """Get the temperature in Celsius from an NTC thermistor

        Args:
            readings (int, optional): number of readings to average, helps with jitter.
            Defaults to 10.

        Returns:
            float: Temperature calculated from an NTC thermistor
        """
        adc_reading = await self._read_adc(readings)
        therm_resistance = self._calculate_resistance(adc_reading)
        return self._steinhart_hart(therm_resistance)
