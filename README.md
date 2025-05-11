# Pico Venti

Raspberry Pi Pico W based Fan controller

## Available Features

* SHT4X temperature and humidity sensors
* NTC Thermistor
* PWM Fan control
* Web based setting management
* Publish readings to Grafana via InfluxDB

## Installation

Use venv to install the development requirements and use  mpremote to install this project as well as the dependency `ssd1306`

### Setup your workspace

```bash
git clone git@github.com:Mosical/pico-venti.git
cd pico-venti/
python3 -m venv pico-venti
source pico-venti/bin/activate
python3 -m pip install -r requirements-dev.txt
```

### Install to the pico

*Note the pico may be available at a different device name than /dev/ttyACM0 depending on your PC*

```bash
mpremote connect /dev/ttyACM0 mip install ssd1306
mpremote connect /dev/ttyACM0 fs cp -r static/ :static/
mpremote connect /dev/ttyACM0 fs cp -r hardware_drivers/ :hardware_drivers/
mpremote connect /dev/ttyACM0 fs cp -r network_drivers/ :network_drivers/
mpremote connect /dev/ttyACM0 fs cp example_config.json :config.json
mpremote connect /dev/ttyACM0 fs cp boot.py :main.py
```

You can also copy over an SSL Certificate and Key in DER format named cert.der and key.der now if you would like to use HTTPS for the webservers
