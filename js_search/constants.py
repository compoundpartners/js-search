# -*- coding: utf-8 -*-

from django.conf import settings

ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'SEARCH_ADD_FILTERED_CATEGORIES',
    [],
)
ADDITIONAL_EXCLUDE = getattr(
    settings,
    'SEARCH_ADDITIONAL_EXCLUDE',
    {},
)
TYPES = getattr(
    settings,
    'SEARCH_TYPES',
    (('article', 'Article'),
    ('person', 'Person'),
    ('event', 'Event'),
    ('service','Service'))
)
FILTER_EMPTY_LABELS = getattr(
    settings,
    'SEARCH_FILTER_EMPTY_LABELS',
    {}
)
try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
