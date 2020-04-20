from rest_framework.permissions import BasePermission


class ReadWritePermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return True


class ReadPermission(BasePermission):
    '''
    Retrieve and list access for non-authenticated user
    '''

    def has_permission(self, request, view):
        if view.action not in ['retrieve', 'list']:
            return request.user.is_authenticated
        else:
            return True


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser
