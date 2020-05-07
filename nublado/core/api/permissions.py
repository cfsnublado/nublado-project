from rest_framework.permissions import BasePermission


class ReadWritePermission(BasePermission):
    write_actions = ['create', 'update', 'partial_update', 'destroy']

    def has_permission(self, request, view):
        if view.action in self.write_actions:
            return request.user.is_authenticated
        else:
            return True


class ReadPermission(BasePermission):
    '''
    Retrieve and list access for non-authenticated user
    '''
    read_actions = ['retrieve', 'list']

    def has_permission(self, request, view):
        if view.action not in self.read_actions:
            return request.user.is_authenticated
        else:
            return True


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser
