from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib import auth


class LogoutView(RedirectView):
    permanent = False
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        response = super(LogoutView, self).get(request, *args, **kwargs)

        return response
