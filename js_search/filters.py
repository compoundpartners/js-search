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
    ADDITIONAL_EXCLUDE,
    TYPES,
    FILTER_EMPTY_LABELS,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company


class SearchFilters(django_filters.FilterSet):
    q = django_filters.CharFilter(label='Search the directory')
    type = django_filters.ChoiceFilter(label='Type', widget=forms.RadioSelect())
    service = django_filters.ModelChoiceFilter(label='Service', queryset=Service.objects.published().exclude(**ADDITIONAL_EXCLUDE.get('service', {})).order_by('translations__title'))
    category = django_filters.ModelChoiceFilter(label='Category', queryset=Category.objects.exclude(**ADDITIONAL_EXCLUDE.get('category', {})).order_by('translations__name'))

    class Meta:
        fields = ['q', 'type', 'service', 'category', ]

    def __init__(self, values, *args, **kwargs):
        super(SearchFilters, self).__init__(values, *args, **kwargs)
        self.filters['type'].extra.update({'choices': TYPES, 'empty_label': FILTER_EMPTY_LABELS.get('type','by type')})
        self.filters['service'].extra.update({'empty_label': FILTER_EMPTY_LABELS.get('service','by service')})
        self.filters['category'].extra.update({'empty_label': FILTER_EMPTY_LABELS.get('category','by category')})
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='Company', queryset=Company.objects.exclude(**ADDITIONAL_EXCLUDE.get('company', {})).order_by('name'))
            self.filters['company'].extra.update({'empty_label': FILTER_EMPTY_LABELS.get('company','by company')})
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().exclude(**ADDITIONAL_EXCLUDE.get(category[0], {})).order_by('translations__name') if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % FILTER_EMPTY_LABELS.get(name, category[1])})

