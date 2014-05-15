from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'retweetit.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('core.urls'), name='core'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + staticfiles_urlpatterns()

urlpatterns += patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social'))
)
