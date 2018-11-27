from django.db import models

from core.models import (
    LanguageModel, ParentModel, PublishModel,
    TimestampModel, TranslationModel, UserstampModel,
    UUIDModel
)

# These models are only used for testing purposes. They are to be migrated only into the test db.


class TestModel(models.Model):
    name = models.CharField(
        max_length=100,
        default="hello",
    )

    class Meta:
        abstract = True


class TestLanguageModel(TestModel, LanguageModel):

    class Meta:
        db_table = "core_tests_testlanguagemodel"


class TestParentModel(TestModel, ParentModel):
    pass


class TestPublishModel(TestModel, PublishModel):
    pass


class TestTimestampModel(TestModel, TimestampModel):
    pass


class TestTranslationModel(TestModel, TranslationModel):
    @property
    def translations(self):
        return self.coretest_testtranslationmodel_children


class TestUserstampModel(TestModel, UserstampModel):

    def get_absolute_url(self):
        return "/"


class TestUUIDModel(TestModel, UUIDModel):
    pass
