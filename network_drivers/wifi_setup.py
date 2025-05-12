"""Present a webpage made to choose wifi network if no credentials are saved"""
import json
import asyncio
import network
import ubinascii
from machine import Pin, I2C, reset
from hardware_drivers.oled import OLED
from network_drivers.network_utils import (
    html_head,
    process_req,
    serve_static_content,
    load_ssl,
    url_unencode,
)


def _start_station() -> network.WLAN:
    """Start the pico wifi in station mode to scan for available networks

    Returns:
        network.WLAN: WiFi network driver
    """
    station = network.WLAN(network.STA_IF)
    station.active(True)
    return station


def _start_display(sda_pin: int, scl_pin: int) -> OLED:
    """Configure the i2c oled driver to be used to display AP info

    Args:
        sda_pin (int): I2C SDA Pin number.
        scl_pin (int): I2C SCL Pin number.

    Returns:
        OLED: OLED driver
    """
    i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
    display = OLED(i2c)
    return display


def _logged_in() -> str:
    """Create an HTML page to be displayed after selecting and saving credentials

    Returns:
        str: HTML page as a single string
    """
    html = html_head()
    html += """
            <body>
                <h1>WiFi credentials saved</h1>
                <div>System will now restart and connect to the saved network</div>
            </body>
        </html>
    """
    return html


def _process_credentials(secrets: str) -> None:
    """Parse the secrets sent in as form data and write it as a base64 encoded string to a file

    Args:
        secrets (str): form data input for wifi credentials
    """
    ssid, password = [url_unencode(param) for param in secrets.split("&")]
    credentials = {"ssid": ssid.split("=")[-1], "password": password.split("=")[-1]}
    byte = json.dumps(credentials).encode("utf-8")
    encoded = ubinascii.b2a_base64(byte)
    with open("ssid_credentials", "wb") as file:
        file.write(encoded)


class WifiSetup:
    """Class to set up a WiFi access point and server a webpage to select your network"""

    def __init__(
        self,
        ssid: str = "picoventi",
        password: str = "raspberry",
        sda_pin: int = 0,
        scl_pin: int = 1,
    ):
        """Start the object that handles network and display drivers. Used to handle a webserver
        to interactively select the wifi network if no credentials are saved

        Example:
            ```
            import asyncio
            from wifi_setup import WifiSetup

            ap_mode = WifiSetup()
            ap_mode.show_ip()
            loop = asyncio.get_event_loop()
            loop.create_task(ap_mode.start_server())
            loop.run_forever()
            ```

        Args:
            ssid (str, optional): AP Name. Defaults to "pico_fan".
            password (str, optional): AP Password. Defaults to "raspberry".
            sda_pin (int, optional): I2C SDA Pin number. Defaults to 0.
            scl_pin (int, optional): I2C SCL Pin number. Defaults to 1.
        """
        self.password = password
        self.access_point = self._start_ap(ssid)
        self.station = _start_station()
        self.display = _start_display(sda_pin, scl_pin)
        self.networks = self._get_networks()

    def _start_ap(self, ssid: str) -> network.WLAN:
        """Start the pico wifi in AP mode to allow connections before credentials are saved

        Args:
            ssid (str, optional): Name of Access Point. Defaults to "pico_fan".
            password (str, optional): Password for access point. Defaults to "raspberry".

        Returns:
            network.WLAN: WiFi network driver
        """
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password=self.password)
        ap.active(True)
        return ap

    def _get_networks(self) -> list[str]:
        """Get a list of networks in range of the pico

        Args:
            station (network.WLAN): Station mode wifi driver

        Returns:
            list[str]: List of wifi SSID names in range
        """
        network_list = []
        networks = self.station.scan()
        for net in networks:
            if name := net[0].decode("utf-8"):
                network_list.append(name)
        return network_list

    def _login_page(self) -> str:
        """Create an HTML login page with all available SSIDs in a dropdown

        Args:
            ssid_list (list[str]): List of SSID names in range of the pico

        Returns:
            str: HTML page as a single string
        """
        html = html_head()
        html += """
                <body>
                    <h1>Enter WiFi Info</h1>
                    <form action="" method="post">
                        <label for="ssid">Network:&nbsp;&nbsp;</label>
                        <select name="ssid" id="ssid">
            """
        for ssid in self.networks:
            html += f'<option value="{ssid}">{ssid}</option>'
        html += """
                        </select>
                        <br>
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password"><br><br>
                        <button type="submit">Submit</button>
                    </form>
                </body>
            </html>
        """
        return html

    def show_ip(self) -> None:
        """Display the IP address, SSID, and Password on the integrated oled screen"""
        self.display.start_screen()
        self.display.clear_framebuffer()
        self.display.write_text(f"SSID: {self.access_point.config('ssid')}", 0, 0)
        self.display.write_text(f"Pass: {self.password}", 0, 10)
        self.display.write_text(f"IP: {self.access_point.ifconfig()[0]}", 0, 20)
        self.display.display_text()

    async def _accept_connections(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Accept connections, receive requests, and send response loop"""
        request = await reader.read(1024)
        if (received := process_req(request)) == "/":
            response = self._login_page()
            writer.write("HTTP/2.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            writer.write(response)
            await writer.drain()
        elif "ssid" in received:
            _process_credentials(received)
            response = _logged_in()
            writer.write("HTTP/1.0 200 OK\r\n")
            writer.write(response)
            await writer.drain()
            await writer.wait_closed()
            await asyncio.sleep(5)
            self.station.deinit()
            self.access_point.deinit()
            reset()
        else:
            await serve_static_content(received, writer)
        await writer.wait_closed()

    async def start_server(self) -> None:
        """Start the async server"""
        server = (
            asyncio.start_server(self._accept_connections, "0.0.0.0", 443, ssl=ssl_context)
            if (ssl_context := load_ssl())
            else asyncio.start_server(self._accept_connections, "0.0.0.0", 80)
        )
        print("Starting Server")
        asyncio.create_task(server)
