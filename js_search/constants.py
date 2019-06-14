# -*- coding: utf-8 -*-

from django.conf import settings

ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'SEARCH_ADD_FILTERED_CATEGORIES',
    [],
)
TYPES = getattr(
    settings,
    'SEARCH_TYPES',
    (('article', 'Article'),
    ('person', 'Person'),
    ('event', 'Event'),
    ('service','Service'))
)
try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
