from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from .views import HomeView, DeleteTopicView

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^delete/(?P<topic_id>\d+)/$', DeleteTopicView.as_view(), name='delete_topic'),
)
