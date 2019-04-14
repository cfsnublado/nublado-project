# Generated by Django 2.1.7 on 2019-04-14 08:10

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(3, message='validation_username_min_length 3'), django.core.validators.RegexValidator(code='characters', message='validation_username_characters', regex='^[0-9a-z-]*$')], verbose_name='label_username')),
                ('email', models.EmailField(error_messages={'unique': 'validation_email_unique'}, max_length=50, unique=True, validators=[django.core.validators.EmailValidator(code='email', message='validation_email_format')], verbose_name='label_email')),
                ('first_name', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(code='characters', message='validation_user_name_characters', regex='^([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+ ?)+$')], verbose_name='label_first_name')),
                ('last_name', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(code='characters', message='validation_user_name_characters', regex='^([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+ ?)+$')], verbose_name='label_last_name')),
                ('is_active', models.BooleanField(default=False, verbose_name='label_is_active')),
                ('is_admin', models.BooleanField(default=False, verbose_name='label_is_admin')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='label_user')),
                ('about', models.TextField(blank=True, verbose_name='label_profile_about')),
            ],
            options={
                'verbose_name': 'label_profile',
                'verbose_name_plural': 'label_profile_plural',
                'ordering': ('user',),
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
