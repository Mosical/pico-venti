"""Utilities to help read and write the fan controller settings"""
import json
import asyncio
from collections import OrderedDict
from network_drivers.network_utils import url_unencode, html_head


async def config_html(writer: asyncio.StreamWriter) -> None:
    """Build the HTML settings page with the current settings filled in

    Streams the page back to the client as it is built to save memory
    """
    config = ordered_config()

    writer.write("HTTP/2.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    html = html_head()
    html += """
        <body>
            <h1>PicoFan Config</h1>
            <div class="buttons">
                <button onclick="location.href='upload'">Upload Files</button>
                <button onclick="location.href='delete'">Delete Files</button>
            </div>
            <form id="config" action="" method="post">
    """
    writer.write(html)
    await writer.drain()
    for key, value in config.items():
        html = ""
        instance_div = False
        html += f'<div class="{key}_div">\n'
        html += f"<br><h2>{key}</h2>"
        for subkey in value:
            if "num_" in subkey:
                html += f'<label for="{key}">{subkey}: </label>\n'
                html += f'<select name="{key}_{subkey}" id="{key}">\n'
                for index in range(value[f"max_{key}"]):
                    if (indx := index + 1) == value[subkey]:
                        html += f'<option value={indx} selected="selected">{indx}</option>\n'
                    else:
                        html += f"<option value={indx}>{indx}</option>\n"
                html += "</select><br>\n"
            elif "max_" in subkey and "temp" not in subkey:
                html += '<div class="tooltip">\n'
                html += f'<label for="{key}_{subkey}">{subkey}: </label>\n'
                html += '<span class="tooltiptext">'
                html += "Increasing this would require hardware changes</span>"
                html += f'<input type="text" id="{key}_{subkey}" name="{key}_{subkey}"'
                html += f'value="{value[subkey]}">'
                html += "<br>\n</div>\n"
            elif isinstance(value[subkey], bool):
                html += f'<label for="{key}_{subkey}">{subkey}: </label>\n'
                html += f'<select name="{key}_{subkey}" id="{key}_{subkey}">\n'
                html += "<option value=true>true</option>\n"
                html += "<option value=false selected='selected'>false</option>\n"
                html += "</select><br>\n"
            else:
                if not instance_div:
                    html += f'<div id="{key}_entries">'
                    instance_div = True
                html += f'<label for="{key}_{subkey}">{subkey}: </label>\n'
                html += f'<input type="text" id="{key}_{subkey}" name="{key}_{subkey}"'
                html += f'value="{value[subkey]}">'
                html += "<br>\n"
        html += "</div>"
        html += "</div>"
        writer.write(html)
        await writer.drain()
    html = """
                <button type="submit">Submit</button>
            </form>
        <script src=script.js></script>
        </body>
    </html>
    """
    writer.write(html)
    await writer.drain()


def ordered_config() -> OrderedDict:
    """Returns the config as an OrderedDict to ensure configs remain in the expected order
    This is needed because unlike Python3.7+ dict loading order is not maintained in micropython

    Returns:
        OrderedDict: Config object with the order ensured
    """
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = config_file.read()

    config = config.replace("\n", "")
    config = config.strip("{").strip("}").strip()
    config_list = []
    for line in config.split("},"):
        config_list.append(line.strip())

    full_dict = []
    for config_items in config_list:
        if "{" in config_items:
            nested_dict = []
            nested = config_items.split("{")
            items = nested[1].split(",")
            for item in items:
                values = item.strip().replace('"', "").split(":")
                value = values[1].strip()
                # convert strings back to the correct data type
                if value.isdigit():
                    nested_dict.append((values[0], int(values[1].strip())))
                elif "false" in value:
                    nested_dict.append((values[0], False))
                elif "true" in value:
                    nested_dict.append((values[0], True))
                else:
                    nested_dict.append((values[0], values[1].strip()))
            sub_dict = OrderedDict(nested_dict)
            full_dict.append((nested[0].strip().strip(":").replace('"', ""), sub_dict))
        else:
            items = config_items.split(":")
            full_dict.append((items[0].strip().replace('"', ""), items[1].strip().replace('"', "")))
    final_dict = OrderedDict(full_dict)
    return final_dict


def prettify_string(raw_str: str) -> str:
    """Takes a dictionary dumped to a string via json.dumps and adds indents and new lines for
    human readability

    This is needed in micropython as json.dumps doesn't have an indent argument

    Args:
        raw_str (str): string representation of a dictionary

    Returns:
        str: string representation of a dictionary "pretty printed"
    """
    indent = 0
    strings = [string + "{" for string in raw_str.split("{")]
    split_strings = []
    for string in strings:
        if "}," in string:
            closing = string.split("},")
            split_strings.append(closing[0] + "},")
            split_strings.append(closing[1])
        else:
            split_strings.append(string)
    fully_split_strings = []
    for string in split_strings:
        if "," in string:
            items = string.split(",")
            for item in items:
                fully_split_strings.append(f"{item},")
        else:
            fully_split_strings.append(string)
    pretty_string = ""
    for line in fully_split_strings:
        if "{" in line:
            pretty_string += f"{' '*indent}{line.strip()}\n".replace(
                "},", f"\n{' '*(indent - 4)}" + "},"
            )
            indent += 4
        elif "}" in line:
            pretty_string += f"{' '*indent}{line.strip()}\n".replace(
                "},", f"\n{' '*(indent - 4)}" + "},"
            )
            indent -= 4
        else:
            pretty_string += f"{' '*indent}{line.strip()}\n".replace(
                "},", f"\n{' '*(indent - 4)}" + "},"
            )
    pretty_string = pretty_string.replace("\n    ,", "")
    pretty_string = pretty_string.replace("}}{,", "\n    }\n}")
    return pretty_string


def updated_settings_html() -> str:
    """Create a page to report that the settings have been updated

    Returns:
        str: HTML page reporting settings saved successfully
    """
    html = html_head()
    html += """
            <body>
                <h1>Updated Configs Saved</h1>
                <div>System will now restart to apply updates</div>
            </body>
        </html>
    """
    return html


def write_settings(settings: str) -> str:
    """Parse and save updated config

    Args:
        settings (str): URL Encoded settings dictionary from update page

    Returns:
        str: HTML page reporting settings saved successfully
    """
    setting_list: list[tuple[str, str]] = []
    # First split the URL encoded POST data with the "&" seperator
    setting_fields = settings.split("&")
    # The nested dicts were flattened by the html to key_subkey. This will unsplit that
    for setting in setting_fields:
        setting_type, setting_value = setting.split("_", 1)
        setting_list.append((setting_type, setting_value))
    # For each subkey split it on the key value pair with the "=" seperator
    # Also ensures it is back to the correct type from all strings
    setting_list_values: list[tuple[str, tuple[str, str | int]]] = []
    print(setting_list_values)
    for setting_tuple in setting_list:
        setting_type, setting_value = setting_tuple[1].split("=")
        if setting_value.isdigit():
            setting_list_values.append(
                (setting_tuple[0], (setting_type.strip("+"), int(setting_value)))
            )
        elif setting_value == "true":
            setting_list_values.append((setting_tuple[0], (setting_type.strip("+"), True)))
        elif setting_value == "false":
            setting_list_values.append((setting_tuple[0], (setting_type.strip("+"), False)))
        else:
            setting_list_values.append(
                (setting_tuple[0], (setting_type.strip("+"), url_unencode(setting_value)))
            )
    # Now that everything is properly split, need to combine them to load into an ordered dict
    setting_list_condensed: list[tuple[str, list[tuple[str, str | int]]]] = []
    for setting_exploded in setting_list_values:
        for setting_item in setting_list_condensed:
            if setting_item[0] in setting_exploded[0]:
                setting_item[1].append(setting_exploded[1])
                break
        else:
            setting_list_condensed.append((setting_exploded[0], [setting_exploded[1]]))
    # Load the now parsed data into OrderedDicts
    setting_list_dicts: list[tuple[str, dict[str, str | int]]] = []
    for setting_final in setting_list_condensed:
        setting_list_dicts.append((setting_final[0], OrderedDict(setting_final[1])))
    # Make the string look like a pretty printed JSON, micropython doesn't support json.dump or
    # json.dumps specifying the indentation. Mostly for human readability no impact on loading
    final_config = prettify_string(json.dumps(OrderedDict(setting_list_dicts)))
    print(final_config)
    # Finally can write the new settings to the config file
    with open("config.json", "w", encoding="utf-8") as config_file:
        config_file.write(final_config.strip())

    return updated_settings_html()
