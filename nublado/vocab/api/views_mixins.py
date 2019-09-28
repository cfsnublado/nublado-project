from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class BatchMixin(object):

    @action(methods=["post"], detail=False)
    def create_batch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
