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

try:
    from custom.js_search.filters import CustomFilterMixin
except:
    class CustomFilterMixin(object):
        pass

class SearchFilters(CustomFilterMixin, django_filters.FilterSet):
    q = django_filters.CharFilter(label='Search the directory')
    type = django_filters.ChoiceFilter(label='Type', empty_label='by type', choices=TYPES, widget=forms.RadioSelect())
    service = django_filters.ModelChoiceFilter(label='Service', empty_label='by service', queryset=Service.objects.published().exclude(**ADDITIONAL_EXCLUDE.get('service', {})))
    category = django_filters.ModelChoiceFilter(label='Category', empty_label='by category', queryset=Category.objects.exclude(**ADDITIONAL_EXCLUDE.get('category', {})))

    class Meta:
        fields = ['q', 'type', 'service', 'category', ]

    def __init__(self, values, *args, **kwargs):
        super(SearchFilters, self).__init__(values, *args, **kwargs)
        selects = ['category', 'service']
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', empty_label='by company', queryset=Company.objects.exclude(**ADDITIONAL_EXCLUDE.get('company', {})).order_by('name'))
            selects.append('company')
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().exclude(**ADDITIONAL_EXCLUDE.get(category[0], {})).order_by('translations__name') if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % category[1]})
                selects.append(name)

        self.set_empty_labels(**FILTER_EMPTY_LABELS)

        for field in selects:
            self.sort_choices(self.filters[field])

    def set_empty_labels(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.filters:
                self.filters[key].extra['empty_label'] = value

    def sort_choices(self, field):
        field = field.field
        if isinstance(field.choices, django_filters.fields.ModelChoiceIterator):
            choices = [(obj.pk, str(obj)) for obj in field.choices.queryset]
            field.iterator = django_filters.fields.ChoiceIterator
            field._set_choices(sorted(choices, key=lambda item: item[1]))


class SearchFilter(django_filters.Filter):
    def filter(self, qs, values):
        values = values or ''
        if len(values) > 0:
            for value in values.strip().split():
                value = value.strip()
                if value:
                    qs = qs.filter(search__search_data__icontains=value)
        return qs

class PageFilters(django_filters.FilterSet):
    q = SearchFilter(label='Search the directory')
