# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from . import models, forms

class LayoutMixin():

    def get_layout(self, context, instance, placeholder):
        return instance.layout

    def get_render_template(self, context, instance, placeholder):
        layout = self.get_layout(context, instance, placeholder)
        if layout:
            template = self.TEMPLATE_NAME % layout
            try:
                select_template([template])
                return template
            except TemplateDoesNotExist:
                pass
        return self.render_template

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'placeholder': placeholder,
        })
        return context


@plugin_pool.register_plugin
class SearchFieldPlugin(LayoutMixin, CMSPluginBase):
    module = 'JumpSuite Search'
    TEMPLATE_NAME = 'js_search/plugins/field_%s.html'
    name = _('Search Field')
    model = models.SearchField
    form = forms.SearchFieldForm
    render_template = 'js_search/plugins/field.html'
