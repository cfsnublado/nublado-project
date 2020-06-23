import json

import requests
import dropbox
from dropbox.files import WriteMode

from .conf import settings

FILES_ENDPOINT = settings.DBX["FILES_ENDPOINT"]


def get_dbx_object(dbx_token):
    dbx = dropbox.Dropbox(dbx_token)

    return dbx


def get_dbx_shared_link(dbx, path, short_url=False, pending_upload=None):
    shared_link = dbx.sharing_create_shared_link(
        path=path,
        short_url=short_url,
        pending_upload=pending_upload
    )

    return shared_link


def upload_file_to_dbx(dbx, local_filepath, dbx_filepath):
    with open(local_filepath, "rb") as upload_file:
        file_data = dbx.files_upload(
            upload_file.read(),
            dbx_filepath,
            mode=WriteMode("overwrite")
        )
        file_metadata = {
            "id": file_data.id,
            "name": file_data.name,
            "path_lower": file_data.path_lower,
            "path_display": file_data.path_display,
            "media_info": file_data.media_info
        }

        return file_metadata


def get_dbx_files(dbx, rel_path=""):
    files = dbx.files_list_folder(rel_path)

    return files.entries


def get_dbx_files_json(dbx_token, rel_path=""):
    """
    Note: leave rel_path blank for root level, and prepend "/" for subfolders.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(dbx_token),
    }
    data = {
        "path": rel_path,
    }
    r = requests.post(
        FILES_ENDPOINT,
        headers=headers,
        data=json.dumps(data)
    )
    results = r.json()

    if "entries" not in results:
        results["entries"] = []

    return results["entries"]


def get_user_dbx_files(dbx, user_id):
    user_dir = "/{}".format(user_id)
    files = get_dbx_files(dbx, rel_path=user_dir)

    return files


def get_user_dbx_files_json(dbx, user_id):
    user_dir = "/{}".format(user_id)
    files = get_dbx_files_json(dbx, rel_path=user_dir)

    return files
