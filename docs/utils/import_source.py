import argparse
import json
import os
import sys

import requests

from base import *


"""
Usage: import_source.py [--localhost] source

Required:
    source: path to vocab source file (JSON or Markdown) or directory

Options:
    --localhost: if provided, the localhost api is called. Otherwise, the production api is called.
"""

IMPORT_JSON_PATH = "api/vocab/source/import/"
IMPORT_MD_PATH = "api/vocab/source/import/markdown/"


def import_source(token, filename):
    print_color(96, filename)

    with open(filename, "r") as file:
        mimetype = get_mimetype(filename)

        if mimetype == "application/json":
            data = json.load(file)
            vocab_source_import_url = "{0}/{1}".format(domain, IMPORT_JSON_PATH)
        elif mimetype == "text/markdown":
            data = file.read()
            vocab_source_import_url = "{0}/{1}".format(domain, IMPORT_MD_PATH)
        else:
            sys.exit("Source file must be json or markdown.")

    headers = {"Authorization": "token {0}".format(token)}
    requests.post(vocab_source_import_url, headers=headers, json=data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import vocab source json data.")
    parser.add_argument("--localhost", help="request from Nublado localhost", action="store_true")
    parser.add_argument("source", help="vocab source file or directory")
    args = parser.parse_args()

    if not args.localhost:
        domain = PRODUCTION_HOST

    token_url = "{0}/{1}".format(domain, TOKEN_PATH)
    token = get_user_auth_token(token_url)

    if token:
        if os.path.isfile(args.source):
            import_source(token, args.source)
        elif os.path.isdir(args.source):
            for root, dirs, files in os.walk(args.source):
                for file in files:
                    import_source(token, os.path.join(root, file))
    else:
        sys.exit("Invalid login.")
