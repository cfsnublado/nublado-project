from collections import defaultdict
from random import choice
from string import ascii_lowercase, digits
import logging
import mimetypes
import os
import re
import shutil
import markdown2

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.core.files.base import File
from django.core.serializers.json import DjangoJSONEncoder
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.functional import Promise, keep_lazy
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger('django')


def str_to_bool(value):
    if value == 'False' or value == 'false' or value == '0' or value == 0:
        value = False
    elif value == 'True' or value == 'true' or value == '1' or value == 1:
        value = True
    else:
        value = None
    return value


def get_group_by_dict(list_queryset, group_by_attr):
    '''
    Returns a dictionary of lists of objects,  indexed by a grouped attribute value.
    Note: I don't like looping through the whole queryset to produce the dict.

    list_queryset: queryset of objects
    group_by_attr: attritbute of object to be grouped by

    Example: Model Foo with attribute 'color'

    get_group_by_dict(Foo.objects.all(), 'color')

    {
        blue: [object1, object2, object3],
        red: [object4, object5]
    }
    '''

    objects = list_queryset
    group_by_dict = defaultdict(list)

    for obj in objects:
        group_by_dict[getattr(obj, group_by_attr)].append(obj)

    return group_by_dict


def get_mimetype(filename):
    mimetype = mimetypes.guess_type(filename)
    return mimetype[0]


def print_color(color_code, text):
    '''
    Prints in color to the console according to the integer color code.

    color codes:
        91: red
        92: green
        93: yellow
        94: light purple
        95: purple
        96: cyan
        97: light gray
        98: black
    '''
    print('\033[{0}m {1}\033[00m'.format(color_code, text))


def setup_test_view(view, request, *args, **kwargs):
    '''
    view - CBV instance
    request - RequestFactory request
    '''
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class FuzzyInt(int):
    '''A fuzzy integer between two integers, inclusive. Useful for testing.
    Example: FuzzyInt(5, 8) A value between 5 and 8, inclusive.
    '''
    def __new__(cls, lowest, highest):
        obj = super(FuzzyInt, cls).__new__(cls, highest)
        obj.lowest = lowest
        obj.highest = highest
        return obj

    def __eq__(self, other):
        return other >= self.lowest and other <= self.highest

    def __repr__(self):
        return '[%d..%d]' % (self.lowest, self.highest)


# Application utilities
@keep_lazy(str)
def format_lazy(string, *args, **kwargs):
    return string.format(*args, **kwargs)


def generate_random_username(length=16, chars=ascii_lowercase + digits, split=4, delimiter='-'):
    from users.models import User

    username = ''.join([choice(chars) for i in range(length)])
    if split:
        username = delimiter.join([username[start:start + split] for start in range(0, len(username), split)])
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username


def markdown_to_html(text, strip_outer_tags=False, extras=['fenced-code-blocks']):
    if not text:
        return ''
    html = markdown2.markdown(text, extras=extras)
    if strip_outer_tags:
        html = strip_outer_html_tags(html)
    return html


def save_text_to_file(filename=None, path=None, content=None):
    if path is None:
        path = settings.MEDIA_ROOT
    if filename is None:
        raise ValueError('Filename required.')
    full_path = os.path.join(path, filename)
    f = open(full_path, 'w')
    file = File(f)
    file.write(content)
    file.close()


def strip_markdown_text(text):
    return re.sub('\b(?<!```)(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', text)


def strip_outer_html_tags(s):
    ''' strips outer html tags '''

    start = s.find('>') + 1
    end = len(s) - s[::-1].find('<') - 1
    return s[start:end]


def tag_replace(m):
    return '<span class="tagged-text">{0}</span>'.format(m.group('tagged'))


def tag_text(tags, text):
    search_str = '(?:(?<=\\W)|(?<=_)|(?<=^))(?P<tagged>{0})(?:(?=\\W)|(?=_)|(?=$))'
    for tag in tags:
        match = search_str.format(tag)
        text = re.sub(match, tag_replace, text, flags=re.IGNORECASE)
    return text


def combine_chunks(total_parts, total_size, source_folder, dest):
    ''' Combine a chunked file into a whole file again. Goes through each part
    , in order, and appends that part's bytes to another destination file.

    Chunks are stored in media/chunks
    Uploads are saved in media/uploads
    '''

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in xrange(total_parts):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())


def save_upload(f, path):
    ''' Save an upload. Django will automatically 'chunk' incoming files
    (even when previously chunked by fine-uploader) to prevent large files
    from taking up your server's memory. If Django has chunked the file, then
    write the chunks, otherwise, save as you would normally save a file in
    Python. Uploads are stored in settings.UPLOAD_DIRECTORY
    '''
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        if hasattr(f, 'multiple_chunks') and f.multiple_chunks():
            for chunk in f.chunks():
                destination.write(chunk)
        else:
            destination.write(f.read())


def handle_deleted_file(uuid):
    '''Handles a filesystem delete based on UUID.'''

    logger.info(uuid)
    loc = os.path.join(settings.UPLOAD_DIRECTORY, uuid)
    shutil.rmtree(loc)


def send_user_token_email(
    user=None,
    request=None,
    subject_template_name=None,
    from_email=None,  # settings.EMAIL_HOST_USER,
    email_template_name=None,
    html_email_template_name=None,
    token_generator=default_token_generator,
    site_name=None,
    site_url=None,
    extra_email_context=None
):
    '''Sends an email to a user with a uid/token link to reset password.

    user - existing user in db
    request - request from view where function is called
    subject_template_name - text file containing the email subject
    from_email - email address of sender
    email_template_name - template containing email body
    html_email_template - html-formatted template to display email_template
    token_generator - generate token based on user
    site name - name of project
    site_url - main project url
    extra_email_context - dict containing extra email context variables
    '''
    if not user or not request or not subject_template_name or not email_template_name:
        pass
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    token_url = request.build_absolute_uri(
        reverse(
            'users:user_forgot_password_reset',
            kwargs={'uidb64': uid, 'token': token}
        )
    )
    if site_name is None:
        if hasattr(settings, 'PROJECT_NAME'):
            site_name = settings.PROJECT_NAME
    if site_url is None:
        if hasattr(settings, 'PROJECT_HOME_URL'):
            site_url = request.build_absolute_uri(reverse(settings.PROJECT_HOME_URL))
        else:
            site_url = request.build_absolute_uri('/')
    else:
        site_url = request.build_absolute_uri(reverse(site_url))
    context = {
        'request': request,
        'username': user,
        'site_url': site_url,
        'site_name': site_name,
        'token_url': token_url
    }
    if extra_email_context is not None:
        context.update(extra_email_context)

    '''
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
     '''
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)
    email_message = EmailMultiAlternatives(subject, body, from_email, [user.email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)
