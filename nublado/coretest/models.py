from django.conf import settings
from django.db import models

from core.models import (
    AccessModel, LanguageModel, ParentModel,
    ProjectModel, ProjectContentModel, ProjectMemberModel,
    ProjectPublishMemberModel, TimestampModel, TrackedFieldModel,
    TranslationModel, UserstampModel, UUIDModel
)

# These models are only used for testing purposes. They are to be migrated only into the test db.


class BaseTestModel(models.Model):
    name = models.CharField(
        max_length=100,
        default="hello",
    )

    class Meta:
        abstract = True


class TestModel(BaseTestModel):
    pass


class TestColorModel(BaseTestModel):
    RED = 1
    BLUE = 2
    GREEN = 3

    COLOR_CHOICES = (
        (RED, "Red"),
        (BLUE, "Blue"),
        (GREEN, "Green")
    )

    color = models.IntegerField(
        choices=COLOR_CHOICES,
        default=GREEN
    )


class TestAccessModel(BaseTestModel, AccessModel):
    pass


class TestTrackedFieldModel(BaseTestModel, TrackedFieldModel):
    tracked_fields = ["name"]


class TestLanguageModel(BaseTestModel, LanguageModel):

    class Meta:
        db_table = "core_tests_testlanguagemodel"


class TestParentModel(BaseTestModel, ParentModel):
    pass


class TestTimestampModel(BaseTestModel, TimestampModel):
    pass


class TestTranslationModel(BaseTestModel, TranslationModel):
    @property
    def translations(self):
        return self.coretest_testtranslationmodel_children


class TestUserstampModel(BaseTestModel, UserstampModel):

    def get_absolute_url(self):
        return "/"


class TestUUIDModel(BaseTestModel, UUIDModel):
    pass


class TestProjectModel(ProjectModel):
    pass


class TestProjectMemberModel(ProjectMemberModel):
    project = models.ForeignKey(
        TestProjectModel,
        related_name='project_members',
        on_delete=models.CASCADE
    )


class TestProjectPublishMemberModel(ProjectPublishMemberModel):
    project = models.ForeignKey(
        TestProjectModel,
        related_name='project_publish_members',
        on_delete=models.CASCADE
    )


class TestProjectContentModel(BaseTestModel, ProjectContentModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s',
        on_delete=models.CASCADE
    )
    content = models.TextField(
        verbose_name='content',
    )

    def get_project(self):
        return 'foo'
