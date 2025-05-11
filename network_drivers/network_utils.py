"""Various utilities related to setting up networking and displaying webpages"""

import os
import ssl
import time
import asyncio
import json
import binascii
import network


def html_head() -> str:
    """Basic HTML header to be used with all webpages that defines basic CSS

    Returns:
        str: Start of an HTML page to serve via the webserver
    """
    html = """<!DOCTYPE html>
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="custom.css">
        </head>
    """
    return html


def _retrieve_credentials() -> tuple[str, str]:
    """Open the base64 encoded wifi credentials and convert it back into standard strings for
    setting up the wifi connection

    Returns:
        tuple[str, str]: SSID and AP Password
    """
    with open("ssid_credentials", "rb") as file:
        data = file.read()
    credentials = json.loads(binascii.a2b_base64(data))
    return credentials["ssid"], credentials["password"]


def connect_to_ap() -> network.WLAN:
    """Use saved credentials to connect to wifi and wait until authentication is done

    Returns:
        network.WLAN: Wifi network driver that has connected to an AP and received an IP Address
    """
    credentials = _retrieve_credentials()
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(credentials[0], credentials[1])
    while station.isconnected() is False:
        time.sleep(1)
    return station


def process_req(request: bytes) -> str:
    """Parse request from clients to determine what the webserver should respond

    Args:
        request (bytes): Bytes sent from the client to the AP

    Returns:
        str: uri to use in webserver response
    """
    req = request.decode("utf-8")
    recv = req.split("\r\n")
    if "POST" in req:
        return recv[-1]
    for line in recv:
        if "GET" in line:
            uri = line.split("HTTP")[0].split("GET")[-1].strip()
            return uri
    return "/"


def setup_station_mode() -> str:
    """Set the hostname and connect to WiFi as a client

    Returns:
        str: IP Address
    """
    with open("config.json", "r", encoding="utf-8") as config_file:
        hostname = json.load(config_file)["hostname"]["hostname"]
    network.hostname(hostname)
    station = connect_to_ap()
    return station.ifconfig()[0]


async def serve_static_content(received: str, writer: asyncio.StreamWriter) -> None:
    """Serve the static content saved on the pico

    Args:
        received (str): content requested
        writer (asyncio.StreamWriter): async stream writing coroutine
    """
    if "favicon.ico" in received:
        writer.write("HTTP/2.0 200 OK\r\nContent-type: image/ico\r\n\r\n")
        with open("static/favicon.ico", "rb") as favicon:
            writer.write(favicon.read())
            await writer.drain()
    elif "custom.css" in received:
        writer.write("HTTP/2.0 200 OK\r\nContent-type: text/css\r\n\r\n")
        with open("static/custom.css", "r", encoding="utf-8") as css:
            writer.write(css.read())
            await writer.drain()
    elif "script.js" in received:
        writer.write("HTTP/2.0 200 OK\r\nContent-type: text/javascript\r\n\r\n")
        with open("static/script.js", "r", encoding="utf-8") as javascript:
            writer.write(javascript.read())
            await writer.drain()


def load_ssl() -> ssl.SSLContext | None:
    """Create an SSLContext object if SSL certs are loaded, otherwise return None

    Returns:
        ssl.SSLContext | None: SSLContext object using SSL certs loaded onto the pico
    """
    if all(x in os.listdir() for x in ("key.der", "cert.der")):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain("cert.der", "key.der")
        return ssl_context
    return None


def url_unencode(string: str) -> str:
    """Convert a URL Encoded string into a UTF-8 encoded string then convert it into a basic string

    Unlike python3's urllib micropython doesn't include an easy way to un-urlencode data retrieved
    from a webserver. For example the webserver will convert an '&' into `%26`, this turns that into
    `\\u0026` which `json.loads` turns back into `&`

    Args:
        string (str): URL Encoded string

    Returns:
        str: String converted back from URL encoding
    """
    json_encode = string.replace("%", r"\u00")
    return str(json.loads(f'"{json_encode}"'))
