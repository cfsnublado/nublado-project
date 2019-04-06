from django.db import models

from core.models import (
    LanguageModel, ParentModel, PublishModel,
    TimestampModel, TranslationModel, UserstampModel,
    UUIDModel
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


class TestLanguageModel(BaseTestModel, LanguageModel):

    class Meta:
        db_table = "core_tests_testlanguagemodel"


class TestParentModel(BaseTestModel, ParentModel):
    pass


class TestPublishModel(BaseTestModel, PublishModel):
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
