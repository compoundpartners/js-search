# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from .views import SearchView


urlpatterns = [
    url(r'^$', SearchView.as_view(), name='index'),
]
