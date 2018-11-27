import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.urls import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from ..managers import UserManager
from ..models import User as User
from ..models import Profile
from ..serializers import ProfileSerializer, UserSerializer

UserModel = get_user_model()


class UserTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs",
            email="cfs@cfs.com",
            first_name="Christopher",
            last_name="Sanders",
            password="Pizza?69p"
        )
        self.user2 = User.objects.create_user(
            username="kfl7",
            email="kfl@kfl.com",
            first_name="Karen",
            last_name="Fuentes",
            password="Coffee?69p"
        )

    def test_id_is_uuid(self):
        self.assertIsInstance(self.user.id, uuid.UUID)

    def test_pk_is_uuid(self):
        self.assertIsInstance(self.user.pk, uuid.UUID)
        self.assertEqual(self.user.pk, self.user.id)

    def test_set_uuid_on_create(self):
        user_id = uuid.uuid4()
        user = User.objects.create_user(
            id=user_id,
            username="foo7",
            email="foo@foo.com",
            first_name="Foo",
            last_name="Foo",
            password="Coffee?69p"
        )
        self.assertEqual(user.id, user_id)

    def test_get_user_model_returns_correct_user_model(self):
        self.assertEqual(UserModel, User)

    def test_string_representation(self):
        self.assertEqual(str(self.user), "{0} : {1}".format(self.user.email, self.user.get_full_name()))

    def test_manager_type(self):
        self.assertIsInstance(UserModel.objects, UserManager)

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), self.user.first_name)

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "{0} {1}".format(self.user.first_name, self.user.last_name))

    def test_get_serializer(self):
        serializer = self.user.get_serializer()
        self.assertEqual(serializer, UserSerializer)

    def test_get_absolute_url(self):
        url_1 = self.user.get_absolute_url()
        url_2 = reverse("users:profile_view", args=[self.user.username])
        self.assertEquals(url_1, url_2)

    def test_is_staff(self):
        self.user.is_admin = True
        self.assertTrue(self.user.is_staff)
        self.user.is_admin = False
        self.assertFalse(self.user.is_staff)

    # Validation
    def test_validation_setup(self):
        self.user.full_clean()
        self.user2.full_clean()

    def test_validaiton_save_valid_user(self):
        self.user.full_clean()
        self.user.save()

    def test_email_set_to_lower_on_clean(self):
        self.user.email = "FoO@Foo.com"
        self.user.full_clean()
        self.assertEqual("foo@foo.com", self.user.email)

    def test_validation_name_characters(self):
        with self.assertRaisesRegexp(ValidationError, _('validation_user_name_characters')):
            self.user.first_name = "test!  user"
            self.user.full_clean()

    def test_validation_duplicate_username(self):
        with self.assertRaises(ValidationError):
            self.user2.username = self.user.username
            self.user2.full_clean()
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username=self.user.username,
                email="foo7@foo.com",
                first_name="FooFoo",
                last_name="FooFoo",
                password="Coffee?69p"
            )

    def test_validation_email_empty(self):
        with self.assertRaises(ValidationError):
            self.user.email = ""
            self.user.full_clean()

    def test_validation_duplicate_email(self):
        with self.assertRaisesMessage(ValidationError, _('validation_email_unique')):
            self.user2.email = self.user.email
            self.user2.full_clean()
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="foo7",
                email=self.user.email,
                first_name="FooFoo",
                last_name="FooFoo",
                password="Coffee?69p"
            )

    def test_validation_email_format(self):
        with self.assertRaisesMessage(ValidationError, _('validation_email_format')):
            self.user.email = "foofoo"
            self.user.full_clean()


class ProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cfs",
            email="cfs@cfs.com",
            first_name="Christopher",
            last_name="Sanders",
            password="Pizza?69p"
        )
        self.profile = self.user.profile

    def tearDown(self):
        self.user.delete()

    def test_profile_created_and_saved_on_user_create(self):
        self.assertIsInstance(self.profile, Profile)
        # Call the save method of the user to activate the signal
        # again, and check that it doesn"t try to create another
        # profile instance.
        self.user.save()
        self.assertIsInstance(self.user.profile, Profile)
        self.assertEqual(self.profile, self.user.profile)

    def test_string_representation(self):
        self.assertEqual(str(self.profile), str(self.user))

    def test_username(self):
        self.assertEqual(self.profile.username, self.user.username)

    def test_get_serializer(self):
        serializer = self.profile.get_serializer()
        self.assertEqual(serializer, ProfileSerializer)

    def test_get_absolute_url(self):
        url_1 = self.profile.get_absolute_url()
        url_2 = self.user.get_absolute_url()
        self.assertEquals(url_1, url_2)
