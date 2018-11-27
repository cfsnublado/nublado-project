from rest_framework import serializers

from django.test import TestCase

from ..serializers import BaseSerializer


class TestClass(object):
    def __init__(self, field_1, field_2, field_3):
        self.field_1 = field_1
        self.field_2 = field_2
        self.field_3 = field_3


class TestSerializer(BaseSerializer, serializers.Serializer):
    minimal_data_fields = ['field_1', 'field_2', 'field_3']
    field_1 = serializers.CharField()
    field_2 = serializers.CharField()
    field_3 = serializers.CharField()


class TestBaseSerializerTest(TestCase):
    def setUp(self):
        self.test_obj = TestClass('one', 'two', 'three')
        self.serializer = TestSerializer(self.test_obj)

    def test_minimal_data_fields(self):
        expected_minimal_data = ['field_2', 'field_1', 'field_3']
        self.assertCountEqual(expected_minimal_data, self.serializer.minimal_data_fields)

    def test_get_minimal_data(self):
        expected_minimal_data = {
            'field_2': self.test_obj.field_2,
            'field_3': self.test_obj.field_3,
            'field_1': self.test_obj.field_1
        }
        self.assertEqual(expected_minimal_data, self.serializer.get_minimal_data())
