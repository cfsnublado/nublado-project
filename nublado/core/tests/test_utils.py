from django.conf import settings
from django.core.files.base import File
from django.test import TestCase

from coretest.models import TestColorModel
from ..utils import (
    get_group_by_dict, FuzzyInt, generate_random_username,
    markdown_to_html, save_text_to_file
)


class TestFuzzyInt(TestCase):

    def test_values(self):
        self.assertNotEqual(4, FuzzyInt(5, 8))
        self.assertEqual(5, FuzzyInt(5, 8))
        self.assertEqual(6, FuzzyInt(5, 8))
        self.assertEqual(7, FuzzyInt(5, 8))
        self.assertEqual(8, FuzzyInt(5, 8))
        self.assertNotEqual(9, FuzzyInt(5, 8))


class TestUtilities(TestCase):

    def test_generate_random_username(self):
        username = generate_random_username()
        # Default is a string of 16 characters with - as a delimiter
        # between every group of 4 characters.
        self.assertEqual(len(username), 19)
        self.assertEqual(username.count('-'), 3)
        username = generate_random_username(length=8)
        self.assertEqual(len(username), 9)
        self.assertEqual(username.count('-'), 1)
        # Generate a random username with no delimiter
        username = generate_random_username(length=8, split=0)
        self.assertEqual(len(username), 8)
        self.assertEqual(username.count('-'), 0)
        username = generate_random_username(split=0)
        self.assertEqual(len(username), 16)
        self.assertEqual(username.count('-'), 0)

    def test_markdown_to_html(self):
        # Blank text
        for markdown_text in ['', None]:
            self.assertEqual('', markdown_to_html(markdown_text))
        # Italic
        for markdown_text in ['*testing testing*', '_testing testing_']:
            self.assertEqual(
                '<p><em>testing testing</em></p>\n',
                markdown_to_html(markdown_text)
            )
        # Boldface
        for markdown_text in ['**testing testing**', '__testing testing__']:
            self.assertEqual(
                '<p><strong>testing testing</strong></p>\n',
                markdown_to_html(markdown_text)
            )
        # Boldface italic
        for markdown_text in ['**_testing testing_**', '__*testing testing*__']:
            self.assertEqual(
                '<p><strong><em>testing testing</em></strong></p>\n',
                markdown_to_html(markdown_text)
            )
        # Headers
        html = markdown_to_html('# hello\n## hello')
        self.assertEqual('<h1>hello</h1>\n\n<h2>hello</h2>\n', html)
        # Lists
        for markdown_text in ['- hello\n- hello', '* hello\n* hello']:
            self.assertEqual(
                '<ul>\n<li>hello</li>\n<li>hello</li>\n</ul>\n',
                markdown_to_html(markdown_text)
            )
        # Code blocks
        # Fenced-in code with syntax highlighting
        html = markdown_to_html('```python\nHello\n```')

        self.assertEqual(
            '<div class="codehilite"><pre><span></span><code><span class="n">Hello</span>\n</code></pre></div>\n',
            html
        )
        # Fenced-in code without syntax highlighting
        html = markdown_to_html('```\nHello\n```')
        self.assertEqual(
            '<pre><code>Hello\n</code></pre>\n',
            html
        )
        # Tab-based code block
        html = markdown_to_html('\tHello\n')
        self.assertEqual(
            '<pre><code>Hello\n</code></pre>\n',
            html
        )
        # Links
        # Inline-style link
        html = markdown_to_html('[I am a link](https://www.foo.com)')
        self.assertEqual(
            '<p><a href="https://www.foo.com">I am a link</a></p>\n',
            html
        )
        # Inline-style link with title
        html = markdown_to_html(
            '[I am a link](https://foo.com "Title")'
        )
        self.assertEqual(
            '<p><a href="https://foo.com" title="Title">' +
            'I am a link</a></p>\n',
            html
        )
        # Rerefence-style link with title
        html = markdown_to_html(
            '[I am a link][reference text]\n' +
            '[reference text]:https://foo.com "Title"'
        )
        self.assertEqual(
            '<p><a href="https://foo.com" title="Title">' +
            'I am a link</a></p>\n',
            html
        )
        # Images
        html = markdown_to_html('![alt text](../foo.png "img text")')
        self.assertEqual('<p><img src="../foo.png" alt="alt text" title="img text" /></p>\n', html)
        html = markdown_to_html('![alt text][logo]\n[logo]:../foo.png "img text"')
        self.assertEqual('<p><img src="../foo.png" alt="alt text" title="img text" /></p>\n', html)

    def test_save_text_to_file(self):
        path = settings.TMP_DIR
        filename = 'testing.txt'
        content = 'testing testing'
        full_path = path / filename
        if full_path.exists():
            full_path.unlink()
        self.assertFalse(full_path.exists())
        save_text_to_file(path=path, filename=filename, content=content)
        self.assertTrue(full_path.exists())
        f = open(full_path, 'r')
        file = File(f)
        self.assertEqual(file.read(), content)
        file.close()

    def test_save_text_to_file_no_path(self):
        path = settings.MEDIA_ROOT
        filename = 'testing.txt'
        content = 'testing testing'
        full_path = path / filename
        if full_path.exists():
            full_path.unlink()
        self.assertFalse(full_path.exists())
        save_text_to_file(filename=filename, content=content)
        self.assertTrue(full_path.exists())
        f = open(full_path, 'r')
        file = File(f)
        self.assertEqual(file.read(), content)
        file.close()

    def test_get_group_by_dict(self):
        blue = TestColorModel.objects.create(name='blue', color=TestColorModel.BLUE)
        green = TestColorModel.objects.create(name='green', color=TestColorModel.GREEN)
        red = TestColorModel.objects.create(name='red', color=TestColorModel.RED)
        red_2 = TestColorModel.objects.create(name='red', color=TestColorModel.RED)

        # GRoup by color choice
        results = get_group_by_dict(TestColorModel.objects.all(), 'color')
        expected_results = {
            TestColorModel.GREEN: [green],
            TestColorModel.RED: [red, red_2],
            TestColorModel.BLUE: [blue]
        }

        self.assertEqual(results, expected_results)

        # Group by name
        results = get_group_by_dict(TestColorModel.objects.all(), 'name')
        expected_results = {
            'green': [green],
            'red': [red, red_2],
            'blue': [blue]
        }

        self.assertEqual(results, expected_results)
