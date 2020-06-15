from appconf import AppConf

from django.conf import settings


class DbxConf(AppConf):
    URL_PREFIX = "dbx"
    settings.DBX["FILES_ENDPOINT"] = "https://api.dropboxapi.com/2/files/list_folder"
