#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import unittest
import urlparse

from wptserve.handlers import json_handler

from mozdownload.treeherder import Treeherder, PLATFORM_MAP
import mozhttpd_base_test as mhttpd


HERE = os.path.dirname(os.path.abspath(__file__))


@json_handler
def handle_rest_api(request, response):
    """Simple JSON handler for the Treeherder Rest API."""
    url_fragments = urlparse.urlparse(request.url)
    query_options = urlparse.parse_qs(url_fragments.query)
    api_endpoint = url_fragments.path.rsplit('/', 2)[1]

    # Use API endpoint to load reference JSON data
    with open(os.path.join(HERE, 'data', '%s.json' % api_endpoint), 'r') as f:
        data = json.loads(f.read())

    def do_filter(entry):
        result = True

        for option, values in query_options.iteritems():
            # Don't handle options which are not properties of the entry
            if option not in entry:
                continue

            for value in values:
                if isinstance(entry[option], int):
                    result &= entry[option] == int(value)
                else:
                    result &= entry[option] == value

        return result

    if api_endpoint == 'jobs':
        data['results'] = filter(do_filter, data['results'])

    elif api_endpoint == 'job-log-url':
        data = filter(do_filter, data)

    return data


class TestAPI(mhttpd.MozHttpdBaseTest):
    """Basic tests for the Treeherder wrapper."""

    def test_query_tinderbox_builds(self):
        self.httpd.router.register('GET', '/api/*', handle_rest_api)

        for platform in PLATFORM_MAP:
            # mac64 is identical to mac
            if platform == 'mac64':
                continue

            application = 'firefox' if not platform.startswith('android') else 'mobile'
            th = Treeherder(application, 'mozilla-beta', platform,
                            server_url='http://{}:{}'.format(self.httpd.host, self.httpd.port))
            builds = th.query_builds_by_revision('29258f59e545')

            self.assertEqual(len(builds), 1)
            self.assertRegexpMatches(builds[0].rsplit('/', 3)[1],
                                     r'mozilla-beta-%s' % platform)


class TestAPIInvalidUsage(mhttpd.MozHttpdBaseTest):
    """Invalid usage of the Treeherder wrapper."""

    def test_invalid_query_does_not_raise(self):
        th = Treeherder('firefox', 'mozilla-beta', 'invalid_platform',
                        server_url='http://{}:{}'.format(self.httpd.host, self.httpd.port))
        builds = th.query_builds_by_revision('29258f59e545')

        self.assertEqual(builds, [])


if __name__ == '__main__':
    unittest.main()
