from rest_framework.permissions import BasePermission


class ReadWritePermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return True


class ReadPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action not in ['retrieve', 'list']:
            return request.user.is_authenticated
        else:
            return True


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class CreatorPermission(BasePermission):
    '''
    Permission granted to object creator or superuser.
    '''

    def has_object_permission(self, request, view, obj):
        user = request.user

        if view.action in ['update', 'partial_update', 'destroy']:
            return self.check_creator_permission(user, obj)
        else:
            return True

        return self.check_creator_permission(user, obj)

    def check_creator_permission(self, user, obj):
        return user.id == obj.creator_id or user.is_superuser


class OwnerPermission(BasePermission):
    '''
    Permission granted to object owner or superuser.
    '''

    def has_object_permission(self, request, view, obj):
        user = request.user

        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return self.check_owner_permission(user, obj)
        else:
            return True

    def check_owner_permission(self, user, obj):
        return user.id == obj.owner_id or user.is_superuser
