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
    (('title', 'Page'),
    ('article', 'Article'),
    ('person', 'Person'),
    ('event', 'Event'),
    ('service','Service'))
)
CONFIGS = getattr(
    settings,
    'SEARCH_CONFIGS',
    (
        ('default', TYPES),
    )
)

CUSTOM_MODULE_NAME = getattr(
    settings,
    'CUSTOM_MODULE_NAME',
    'custom',
)

FILTER_EMPTY_LABELS = getattr(
    settings,
    'SEARCH_FILTER_EMPTY_LABELS',
    {}
)
PAGE_PLACEHOLDER = getattr(
    settings,
    'SEARCH_PAGE_PLACEHOLDER',
    'content'
)
PLUGIN_LAYOUTS = getattr(
    settings,
    'SEARCH_PLUGIN_LAYOUTS',
    (),
)


try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
