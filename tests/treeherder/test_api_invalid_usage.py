#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from mozdownload.treeherder import Treeherder


def test_invalid_query_does_not_raise(httpd):
    """Invalid usage of the Treeherder wrapper."""
    th = Treeherder('firefox', 'mozilla-beta', 'invalid_platform',
                    server_url='http://{}:{}'.format(httpd.host, httpd.port))
    builds = th.query_builds_by_revision('29258f59e545')

    assert builds == []
