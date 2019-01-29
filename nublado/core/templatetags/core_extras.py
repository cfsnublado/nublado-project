import json

from urlobject import URLObject

from django.urls import Resolver404, resolve, reverse
from django.template import Library
from django.utils.translation import activate, get_language

from ..utils import markdown_to_html

register = Library()


@register.simple_tag()
def alias(obj):
    '''
    Alias Tag
    '''
    return obj


@register.simple_tag(takes_context=True)
def change_language(context, language=None, *args, **kwargs):
    '''
    Get active page's url by a specified language.
    Usage: {% change_lang 'en' %}
    '''

    path = context['request'].path
    try:
        url_parts = resolve(path)
    except Resolver404:
        return None
    url = path
    current_language = get_language()
    try:
        activate(language)
        url = reverse(url_parts.view_name, kwargs=url_parts.kwargs)
    finally:
        activate(current_language)

    return '%s' % url


@register.simple_tag(takes_context=True)
def url_set_param(context, url=None, **kwargs):
    '''
    Sets url query pararmeter.

    url: url name , or current url if None
    '''

    if url is not None:
        url = URLObject(reverse(url))
    else:
        url = URLObject(context.request.get_full_path())
    path = url.path
    query = url.query
    for k, v in kwargs.items():
        query = query.set_param(k, v)
    return '{}?{}'.format(path, query)


@register.filter
def to_html(text, strip_outer=False):
    return markdown_to_html(text, strip_outer_tags=strip_outer)


@register.filter
def strconcat(arg1, arg2):
    '''concatenate arg1 & arg2'''
    return '{0}{1}'.format(str(arg1), str(arg2))


@register.filter
def jsonify(arg):
    return json.dumps(arg)
