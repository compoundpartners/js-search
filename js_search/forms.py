# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.text import slugify
from . import models
from .constants import (
    TYPES,
    PLUGIN_LAYOUTS,
)

PLUGIN_LAYOUT_CHOICES = PLUGIN_LAYOUTS
if len(PLUGIN_LAYOUT_CHOICES) == 0 or len(PLUGIN_LAYOUT_CHOICES[0]) != 2:
    PLUGIN_LAYOUT_CHOICES = zip(list(map(lambda s: slugify(s).replace('-', '_'), ('',) + PLUGIN_LAYOUTS)), ('default',) + PLUGIN_LAYOUTS)


class SearchFieldForm(forms.ModelForm):

    layout = forms.ChoiceField(choices=PLUGIN_LAYOUT_CHOICES, required=False)
    results_type = forms.ChoiceField(choices=(('', 'All'),) + TYPES, required=False)

    #def __init__(self, *args, **kwargs):
        #super(SearchFieldForm, self).__init__(*args, **kwargs)
        #if len(PLUGIN_LAYOUTS) == 0:
            #self.fields['layout'].widget = forms.HiddenInput()

    class Meta:
        model = models.SearchField
        fields = '__all__'

