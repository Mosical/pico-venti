"""Handle all of the configs that need to be loaded to run the fan controller application"""
import json
import asyncio
from machine import Pin, I2C, ADC

from hardware_drivers.oled import OLED
from hardware_drivers.fan_pwm import FanControl
from hardware_drivers.thermistor import Thermistor
from hardware_drivers.sht4x_driver import SHT4X


def _load_config() -> dict:
    """Load the settings from the json file

    Returns:
        dict[str, dict[str, str | int | bool]]: dict loaded from config.json
    """
    with open("config.json", "r", encoding="utf-8") as config:
        return json.load(config)


class FanController:
    """All objects needed to act as a fan controller"""

    def __init__(self, ip_address: str):
        self.config = _load_config()
        self.thermistors = self._create_thermistors()
        self.i2cs = self._create_i2cs()
        self.sht4x = self._create_sht4x()
        self.oled = self._create_oled()
        self.fans = self._create_fans()
        self.ip_address = ip_address

    def _create_thermistors(self) -> list[Thermistor]:
        """Initialize any number of thermistors using config.json

        Returns:
            list[Thermistor]: list of all defined thermistor objects
        """
        thermistors: list[Thermistor] = []
        configs = self.config["thermistor"]
        for num in range(configs["num_thermistor"]):
            _ = Pin(configs[f"pin_{num}"], Pin.IN)
            adc = ADC(configs[f"adc_{num}"])
            thermistor = Thermistor(adc)
            thermistor.thermistor_specs(
                configs[f"temp_{num}"],
                configs[f"beta_{num}"],
                configs[f"nominal_resistor_{num}"],
                configs[f"external_resistor_{num}"],
            )
            thermistors.append(thermistor)
        return thermistors

    def _create_i2cs(self) -> list[I2C]:
        """Initialize the i2c channels using config.json

        Returns:
            list[I2C]: List of defined i2c objects
        """
        i2cs: list[I2C] = []
        configs = self.config["i2c"]
        for num in range(configs["num_channels"]):
            i2cs.append(I2C(num, scl=configs[f"scl_{num}"], sda=configs[f"sda_{num}"]))
        return i2cs

    def _create_sht4x(self) -> list[tuple[SHT4X, str]]:
        """Initialize the sht4x driver using config.json

        Returns:
            list[tuple[SHT4X, str]]: List of defined SHT4x objects and precision mode
        """
        sht4x: list[tuple[SHT4X, str]] = []
        configs = self.config["sht4x"]
        for num in range(configs["num_sht4x"]):
            sht4x_instance = (
                SHT4X(self.i2cs[configs[f"i2c_channel_{num}"]], configs[f"i2c_address_{num}"]),
                configs[f"mode_{num}"],
            )
            sht4x.append(sht4x_instance)
        return sht4x

    def _create_oled(self) -> tuple[OLED, int, int]:
        """Initialize the oled using config.json

        Returns:
            tuple[OLED, int, int]: oled object and the identifier of the thermistor and sht4x to
            display
        """
        configs = self.config["oled"]
        oled = OLED(
            i2c=self.i2cs[configs["i2c_channel"]],
            horizontal=configs["horizontal"],
            vertical=configs["vertical"],
            address=configs["i2c_address"],
        )
        oled.start_screen()
        return oled, configs["thermistor_number"], configs["sht4x_number"]

    def _create_fans(self) -> list[tuple[FanControl, str, int]]:
        """Initialize the fan controllers using config.json

        Returns:
            list[tuple[FanControl, str, int]]: List of tuples defining fan objects and temp sensor
        """
        fans: list[tuple[FanControl, str, int]] = []
        configs = self.config["fan"]
        for num in range(configs["num_fans"]):
            fan = FanControl(configs[f"pin_fan_{num}"])
            fan.define_curve(
                configs[f"zero_rpm_{num}"],
                configs[f"min_temp_{num}"],
                configs[f"max_temp_{num}"],
                configs[f"fan_curve_{num}"],
            )
            fan_instance = (fan, configs[f"temp_type_{num}"], configs[f"temp_instance_{num}"])
            fans.append(fan_instance)
        return fans

    async def get_thermistor_temps(self) -> list[float]:
        """Get temperature readings from all configured thermistors

        Returns:
            list[float]: list of temperature rea
        """
        temps: list[float] = []
        coro = [asyncio.create_task(thermistor.ntc()) for thermistor in self.thermistors]
        for routine in coro:
            temps.append(await routine)
        return temps

    async def get_sht4x_readings(self) -> list[tuple[float, float]]:
        """_summary_

        Returns:
            list[tuple[float, float]]: _description_
        """
        readings: list[tuple[float, float]] = []
        coro = [asyncio.create_task(sht4x.get_readings(mode)) for sht4x, mode in self.sht4x]
        for routine in coro:
            readings.append(await routine)
        return readings

    def display_temps(self, thermistor: float, sht4x: tuple[float, float]) -> None:
        """Display data on the OLED screen

        Args:
            thermistor (float): thermistor reading to display
            sht4x (tuple[float, float]): sht4x reading to display
        """
        display = self.oled[0]
        display.clear_framebuffer()
        display.write_text(f"Thermistor: {thermistor:.1f}", 0, 0)
        display.write_text(f"Temp: {sht4x[0]:.1f}", 0, 8)
        display.write_text(f"RH: {sht4x[1]:.1f}", 0, 16)
        display.write_text(f"IP:{self.ip_address}", 0, 24)
        display.display_text()

    def set_fans(self, temperatures: tuple[list[float], list[float]]) -> None:
        """_summary_

        Args:
            temperatures (tuple[list[float], list[float]]): _description_
        """
        for pwm_controller in self.fans:
            fan, sensor, instance = pwm_controller
            sensor_type = 0 if "thermistor" in sensor else 1
            fan.set_fan(temperatures[sensor_type][instance])
