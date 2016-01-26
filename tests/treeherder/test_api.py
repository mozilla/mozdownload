#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import unittest

from wptserve.handlers import json_handler

from mozdownload.treeherder import Treeherder
import mozhttpd_base_test as mhttpd


HERE = os.path.dirname(os.path.abspath(__file__))


@json_handler
def handle_rest_api(request, response):
    """Simple JSON handler for the Treeherder Rest API."""
    filename = '%s.json' % request.request_path.rsplit('/', 2)[1]

    with open(os.path.join(HERE, '29258f59e545', filename), 'r') as f:
        return json.loads(f.read())


class TestAPI(mhttpd.MozHttpdBaseTest):
    """Basic tests for the Treeherder wrapper."""

    def test_query_builds(self):
        self.httpd.router.register('GET', '/api/*', handle_rest_api)

        th = Treeherder('firefox', 'mozilla-central', 'win32',
                        host='{}:{}'.format(self.httpd.host, self.httpd.port),
                        protocol='http')
        builds = th.query_builds_by_revision('29258f59e545')

        self.assertNotEqual(builds, [])


class TestAPIInvalidUsage(mhttpd.MozHttpdBaseTest):
    """Invalid usage of the Treeherder wrapper."""

    def test_invalid_query_does_not_raise(self):
        th = Treeherder('foobar', 'example', 'win32',
                        host='{}:{}'.format(self.httpd.host, self.httpd.port),
                        protocol='http')
        builds = th.query_builds_by_revision('29258f59e545')

        self.assertEqual(builds, [])


if __name__ == '__main__':
    unittest.main()
