from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class CreatorPermission(BasePermission):
    '''
    Permission granted to object creator or superuser.
    '''

    def has_object_permission(self, request, view, obj):
        user = request.user
        return self.check_creator_permission(user, obj)

    def check_creator_permission(self, user, obj):
        return user.id == obj.creator_id or user.is_superuser
