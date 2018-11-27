from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from security.conf import SecurityConf
from users.conf import ProfileConf

SECURITY_URL_PREFIX = SecurityConf.URL_PREFIX
USER_URL_PREFIX = ProfileConf.URL_PREFIX

urlpatterns = i18n_patterns(
    path('', include('core.urls', namespace='core')),
    path('', include('app.urls')),
    path("api/", include("app.api.urls", namespace="api")),
    path('djangoadmin/', admin.site.urls),
    path('{0}/'.format(SECURITY_URL_PREFIX), include('security.urls', namespace='security')),
    path('{0}/'.format(USER_URL_PREFIX), include('users.urls', namespace='users')),
    prefix_default_language=False
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
