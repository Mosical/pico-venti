"""Various functions to manage files over the network"""
import os
import asyncio
from network_drivers.network_utils import html_head, url_unencode


def get_files(path: str = ""):
    """Recursive generator function to walk through all directories and list all files with their
    full path

    Note: if there are any empty directories they will not be listed

    Args:
        path (str, optional): Path to start walking down. Defaults to "". This defaults to starting
        in the root directory

    Yields:
        Generator[str]: Generator of fully qualified file names
    """
    for files in os.ilistdir(path):
        if files[1] == 0x8000:
            yield f"{path}/{files[0]}".lstrip("/")
        else:
            yield from get_files(f"{path}/{files[0]}")


async def get_file_delete_html(writer: asyncio.StreamWriter) -> None:
    """Create an HTML form to allow deleting files off of the microcontroller's flash

    Streams the HTML to the client as it builds to save memory
    """
    writer.write("HTTP/2.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    file_list = list(get_files())
    html = html_head()
    html += '<body><h1>Select Files to Delete</h1><form id="delete" action="" method="post">\n'
    html += '<input type="hidden", id="delete", name="delete", value="delete">\n'
    writer.write(html)
    await writer.drain()
    for file in file_list:
        html = f'<input type="checkbox" id="{file}" name="{file}" value="{file}" class=checkbox>\n'
        html += f'<label for="{file}" class=checkbox_label>{file}</label><br>\n'
        writer.write(html)
        await writer.drain()
    html = '<button type="submit" value="delete">Submit</button></form></body></html>'
    writer.write(html)
    await writer.drain()


def parse_deletion_parameters(params: str) -> list[str]:
    """Parse the URLEncoded POST data into a list of the filenames requested for deletion

    Args:
        params (str): URLEncoded POST data

    Returns:
        list[str]: list of file names
    """
    cleaned_params = [url_unencode(split_params) for split_params in params.split("&")]
    file_list = [file.split("=")[0] for file in cleaned_params]
    file_list.remove("delete")
    return file_list


def process_deletion_request(parameters: str) -> str:
    """Delete files that were requested for deletion via the webpage

    Args:
        parameters (str): POST data from delete page

    Returns:
        str: HTML page showing the files that were deleted
    """
    delete_request = parse_deletion_parameters(parameters)
    html = html_head()
    html += "<body><h1>Deleted Files</h1><ol>\n"
    for file in delete_request:
        os.remove(file)
        html += f"<li>{file}</li>\n"
    html += "</ol></body></html>"
    return html


def get_file_upload_html() -> str:
    """Create an HTML page for uploading a file to the fan controller

    Returns:
        str: HTML page that allows uploading a file
    """
    html = html_head()
    html += """
    <body>
    <h1>Upload file</h1>
    <form method="post" enctype="multipart/form-data">
        <div>
            <label for="file" class=upload_label>Choose file to upload: </label>
            <input type="file" class=upload id="file" name="file" multiple />
        </div>
        <br>
        <div>
            <button>Submit</button>
        </div>
    </form>
    </body>
    </html>
    """
    return html


def uploaded_html(filename: str) -> str:
    """Create an HTML page reporting a file was successfully uploaded

    Returns:
        str: HTML page reporting the file that was uploaded
    """
    html = html_head()
    html += f"""
    <body>
        <h1>Uploaded file</h1>
        <p>{filename}</p>
    </body>
    </html>
    """
    return html
