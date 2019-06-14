# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.timezone import now
from django import forms
from aldryn_categories.models import Category
from js_services.models import Service
import django_filters

from .constants import (
    IS_THERE_COMPANIES,
    ADD_FILTERED_CATEGORIES,
    TYPES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company


class SearchFilters(django_filters.FilterSet):
    q = django_filters.CharFilter(label='Search the directory')
    type = django_filters.ChoiceFilter(label='type')
    service = django_filters.ModelChoiceFilter(label='service', queryset=Service.objects.published().all().order_by('translations__title'))
    category = django_filters.ModelChoiceFilter(label='category', queryset=Category.objects.all().order_by('translations__name'))

    class Meta:
        fields = ['q', 'type', 'service', 'category', ]

    def __init__(self, values, *args, **kwargs):
        super(SearchFilters, self).__init__(values, *args, **kwargs)
        self.filters['type'].extra.update({'choices': TYPES, 'empty_label': 'by type'})
        self.filters['service'].extra.update({'empty_label': 'by service'})
        self.filters['category'].extra.update({'empty_label': 'by category'})
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', queryset=Company.objects.all().order_by('name'))
            self.filters['company'].extra.update({'empty_label': 'by company'})
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().order_by('translations__name') if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % category[1]})

