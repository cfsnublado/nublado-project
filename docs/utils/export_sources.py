import argparse
import json
import os
import sys

import requests

from base import get_user_auth_token, print_color

'''
Usage: export_sources.py [-h] [--localhost] output_path

Required:
    output_path: path to export files

Options:
    --localhost: if provided, the localhost api is called. Otherwise, the production api is called.
'''


def export_source(token, output_path):
    file_path = os.path.join(output_path, 'vocab_entries.json')
    print_color(96, file_path)

    with open(file_path, 'w+') as f:
        headers = {
            'Authorization': 'token {0}'.format(token)
        }
        response = requests.get(export_url, headers=headers)
        json_data = response.json()
        f.write(json.dumps(json_data, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export vocab entries json data.')
    parser.add_argument('--localhost', help='request from Nublado localhost', action='store_true')
    parser.add_argument('source_id', help='source id')
    parser.add_argument('output_path', help='output path')
    args = parser.parse_args()
    localhost_base = 'http://127.0.0.1:8000'
    host_base = 'http://cfsnublado.herokuapp.com'
    token_path = 'api/api-token-auth/'
    export_path = 'api/vocab/source/{0}/export/'.format(args.source_id)

    if args.localhost:
        token_url = '{0}/{1}'.format(localhost_base, token_path)
        export_url = '{0}/{1}'.format(localhost_base, export_path)
    else:
        token_url = '{0}/{1}'.format(host_base, token_path)
        export_url = '{0}/{1}'.format(host_base, export_path)

    token = get_user_auth_token(token_url)

    if token:
        export_source(token, args.output_path)
    else:
        sys.exit('Invalid login.')
