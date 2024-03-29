# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save

from cms.models import CMSPlugin, Title, Page
from cms.utils.i18n import get_current_language, get_default_language
from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool

from aldryn_newsblog.utils import get_plugin_index_data, get_request, strip_tags

from .constants import PAGE_PLACEHOLDER


class SearchExtension(PageExtension):
    show_on_search = models.BooleanField(_('Show on search'), null=False, default=True)

extension_pool.register(SearchExtension)


class TitleSearch(models.Model):
    title = models.OneToOneField(
        Title,
        on_delete=models.CASCADE,
        related_name='search'
    )
    search_data=models.TextField(blank=True, editable=False)


    def get_search_data(self, request=None):
        """
        Provides an index for use with Haystack, or, for populating
        Event.translations.search_data.
        """
        if not self.pk:
            return ''
        language = self.title.language
        if language is None:
            language = get_current_language()
        if request is None:
            request = get_request(language=language)
        text_bits = []
        placeholder = self.get_placeholder()
        if placeholder:
            plugins = placeholder.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                try:
                    plugin_text_content = ' '.join(
                        get_plugin_index_data(base_plugin, request))
                except:
                    plugin_text_content = ''
                text_bits.append(plugin_text_content)
        text_bits.append(self.title.title)
        text_bits.append(self.title.meta_description or '')
        return ' '.join(text_bits)

    def get_placeholder(self):
        try:
            return self.title.page.placeholders.get(slot=PAGE_PLACEHOLDER)
        except:
            return None

    def save(self, *args, **kwargs):
        self.search_data = self.get_search_data()
        super(TitleSearch, self).save(*args, **kwargs)


class SearchField(CMSPlugin):
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
        null=True,
        blank=True,
    )
    results_type = models.CharField(
        max_length=255,
        verbose_name=_('Results'),
        default='',
        blank=True,
    )
    search_url = models.CharField(
        max_length=255,
        verbose_name=_('Search target URL'),
        default='',
        blank=True,
    )
    layout = models.CharField(
        blank=True,
        default='',
        max_length=60,
        verbose_name=_('layout')
    )

    def __str__(self):
        return self.title or str(self.pk)


@receiver(post_save, dispatch_uid='page_update_search_data')
def update_search_data(sender, instance, **kwargs):
    if instance.__class__ == Title:
        title = instance
        if title:
            if hasattr(title, 'search'):
                search = title.search
            else:
                search = TitleSearch.objects.create(title=title)
            search.search_data = search.get_search_data(instance.language)
            search.save()

