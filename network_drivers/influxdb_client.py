"""Send data to influxdb for grafana or other timeseries purposes"""
import json
import requests


def _load_config() -> dict:
    """Load the settings from the json file

    Returns:
        dict[str, dict[str, str | int | bool]]: dict loaded from config.json
    """
    with open("config.json", "r", encoding="utf-8") as config_file:
        return json.load(config_file)


class InfluxClient:
    """Class to handle InfluxDB configuration and sending data"""

    def __init__(self) -> None:
        """Create the object to send all sensor data to influxDB for graph purposes

        Example:
            ```
            from influxdb_client import InfluxClient

            # code to retrieve thermistor and sht4x readings #

            influx = InfluxClient()
            influx.send_data([thermistor, sht4x])
            ```
        """
        self.config = _load_config()
        self.url = self.create_url()
        self.header = self.create_header()

    def create_header(self) -> dict[str, str]:
        """Create headers dict using config file

        Returns:
            dict[str, str]: Headers needed to send data to InfluxDB
        """
        headers = {
            "Authorization": f"Token {self.config['influxdb']['token']}",
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json",
        }
        return headers

    def create_url(self) -> str:
        """Construct the URL of the influxdb server using config file

        Returns:
            str: InfluxDB api write URL
        """
        base_url = (
            f'https://{self.config["influxdb"]["url"]}'
            if self.config["influxdb"]["ssl"]
            else f'http://{self.config["influxdb"]["url"]}'
        )
        base_url += (
            f':{self.config["influxdb"]["port"]}/api/v2/write?'
            if {self.config["influxdb"]["port"]} != ""
            else "/api/v2/write?"
        )
        uri = f'org={self.config["influxdb"]["org"]}&bucket={self.config["influxdb"]["bucket"]}'
        return f"{base_url}{uri}&precision=ns"

    def parse_data(self, data: tuple[list[float], list[tuple[float, float]]]) -> str:
        """Parse the input data and build a URLEncoded body that will be sent to InfluxDB

        ref: https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/ for format

        Args:
            data (tuple[list[float], list[tuple[float, float]]]): List of lists of sensor readings

        Returns:
            str: body to send to influxDB based on "line protocol" syntax
        """
        thermistor = data[0]
        sht4x = data[1]
        post_data = f'picofan,location={self.config["influxdb"]["location"]} '
        for indx, therm_entry in enumerate(thermistor):
            post_data += f"thermistor{indx}_temperature={therm_entry},"
        for indx, entry in enumerate(sht4x):
            post_data += f"sht4x_{indx}_temperature={entry[0]},"
            post_data += f"sht4x{indx}_humidity={entry[1]},"
        return post_data.rstrip(",")

    def send_data(self, data: tuple[list[float], list[tuple[float, float]]]) -> None:
        """POST sensor readings into InfluxDB

        Args:
            data (tuple[list[float], list[tuple[float, float]]]): Sensor readings
        """
        params = self.parse_data(data)
        # Catching all exceptions so that infrequent failures due to network issues or running out
        # of memory doesn't cause the whole application to crash
        try:
            response = requests.post(self.url, headers=self.header, data=params)
        except Exception as e:  # pylint: disable=W0718
            print(e)
            return
        print(response.status_code)
        response.close()
