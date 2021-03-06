"""Functional tests of caching different methods."""

from __future__ import print_function
from helpers import tf_cfg, chains
from testers import functional

__author__ = 'Tempesta Technologies, Inc.'
__copyright__ = 'Copyright (C) 2017 Tempesta Technologies, Inc.'
__license__ = 'GPL2'


class TestCacheMethods(functional.FunctionalTest):

    messages = 10

    # Replicated cache mode, no need to test other modes in this test.
    cache_mode = 2

    allow_method_caching = True

    # Methods, that can be cached by TempestaFW.
    cacheable_methods = ['COPY', 'DELETE', 'GET', 'HEAD', 'LOCK', 'MKCOL',
                         'MOVE', 'OPTIONS', 'PATCH', 'POST', 'PROPFIND',
                         'PROPPATCH', 'PUT', 'TRACE', 'UNLOCK']

    def chain(self, method, uri='/page.html', cache_alowed=True):
        if self.cache_mode == 0:
            cache_alowed = False
        if cache_alowed:
            return chains.cache_repeated(self.messages, method=method, uri=uri)
        return chains.proxy_repeated(self.messages, method=method, uri=uri)

    def try_method(self, method):
        tf_cfg.dbg(3, '\tTest method %s.' % method)
        chain = self.chain(method=method,
                           cache_alowed=(method in self.cacheable_methods))
        if self.allow_method_caching:
            cache_method = method
        else:
            cache_method = 'GET' if method != 'GET' else 'HEAD'
        config = ('cache %d;\n'
                  'cache_fulfill * *;\n'
                  'cache_methods %s;\n'
                  % (self.cache_mode, cache_method))
        self.generic_test_routine(config, chain)

    def test_copy(self):
        self.try_method('COPY')

    def test_delete(self):
        self.try_method('DELETE')

    def test_get(self):
        self.try_method('GET')

    def test_head(self):
        self.try_method('HEAD')

    def test_lock(self):
        self.try_method('LOCK')

    def test_mkcol(self):
        self.try_method('MKCOL')

    def test_move(self):
        self.try_method('MOVE')

    def test_options(self):
        self.try_method('OPTIONS')

    def test_patch(self):
        self.try_method('PATCH')

    def test_post(self):
        self.try_method('POST')

    def test_propfind(self):
        self.try_method('PROPFIND')

    def test_proppatch(self):
        self.try_method('PROPPATCH')

    def test_put(self):
        self.try_method('PUT')

    def test_trace(self):
        self.try_method('TRACE')

    def test_unlock(self):
        self.try_method('UNLOCK')


class TestCacheMethodsNC(TestCacheMethods):

    cacheable_methods = []
    allow_method_caching = False


class TestMultipleMethods(functional.FunctionalTest):
    """TempestaFW must return cached responses to exactly matching request
    methods only. I.e. if we receive HEAD requests, we must not return response
    cached for GET method.
    RFC 7234:
        The primary cache key consists of the request method and target URI.
    """

    config = ('cache 2;\n'
              'cache_fulfill * *;\n'
              'cache_methods GET HEAD;\n')

    def chains(self):
        uri = '/page.html'
        result = [# Populate Cache
                  chains.proxy(method='GET', uri=uri),
                  chains.proxy(method='HEAD', uri=uri),
                  # Serve from cache
                  chains.cache(method='GET', uri=uri),
                  chains.cache(method='HEAD', uri=uri),
                  ]
        return result

    def test_purge(self):
        self.generic_test_routine(self.config, self.chains())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
