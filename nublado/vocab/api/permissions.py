from rest_framework.permissions import BasePermission


class ReadWritePermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ["create", "update", "partial_update", "destroy"]:
            return request.user.is_authenticated
        else:
            return True


class ReadPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action not in ["retrieve", "list"]:
            return request.user.is_authenticated
        else:
            return True


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class CreatorPermission(BasePermission):
    """
    Permission granted to object creator or superuser.
    """

    superuser_override = True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if view.action not in ["retrieve", "list"]:
            return self.check_creator_permission(user, obj)
        else:
            return True

        return self.check_creator_permission(user, obj)

    def check_creator_permission(self, user, obj):
        if self.superuser_override:
            return user.is_superuser or user.id == obj.creator_id
        else:
            return user.id == obj.creator_id


class SourceCreatorPermission(CreatorPermission):
    pass


class SourceContextCreatorPermission(CreatorPermission):
    def check_creator_permission(self, user, obj):
        if self.superuser_override:
            return user.is_superuser or user.id == obj.vocab_source.creator_id
        else:
            return user.id == obj.vocab_source.creator_id


class SourceContextEntryCreatorPermission(CreatorPermission):
    def check_creator_permission(self, user, obj):
        if self.superuser_override:
            return user.is_superuser or user.id == obj.vocab_context.vocab_source.creator_id
        else:
            return user.id == obj.vocab_context.vocab_source.creator_id
