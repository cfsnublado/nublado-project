import argparse
import json
import os
import sys

import requests

from base import get_user_auth_token

"""
Usage: import_entries.py [-h] [--localhost] entries

Required:
    entries: path to vocab entries file(s). If it's a directory, the json files in it are processed.

Options:
    --localhost: if provided, the localhost api is called. Otherwise, the production api is called.
"""


def import_entries_json(token, filename):
    with open(filename) as json_file:
        json_data = json.load(json_file)
    headers = {"Authorization": "token {0}".format(token)}
    requests.post(vocab_entries_import_url, headers=headers, json=json_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import vocab entries json data.")
    parser.add_argument("--localhost", help="request from Nublado localhost", action="store_true")
    parser.add_argument("entries", help="vocab entries file or directory")
    args = parser.parse_args()
    localhost_base = "http://127.0.0.1:8000"
    host_base = "http://cfsnublado.herokuapp.com"
    token_path = "api/api-token-auth/"
    entries_path = "api/vocab/entries/import/"

    if args.localhost:
        token_url = "{0}/{1}".format(localhost_base, token_path)
        vocab_entries_import_url = "{0}/{1}".format(localhost_base, entries_path)
    else:
        token_url = "{0}/{1}".format(host_base, token_path)
        vocab_entries_import_url = "{0}/{1}".format(host_base, entries_path)

    token = get_user_auth_token(token_url)

    if token:
        if os.path.isfile(args.entries):
            import_entries_json(token, args.entries)
        elif os.path.isdir(args.entries):
            for root, dirs, files in os.walk(args.entries):
                for file in files:
                    import_entries_json(token, os.path.join(root, file))
    else:
        sys.exit("Invalid login.")
