import magic
from dropbox.exceptions import ApiError
from rest_framework import status
from rest_framework.exceptions import APIException, ParseError, UnsupportedMediaType
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from core.api.views_api import APIDefaultsMixin
from ..utils import (
    get_dbx_object, get_dbx_shared_link,
    get_user_dbx_files_json, upload_file_to_dbx
)


def check_in_memory_mime(in_memory_file):
    mime = magic.from_buffer(
        in_memory_file.read(),
        mime=True
    )

    return mime


class DbxSharedLinkView(
    APIDefaultsMixin, APIView
):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        dbx_token = settings.DBX["ACCESS_TOKEN"]
        dbx = get_dbx_object(dbx_token)
        data = request.data

        if "dbx_path" not in data:
            raise ParseError("dbx_path required in post data")

        shared_link = get_dbx_shared_link(dbx, data["dbx_path"])

        return Response(data={"shared_link": shared_link.url}, status=status.HTTP_200_OK)


class DbxUserFilesView(
    APIDefaultsMixin, APIView
):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        dbx_token = settings.DBX["ACCESS_TOKEN"]
        try:
            files = get_user_dbx_files_json(dbx_token, request.user.id)
        except ApiError:
            raise APIException("User directory not found.")

        return Response(data={"files": files}, status=status.HTTP_200_OK)


class DbxDeleteFileView(APIDefaultsMixin, APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        dbx_token = settings.DBX["ACCESS_TOKEN"]
        dbx = get_dbx_object(dbx_token)
        data = request.data

        if "dbx_path" not in data:
            raise ParseError("dbx_path required in post data")

        try:
            metadata = dbx.files_delete(data["dbx_path"])
            file_metadata = {
                "id": metadata.id,
                "name": metadata.name,
                "path_lower": metadata.path_lower,
                "path_display": metadata.path_display,
                "media_info": metadata.media_info
            }

            return Response(data={"file_metadata": file_metadata}, status=status.HTTP_204_NO_CONTENT)
        except ApiError:
            raise APIException("Delete dbx error")


class DbxUploadView(
    APIDefaultsMixin, APIView
):
    permission_classes = [IsAdminUser]
    allowed_mime_types = [
        "text/plain", "text/markdown",
        "application/pdf", "audio/mpeg"
    ]

    def post(self, request, *args, **kwargs):
        dbx_token = settings.DBX["ACCESS_TOKEN"]
        file_metadata = ""

        if "file" not in request.data:
            raise ParseError("Empty content")

        file = request.data["file"]
        mime = check_in_memory_mime(file)

        if mime not in self.allowed_mime_types:
            raise UnsupportedMediaType(mime)

        upload_dir = settings.TMP_DIR
        tmp_filepath = upload_dir / file.name
        # Upload to user subfolder in app identified by user id (UUID)
        dbx_filepath = "/{0}/{1}".format(request.user.id, file.name)

        with open(tmp_filepath, "wb") as tmp_upload_file:
            for chunk in file.chunks():
                tmp_upload_file.write(chunk)

        try:
            dbx = get_dbx_object(dbx_token)
            file_metadata = upload_file_to_dbx(
                dbx,
                tmp_filepath,
                dbx_filepath,
            )
        except ApiError:
            raise APIException("Upload dbx error")

        return Response(
            data={"file_metadata": file_metadata},
            status=status.HTTP_200_OK
        )


class DbxUploadAudioView(DbxUploadView):
    allowed_mime_types = ["audio/mpeg"]
