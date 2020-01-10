from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from core.serializers import BaseSerializer, UUIDEncoder
from .models import Profile, User
from .validation import (
    email_format, name_characters,
    password_characters, password_min_length,
    username_characters, username_min_length
)


class UserSerializer(BaseSerializer, serializers.HyperlinkedModelSerializer):
    json_encoder = UUIDEncoder
    minimal_data_fields = ["id", "username"]
    id = serializers.UUIDField(),
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail",
        lookup_field="username"
    )
    profile = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:profile-detail",
        lookup_field="username"
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[password_min_length, password_characters],
    )
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "url", "id", "profile", "username", "email", "first_name", "last_name",
            "password", "confirm_password", "date_created", "date_updated"
        )
        read_only_fields = ("url", "id", "date_created", "date_updated")
        write_only_fields = ("password", "confirm_password")

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields["username"].validators = [username_characters, username_min_length]
        self.fields["first_name"].validators = [name_characters]
        self.fields["last_name"].validators = [name_characters]
        self.fields["email"].validators = [email_format]
        if not self.instance:
            self.fields["password"].required = True

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        # Password has been validated and confirmed
        password = validated_data.get("password", None)

        if password:
            instance.set_password(password)

        instance.save()

        return instance

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.pop("confirm_password", None)

        if password and password != confirm_password:
            raise serializers.ValidationError({"confirm_password": _("validation_password_match")})

        return data


class ProfileSerializer(BaseSerializer, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:profile-detail",
        lookup_field="username"
    )
    user = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="api:user-detail",
        lookup_field="username"
    )

    class Meta:
        model = Profile
        fields = (
            "url", "user", "about", "avatar_url", "date_created", "date_updated"
        )
        read_only_fields = ("url", "date_created", "date_updated")
