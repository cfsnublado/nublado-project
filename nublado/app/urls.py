from django.urls import path

from .views import (
    AppSessionView, HomeView
)

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('app-session/', AppSessionView.as_view(), name='app_session'),

]
