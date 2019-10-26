import argparse
import json
import os
import sys

import requests

from base import get_mimetype, get_user_auth_token, print_color


'''
Usage: import_source.py [--localhost] source

Required:
    source: path to vocab source file or directory

Options:
    --localhost: if provided, the localhost api is called. Otherwise, the production api is called.
'''

LOCALHOST = "http://127.0.0.1:8000"
PRODUCTION_HOST = "http://cfsnublado.herokuapp.com"
TOKEN_PATH = "api/api-token-auth/"
IMPORT_PATH = "api/vocab/source/import/"
IMPORT_MD_PATH = "api/vocab/source/import/markdown/"


def import_source(token, filename):
    print_color(96, filename)
    with open(filename, "r") as file:
        mimetype = get_mimetype(filename)
        if mimetype == "application/json":
            data = json.load(file)
        elif mimetype == "text/markdown":
            data = file.read()
        else:
            sys.exit("Source file must be json or markdown.")
    headers = {"Authorization": "token {0}".format(token)}
    requests.post(vocab_source_import_url, headers=headers, json=data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import vocab source json data.")
    parser.add_argument("--localhost", help="request from Nublado localhost", action="store_true")
    parser.add_argument("source", help="vocab source file or directory")
    args = parser.parse_args()

    if args.localhost:
        token_url = "{0}/{1}".format(LOCALHOST, TOKEN_PATH)
        vocab_source_import_url = "{0}/{1}".format(LOCALHOST, IMPORT_MD_PATH)
    else:
        token_url = "{0}/{1}".format(PRODUCTION_HOST, TOKEN_PATH)
        vocab_source_import_url = "{0}/{1}".format(PRODUCTION_HOST, IMPORT_MD_PATH)

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
