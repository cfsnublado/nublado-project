import hashlib
from urllib.parse import urlencode, urljoin

from django import template
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

from ..conf import settings

register = template.Library()

IMG_CIRCLE = "circle"


# @cache_result()
@register.simple_tag
def profile_image_url(user, size=settings.USERS_IMAGE_DEFAULT_SIZE):
    if settings.USERS_USE_GRAVATAR:
        params = {"s": str(size)}

        if settings.USERS_GRAVATAR_DEFAULT:
            params["d"] = settings.USERS_GRAVATAR_DEFAULT

        path = "{0}/?{1}".format(
            hashlib.md5(force_bytes(user.email.lower())).hexdigest(), urlencode(params)
        )

        return urljoin(settings.USERS_GRAVATAR_BASE_URL, path)


@register.simple_tag
def profile_image(
    user,
    size=settings.USERS_IMAGE_DEFAULT_SIZE,
    border_radius=0,
    **kwargs
):
    alt = user.username

    if user.profile.avatar_url:
        url = user.profile.avatar_url
    else:
        url = profile_image_url(user, size)

    if border_radius == IMG_CIRCLE:
        border_radius = int(size / 2)

    image_context = dict(kwargs, **{
        "user": user,
        "url": url,
        "alt": alt,
        "size": size,
        "border_radius": border_radius
    })

    return render_to_string("users/profile_image/profile_image_tag.html", image_context)
