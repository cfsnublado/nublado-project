import argparse
import getpass
import json
import os
import requests
import sys

"""
Usage: export_entries.py [-h] [--localhost] source

Required:
    export_path: path to export file

Options:
    --localhost: if provided, the localhost api is called. Otherwise, the production api is called.
"""


def print_color(color_code, text):
    """
    Prints in color to the console according to the integer color code.

    color codes:
        91: red
        92: green
        93: yellow
        94: light purple
        95: purple
        96: cyan
        97: light gray
        98: black
    """
    print("\033[{0}m {1}\033[00m".format(color_code, text))


def export_entries(token, output_path):
    file_path = os.path.join(output_path, 'vocab_entries.json')
    print_color(96, file_path)

    with open(file_path, 'w+') as f:
        headers = {
            "Authorization": "token {0}".format(token)
        }
        response = requests.get(export_url, headers=headers)
        json_data = response.json()
        f.write(json.dumps(json_data, indent=2))


def get_user_auth_token(token_url):
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    r = requests.post(
        token_url,
        {"username": username, "password": password}
    )
    token = r.json().get("token", None)
    return token


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export vocab entries json data.")
    parser.add_argument("--localhost", help="request from Nublado localhost", action="store_true")
    parser.add_argument("output_path", help="output path")
    args = parser.parse_args()
    localhost_base = "http://127.0.0.1:8000"
    host_base = "http://cfsnublado.herokuapp.com"
    token_path = "api/api-token-auth/"
    export_path = "api/vocab/entries/export/"

    if args.localhost:
        token_url = "{0}/{1}".format(localhost_base, token_path)
        export_url = "{0}/{1}".format(localhost_base, export_path)
    else:
        token_url = "{0}/{1}".format(host_base, token_path)
        export_url = "{0}/{1}".format(host_base, export_path)

    token = get_user_auth_token(token_url)

    if token:
        export_entries(token, args.output_path)
    else:
        sys.exit("Invalid login.")
