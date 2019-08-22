# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
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


@python_2_unicode_compatible
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


@receiver(post_save, dispatch_uid='page_update_search_data')
def update_search_data(sender, instance, **kwargs):
    is_cms_plugin = issubclass(instance.__class__, CMSPlugin)
    title = None

    if is_cms_plugin:
        placeholder = (getattr(instance, '_placeholder_cache', None) or
                       instance.placeholder)
        if hasattr(placeholder, '_attached_model_cache'):
            if placeholder._attached_model_cache == Page and placeholder.slot == PAGE_PLACEHOLDER:
                page = placeholder.page
                title = page.title_set.get(language=instance.language)
    if instance.__class__ == Title:
        title = instance
    if title:
        if hasattr(title, 'search'):
            search = title.search
        else:
            search = TitleSearch.objects.create(title=title)
        search.search_data = search.get_search_data(instance.language)
        search.save()
