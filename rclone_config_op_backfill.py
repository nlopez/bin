#!/usr/bin/env python3
import os
import subprocess
import json

"""
Script to backfill 1Password items with rclone configuration values.
Used in cases where rclone updates things like oauth bearer and refresh tokens.
"""

# Constants
op_vault = "rclone"

# Mapping of JSON paths to op items
config_path_to_op_item = {
    "gdrive_personal_my_drive.token": "gdrive_personal",
    "gdrive_alt_my_drive.token": "gdrive_alt",
    "dropbox_personal.token": "dropbox_personal",
    "dropbox_alt.token": "dropbox_alt",
}

def get_rclone_config():
    """Fetch the rclone configuration as a dictionary."""
    result = subprocess.run(["rclone", "config", "dump"], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def edit_op_item(op_vault, op_item, value):
    """Pass the value as the final positional parameter to `op item edit`."""
    print(f"Editing {op_item} in op vault {op_vault}")
    subprocess.run([
        "op", "item", "--vault", op_vault, "edit", op_item, value
    ], text=True, check=True)

def get_nested_value(data, path):
    """Retrieve a nested value from a dictionary using a dot-separated path."""
    keys = path.split('.')
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return None

def main():
    rclone_config = get_rclone_config()

    for json_path, op_item in config_path_to_op_item.items():
        value_from_config = get_nested_value(rclone_config, json_path)
        op_field_name = json_path.split('.')[-1]
        value_for_op = f"{op_field_name}={value_from_config}" if value_from_config else None

        if value_from_config and value_from_config != "null":
            edit_op_item(op_vault, op_item, value_for_op)
        else:
            print(f"No value found for {json_path}, skipping edit.")

if __name__ == "__main__":
    main()
