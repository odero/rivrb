from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from .views import HomeView

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
)
