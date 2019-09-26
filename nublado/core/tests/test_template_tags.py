from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.utils.translation import get_language

User = get_user_model()


class TestCommon(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.pwd = 'Pizza?69p'
        self.user = User.objects.create_user(
            username='cfs',
            first_name='Christopher',
            last_name='Sanders',
            email='cfs7@cfs.com',
            password=self.pwd
        )


class SetUrlParamTest(TestCommon):

    def test_tag_with_no_url(self):
        current_url = '/foo/current/'
        request = self.request_factory.get(current_url)
        context = Context({}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} {% url_set_param foo="cham" language="en" %}')
        rendered = template.render(context)
        self.assertIn('{0}?foo=cham&language=en'.format(current_url), rendered)

    def test_tag_replace_query_paraml(self):
        path = '/foo/list'
        current_url = '{0}?foo=cham&language=en'.format(path)
        param = 'pizza'
        request = self.request_factory.get(current_url)
        context = Context({}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} {% url_set_param foo="pizza" %}')
        rendered = template.render(context)
        self.assertIn('{0}?language=en&foo={1}'.format(path, param), rendered)


class ChangeLanguageTest(TestCommon):

    def test_change_language(self):
        url = '/'
        default_language = 'en'
        changed_language = 'es'
        changed_url = '/{0}{1}'.format(changed_language, url)

        # Change from en to es.
        request = self.request_factory.get(url)
        context = Context({'request': request}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} <a href="{% change_language "es" %}">language</a>')
        rendered = template.render(context)
        self.assertIn('<a href="{0}">language</a>'.format(changed_url), rendered)
        language = get_language()
        self.assertEqual(default_language, language)
        self.client.get(changed_url)
        language = get_language()
        self.assertEqual(changed_language, language)

        # Switch back to en.
        request = self.request_factory.get(changed_url)
        context = Context({'request': request}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} <a href="{% change_language "en" %}">language</a>')
        rendered = template.render(context)
        self.assertIn('<a href="{0}">language</a>'.format(url), rendered)
        self.client.get(url)
        language = get_language()
        self.assertEqual(default_language, language)


class ToUrlTest(TestCommon):

    def test_markdown_to_html(self):
        current_url = '/foo/current/'
        request = self.request_factory.get(current_url)
        context = Context({'markdown_text': '**sample text**'}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} {{ markdown_text|to_html }}')
        rendered = template.render(context)
        self.assertIn('<p><strong>sample text</strong></p>', rendered)


class StrconcatTest(TestCommon):

    def test_concatenate_strings(self):
        current_url = '/foo/current/'
        request = self.request_factory.get(current_url)
        context = Context({'text': 'micro'}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} {{ text|strconcat:"cosm" }}')
        rendered = template.render(context)
        self.assertIn('microcosm', rendered)


class JsonifyTest(TestCommon):

    def test_convert_text_to_json(self):
        current_url = '/foo/current/'
        request = self.request_factory.get(current_url)
        context = Context({'text': 'some text'}, autoescape=False)
        context.request = request
        template = Template('{% load core_extras %} {{ text|jsonify }}')
        rendered = template.render(context)
        self.assertIn('some text', rendered)
