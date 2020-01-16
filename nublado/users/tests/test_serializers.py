import json

from rest_framework.reverse import reverse as drf_reverse

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase

from ..models import User
from ..serializers import UserSerializer, ProfileSerializer


class ProfileSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs",
            email="cfs@cfs.com",
            first_name="Christopher",
            last_name="Sanders",
            password="Pizza?69p"
        )
        self.profile = self.user.profile
        self.profile_data = {
            "about": "Hello there. I am {0}.".format(self.user.first_name)
        }

    def test_serialized_data(self):
        request = self.client.get(reverse("api:profile-list")).wsgi_request
        serializer = ProfileSerializer(self.profile, context={"request": request})
        expected_data = {
            "url": drf_reverse("api:profile-detail", kwargs={"username": self.user.username}, request=request),
            "about": self.profile.about,
            "avatar_url": self.profile.avatar_url,
            "date_created": self.profile.date_created.isoformat(),
            "date_updated": self.profile.date_updated.isoformat(),
            "user": drf_reverse("api:user-detail", kwargs={"username": self.user.username}, request=request),
        }
        self.assertEqual(expected_data, serializer.data)

    def test_json_data(self):
        request = self.client.get(reverse("api:profile-list")).wsgi_request
        serializer = ProfileSerializer(self.profile, context={"request": request})
        expected_json_data = json.dumps({
            "url": drf_reverse("api:profile-detail", kwargs={"username": self.user.username}, request=request),
            "about": self.profile.about,
            "avatar_url": self.profile.avatar_url,
            "date_created": self.profile.date_created.isoformat(),
            "date_updated": self.profile.date_updated.isoformat(),
            "user": drf_reverse("api:user-detail", kwargs={"username": self.user.username}, request=request),
        })
        json_data = serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))


class UserSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs",
            email="cfs@cfs.com",
            first_name="Christopher",
            last_name="Sanders",
            password="Pizza?69p"
        )
        self.user_data = {
            "username": "ale7",
            "email": "ale7@ale.com",
            "first_name": "Alejandra",
            "last_name": "Acosta",
            "password": "Coffee?69c",
            "confirm_password": "Coffee?69c"
        }

    def test_minimal_data_fields(self):
        request = self.client.get(reverse("api:user-list")).wsgi_request
        serializer = UserSerializer(self.user, context={"request": request})
        expected_minimal_data = ["id", "username"]
        self.assertCountEqual(expected_minimal_data, serializer.minimal_data_fields)

    def test_serialized_data(self):
        request = self.client.get(reverse("api:user-list")).wsgi_request
        serializer = UserSerializer(self.user, context={"request": request})
        expected_data = {
            "url": drf_reverse("api:user-detail", kwargs={"username": self.user.username}, request=request),
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "date_created": self.user.date_created.isoformat(),
            "date_updated": self.user.date_updated.isoformat(),
            "profile": drf_reverse("api:profile-detail", kwargs={"username": self.user.username}, request=request),
        }
        self.assertEqual(expected_data, serializer.data)

    def test_json_data(self):
        request = self.client.get(reverse("api:user-list")).wsgi_request
        serializer = UserSerializer(self.user, context={"request": request})
        expected_json_data = json.dumps({
            "url": drf_reverse("api:user-detail", kwargs={"username": self.user.username}, request=request),
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "date_created": self.user.date_created.isoformat(),
            "date_updated": self.user.date_updated.isoformat(),
            "profile": drf_reverse("api:profile-detail", kwargs={"username": self.user.username}, request=request),
        })
        json_data = serializer.json_data()
        self.assertEqual(json.loads(expected_json_data), json.loads(json_data))

    def test_create_user(self):
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(User.objects.filter(username=self.user_data["username"]).exists())

    def test_update_user(self):
        serializer = UserSerializer(self.user, data=self.user_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.user.username, self.user_data["username"])
        self.assertEqual(self.user.email, self.user_data["email"])
        self.assertEqual(self.user.first_name, self.user_data["first_name"])
        self.assertEqual(self.user.last_name, self.user_data["last_name"])

    def test_update_user_no_password(self):
        updated_data = {
            "username": "josie7",
            "email": "josie7@josie.com",
            "first_name": "Josie",
            "last_name": "Jagger"
        }
        serializer = UserSerializer(self.user, data=updated_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

    def test_validation_create_no_password(self):
        self.user_data["password"] = ""
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors["password"])

    def test_validation_create_passwords_no_match(self):
        self.user_data["confirm_password"] = "asdf"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["confirm_password"], [_("validation_password_match")])

    def test_validation_password_characters(self):
        self.user_data["password"] = "aAaaAads8"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["password"], [_("validation_password_characters")])

    def test_validation_password_min_length(self):
        self.user_data["password"] = "a@A8"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["password"], ["Password must contain at least 8 characters"])

    def test_validation_no_username(self):
        self.user_data["username"] = ""
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors["username"])

    def test_validation_username_characters(self):
        self.user_data["username"] = "adf!7"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["username"], [_("validation_username_characters")])

    def test_validation_username_min_length(self):
        self.user_data["username"] = "ad"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["username"], [_("validation_username_min_length 3")])

    def test_validation_no_email(self):
        self.user_data["email"] = ""
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors["email"])

    def test_validation_email_format(self):
        self.user_data["email"] = "adf"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["email"], [_("validation_email_format")])

    def test_validation_no_first_name(self):
        self.user_data["first_name"] = ""
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors["first_name"])

    def test_validation_name_characters(self):
        self.user_data["first_name"] = "adf!7"
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["first_name"], [_("validation_user_name_characters")])

    def test_validation_no_last_name(self):
        self.user_data["last_name"] = ""
        serializer = UserSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors["last_name"])
