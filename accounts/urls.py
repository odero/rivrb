from django.conf.urls import patterns, include, url

from django.contrib.auth import views as auth_views
from django.conf import settings

from .views import LogoutView


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', HomeView.as_view(), name='home'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^login/$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),

)
