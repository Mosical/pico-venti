"""Logic to run at startup, either serves the wifi login page or runs the fan controller"""
import os
import time
import asyncio
from hardware_drivers.fan_controller import FanController
from network_drivers.wifi_setup import WifiSetup
from network_drivers.influxdb_client import InfluxClient
from network_drivers.webserver import start_server
from network_drivers.network_utils import setup_station_mode


async def sensor_loop(controller: FanController, influx_client: InfluxClient) -> None:
    """Logic to get readings, set fan speed, and send readings to influxDB

    Args:
        controller (FanController): Fan Controller object
        influx_client (InfluxClient): InfluxDB POST data object
    """
    while True:
        thermistor = await controller.get_thermistor_temps()
        sht4x = await controller.get_sht4x_readings()
        temperatures = (thermistor, [item[0] for item in sht4x])
        influx_client.send_data((thermistor, sht4x))
        controller.display_temps(thermistor[controller.oled[1]], sht4x[controller.oled[2]])
        controller.set_fans(temperatures)


def main() -> None:
    """Function to run the pico fan controller"""
    # Add a 5 second delay to be able to kill boot.py if there are issues
    time.sleep(5)
    # If the WiFi credentials aren't saved serve the wifi setup page
    if "ssid_credentials" not in os.listdir():
        ap_mode = WifiSetup()
        ap_mode.show_ip()
        login_loop = asyncio.get_event_loop()
        login_loop.create_task(ap_mode.start_server())
        login_loop.run_forever()

    # If wifi credentials are available start both the fan controller and settings page
    ip_address = setup_station_mode()
    fan_controller = FanController(ip_address)
    influx = InfluxClient()

    loop = asyncio.get_event_loop()
    loop.create_task(start_server())
    loop.create_task(sensor_loop(fan_controller, influx))
    loop.run_forever()


main()
