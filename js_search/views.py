# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.utils.translation import get_language_from_request
from django.core.paginator import Paginator, Page
from django.utils.functional import cached_property
from django.db.models import Q
from django.utils import timezone

from cms.models import Title
from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin
from django_filters.views import FilterMixin

from aldryn_people.utils import get_valid_languages
from aldryn_people.models import Person
from aldryn_people.filters import PeopleFilters
from aldryn_newsblog.models import Article
from aldryn_newsblog.filters import ArticleFilters
from js_events.models import Event
from js_events.filters import EventFilters
from js_services.models import Service
from js_services.filters import ServiceFilters

from .filters import SearchFilters, PageFilters
from .constants import TYPES
from . import DEFAULT_APP_NAMESPACE


class MixPaginator(Paginator):

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        self.indexes = []
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        object_list = []
        index = 0
        for count in self.counts:
            if bottom > count or top < 1:
                bottom -= count
                top -= count
                index += 1
                object_list.append([])
                continue
            object_list.append(self.object_list[index][max(0,bottom):min(count,top)])
            bottom -= count
            top -= count
            index += 1
        return Page(object_list, number, self)


    @cached_property
    def counts(self):
        counts = []
        for object_list in self.object_list:
            try:
                counts.append(object_list.count())
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                counts.append(len(object_list))
        return counts

    @cached_property
    def count(self):
        return sum(self.counts)


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang


class SearchView(MultipleObjectMixin, TemplateView):
    template_name = 'js_search/index.html'
    paginator_class = MixPaginator
    filters = {
        'title': PageFilters,
        'article': ArticleFilters,
        'person': PeopleFilters,
        'event': EventFilters,
        'service': ServiceFilters,
    }
    paginate_by = 20
    strict = False

    def get_strict(self):
        return self.strict

    def dispatch(self, request, *args, **kwargs):
        self.request_language = get_language(request)
        self.request = request
        self.site_id = getattr(get_current_site(self.request), 'id', None)
        self.valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, self.request_language, self.site_id)
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.qss = {
            'title': Title.objects.public().filter(
                Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
                Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
                Q(redirect__exact='') | Q(redirect__isnull=True),
                language=self.request_language
            ).exclude(page__searchextension__show_on_search=False).select_related('page').distinct(),
            'article': Article.objects.published(),
            'person': Person.objects.published(),
            'event': Event.objects.published(),
            'service': Service.objects.published(),
        }
        self.sorting = {
            'person': getattr(settings, 'ALDRYN_PEOPLE_DEFAULT_SORTING', ('last_name',),),
            'article': ('-publishing_date',),
        }
        requested_type = request.GET.get('type')
        self.object_list = []
        specific_filter = None
        for name, _ in TYPES:
            if not requested_type or requested_type == name:
                order_by = ()
                if requested_type == name:
                    order_by = self.sorting.get(requested_type, order_by)
                filterset = self.filters[name](request.GET or None, queryset=self.qss[name].order_by(*order_by))
                if requested_type == name:
                    specific_filter = filterset
                if not filterset.is_bound:
                    self.object_list.append([])
                elif filterset.is_bound or filterset.is_valid() or not self.get_strict():
                    self.object_list.append(filterset.qs)

        pagination = {
            'pages_start': 10,
            'pages_visible': 2,
        }
        pages_visible_negative = -pagination['pages_visible']
        pagination['pages_visible_negative'] = pages_visible_negative
        pagination['pages_visible_total'] = pagination['pages_visible'] + 1
        pagination['pages_visible_total_negative'] = pages_visible_negative - 1

        context = self.get_context_data(
            filter=SearchFilters(self.request.GET or None, queryset=Title.objects.none()),
            object_list=self.object_list,
            pagination=pagination,
            specific_filter=specific_filter,
        )
        index = 0
        for name, _ in TYPES:
            if not requested_type or requested_type == name:
                context['%s_list' % name] = context['object_list'][index]
                index += 1
        object_list = []
        for objects in context['object_list']:
            object_list += list(objects)
        context['object_list'] = object_list
        return self.render_to_response(context)

