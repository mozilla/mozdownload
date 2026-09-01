#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import re

import pytest

from mozdownload.treeherder import PLATFORM_MAP, Treeherder


@pytest.mark.parametrize('platform', PLATFORM_MAP)
def test_query_builds_by_revision(httpd, platform):
    """Basic tests for the Treeherder wrapper."""
    if platform == 'mac64':
        pytest.skip("mac64 is identical to mac")

    application = 'firefox' if not platform.startswith('android') else 'fenix'
    th = Treeherder(application, 'mozilla-beta', platform,
                    server_url='http://{}:{}'.format(httpd.host, httpd.port))
    builds = th.query_builds_by_revision('29258f59e545')

    assert len(builds) == 1
    assert re.search(r'mozilla-beta-%s' % platform, builds[0].rsplit('/', 3)[1]) is not None
