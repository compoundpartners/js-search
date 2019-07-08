from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import SearchExtension


class SearchExtensionAdmin(PageExtensionAdmin):
    pass

admin.site.register(SearchExtension, SearchExtensionAdmin)
