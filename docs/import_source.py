from markdownify import markdownify as md
import argparse
import getpass
import json
import markdown2
import mimetypes
import os
import requests
import sys
from bs4 import BeautifulSoup

"""
Usage: import_source.py [-h] [--localhost] source

Required:
    source: path to vocab source file(s). If it's a directory, the files in its top level are processed.

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


def import_source(token, filename):
    print_color(96, filename)
    with open(filename, "r") as file:
        mimetype = get_mimetype(filename)
        if mimetype == "application/json":
            data = json.load(file)
        elif mimetype == "text/markdown":
            data = convert_markdown_to_dict(file.read())
        else:
            sys.exit("Source file must be json or markdown.")
    headers = {"Authorization": "token {0}".format(token)}
    requests.post(vocab_source_import_url, headers=headers, json=data)


def convert_markdown_to_dict(md_text, display_html=False):
    html = markdown2.markdown(md_text, extras=["metadata", "markdown-in-html"])
    source_data = {}
    project_data = {}

    if "project_name" not in html.metadata:
        raise TypeError("Missing project_name attribute in metadata.")
    project_data["name"] = html.metadata["project_name"]

    if "source_name" not in html.metadata:
        raise TypeError("Missing source_name attribute in metadata.")
    source_data["name"] = html.metadata["source_name"]

    if "source_type" in html.metadata:
        source_data["source_type"] = int(html.metadata["source_type"])

    if "source_description" in html.metadata:
        source_data["description"] = html.metadata["source_description"]

    data_dict = {
        "vocab_project_data": project_data,
        "vocab_source_data": source_data,
        "vocab_contexts": {}
    }
    soup = BeautifulSoup(html, "html.parser")
    lis = soup.ul.find_all("li", recursive=False)
    for num, li in enumerate(lis, start=1):
        data_dict["vocab_contexts"][num] = {
            "vocab_context_data": {},
            "vocab_entries": []
        }
        # Tagged entries
        tagged_vocab = li.find("div", "tagged-entries")
        if tagged_vocab:
            for entry_tag in tagged_vocab.find_all("p", recursive=False):
                # entry: language: tag1, tag2, tag3...
                entry_list = [x.strip() for x in entry_tag.string.split(":")]
                tags = [x.strip() for x in entry_list[2].split(",")]
                data_dict["vocab_contexts"][num]["vocab_entries"].append(
                    {
                        "vocab_entry_data": {
                            "language": entry_list[0],
                            "entry": entry_list[1]
                        },
                        "vocab_entry_tags": tags
                    }
                )
            tagged_vocab.extract()
        li_content = li.decode_contents()

        # Revert li content back to markdown. (Hacky I know).
        data_dict["vocab_contexts"][num]["vocab_context_data"]["content"] = md(li_content)

    if display_html:
        print_color(92, "\n\nSource html")
        print(soup.prettify())

    return data_dict


def get_mimetype(filename):
    mimetype = mimetypes.guess_type(filename)
    return mimetype[0]


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
    parser = argparse.ArgumentParser(description="Import vocab source json data.")
    parser.add_argument("--localhost", help="request from Nublado localhost", action="store_true")
    parser.add_argument("source", help="vocab source file or directory")
    args = parser.parse_args()
    localhost_base = "http://127.0.0.1:8000"
    host_base = "http://cfsnublado.herokuapp.com"
    token_path = "api/api-token-auth/"
    source_path = "api/vocab/source/import/"

    if args.localhost:
        token_url = "{0}/{1}".format(localhost_base, token_path)
        vocab_source_import_url = "{0}/{1}".format(localhost_base, source_path)
    else:
        token_url = "{0}/{1}".format(host_base, token_path)
        vocab_source_import_url = "{0}/{1}".format(host_base, source_path)

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