"""Async webserver to load and allow changing the fan controller settings"""
import asyncio
import machine
from network_drivers.manage_configs import write_settings, config_html
from network_drivers.network_utils import serve_static_content, load_ssl
from network_drivers.file_manager import (
    get_file_delete_html,
    process_deletion_request,
    get_file_upload_html,
    uploaded_html,
)


async def write_html(writer: asyncio.StreamWriter, html: str) -> None:
    """Write a basic HTML page small enough not to need to be streamed in chunks

    Args:
        writer (asyncio.StreamWriter): async HTTP writer
        html (str): HTML to send to the client
    """
    writer.write("HTTP/2.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    writer.write(html)
    await writer.drain()


async def process_gets(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, req: str
) -> None:
    """Process any GET requests to the web server

    Args:
        reader (asyncio.StreamReader): async HTTP reader
        writer (asyncio.StreamWriter): async HTTP writer
        req (str): First line of HTTP request which contains GET parameters
    """
    # Server will close the connection if the whole request hasn't been read before responding
    await reader.read(1024)
    if (uri := req.split("HTTP")[0].split("GET")[-1].strip()) == "/":
        await config_html(writer)
    elif "delete" in uri:
        await get_file_delete_html(writer)
    elif "upload" in uri:
        await write_html(writer, get_file_upload_html())
    else:
        await serve_static_content(uri, writer)


async def receive_header(reader: asyncio.StreamReader) -> dict[str, str]:
    """Process data sent to the web server to parse the HTTP headers

    Args:
        reader (asyncio.StreamReader): async HTTP reader

    Returns:
        dict[str, str]: HTTP headers parsed into a dictionary
    """
    header = []
    finished = False
    while not finished:
        if (req := (await reader.readline()).decode("utf-8")) != "\r\n":
            header.append((req.strip().split(":", 1)))
        else:
            finished = True
    return dict(header)


async def receive_urlencoded(reader: asyncio.StreamReader, content_length: int) -> str:
    """Process data sent in the body of a POST request if the data was urlencoded

    Args:
        reader (asyncio.StreamReader): async HTTP reader
        content_length (int): Content length reported by the HTTP Headers

    Returns:
        str: HTML page as a string to respond with
    """
    chunk = 1024
    # Ensure the entire config can be downloaded
    # If something urlencoded is bigger than 2048 bytes should rewrite to use multipart
    if content_length > chunk:
        chunk *= 2
    received = (await reader.read(chunk)).decode("utf-8")
    if "hostname=" in received:
        return write_settings(received)
    if "delete=delete" in received:
        return process_deletion_request(received)
    return ""


async def receive_multipart(reader: asyncio.StreamReader, file_size: int, boundary: str) -> str:
    """Process data sent in the body of a POST request if the data was sent as a multipart form

    Args:
        reader (asyncio.StreamReader): async HTTP reader
        file_size (int): Content length reported by the HTTP Headers
        boundary (str): boundary string separating multipart parts

    Returns:
        str: HTML page as a string to respond with
    """
    downloaded = 0
    file_name = ""
    # Working with 512 byte chunks for memory purposes
    while downloaded < file_size:
        # Find the file name and create the file if nothing has been downloaded yet
        if downloaded == 0:
            file_start = (await reader.read(512)).split(b"\r\n")
            file_name = dict(
                [
                    key.replace("=", ":").split(":")
                    for key in file_start[1].decode("utf-8").split(";")
                ]
            )[" filename"].strip('"')
            with open(file_name, "wb") as new_file:
                new_file.write(file_start[-1])
        # Try to find if the next chunk would be the last and download two chunks at once to ensure
        # the file boundary can be removed
        elif file_size - (downloaded + 512) <= 512:
            final_chunk = (await reader.read(1024)).replace(
                f"\r\n--{boundary}--\r\n".encode("utf-8"), b""
            )
            with open(file_name, "ab") as final_file:
                final_file.write(final_chunk)
            downloaded += 512
        else:
            with open(file_name, "ab") as append_file:
                append_file.write(await reader.read(512))
        downloaded += 512
    return uploaded_html(file_name)


async def process_posts(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Process any POST requests to the web server

    Args:
        reader (asyncio.StreamReader): async HTTP reader
        writer (asyncio.StreamWriter): async HTTP writer
    """
    header = await receive_header(reader)
    content_length = int(header["Content-Length"].strip())
    if "x-www-form-urlencoded" in header["Content-Type"]:
        response = await receive_urlencoded(reader, content_length)
        await write_html(writer, response)
        await asyncio.sleep(30)
        machine.reset()
    elif "multipart" in header["Content-Type"]:
        boundary = header["Content-Type"].split("boundary=")[1]
        response = await receive_multipart(reader, content_length, boundary)
        await write_html(writer, response)
        await asyncio.sleep(30)
        machine.reset()


async def _accept_connections(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Accept connections, receive requests, and send response loop"""
    if "GET" in (req := (await reader.readline()).decode("utf-8")):
        await process_gets(reader, writer, req)
    elif "POST" in req:
        await process_posts(reader, writer)
    await writer.wait_closed()


async def start_server() -> None:
    """Start the async server"""
    server = (
        asyncio.start_server(_accept_connections, "0.0.0.0", 443, ssl=ssl_context)
        if (ssl_context := load_ssl())
        else asyncio.start_server(_accept_connections, "0.0.0.0", 80)
    )
    asyncio.create_task(server)
