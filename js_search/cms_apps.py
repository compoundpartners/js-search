# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from . import DEFAULT_APP_NAMESPACE
from .constants import CONFIGS


class ConfigProxy():
    prefix = 'search-'
    pk = None
    key = None
    value = None
    namespace = ''

    def __init__(self, pk, key, value):
        self.value = value
        self.key = key
        self.pk = pk
        self.namespace = self.prefix + key

    def __str__(self):
        return self.key


class ConfigProxyList():
    configs = None
    proxy_class = ConfigProxy

    def __init__(self, configs):
        self.configs = configs
        self.configs_by_namespace = {}
        for i in range(len(configs)):
            self.configs_by_namespace[configs[i][0]] = (i, configs[i][1])

    def get(self, namespace=None, pk=0):
        prefix = self.proxy_class.prefix
        if namespace and prefix in namespace:
            key = namespace.split(prefix)[1]
            config = self.configs_by_namespace.get(key)
            if config and len(config) == 2:
                return self.proxy_class(config[0], key, config[1])
            raise ObjectDoesNotExist('Error')
        else:
            return self.proxy_class(pk, self.configs[pk][0], self.configs[pk][1])

    def __iter__(self):
        return iter([self.proxy_class(i, value[0], value[1]) for i, value in enumerate(self.configs)])


class SearchApp(CMSApp):
    name = _('Search')
    #app_name = DEFAULT_APP_NAMESPACE
    urls = ['js_search.urls']
    app_config = ConfigProxy

    def get_urls(self, *args, **kwargs):
        return self.urls

    def get_configs(self):
        return ConfigProxyList(CONFIGS)

    def get_config(self, namespace):
        return self.get_configs().get(namespace=namespace)

    def get_config_add_url(self):
        pass

apphook_pool.register(SearchApp)
