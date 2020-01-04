from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from core.views import home_files, render_js, UploadView

app_name = 'core'

urlpatterns = [
    re_path('(?P<filename>(robots.txt)|(humans.txt)|(googleb7077bd8f7f710c0.html))', home_files, name='home_files'),
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path('upload/', UploadView.as_view(), name='upload_ajax'),
    path('js-settings/', render_js, name='js_settings',),
]
