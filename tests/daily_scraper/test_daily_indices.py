#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import DailyScraper

@pytest.mark.parametrize("args,build_index,builds", [
    ({'platform': 'win32'}, 0, ['2013-10-01-03-02-04-mozilla-central']),
    ({'build_id': '20130706031213', 'platform': 'win32', 'branch': 'mozilla-central'}, 0,
     ['2013-07-06-03-12-13-mozilla-central']),
    ({'date': '2013-07-02', 'platform': 'win32', 'branch': 'mozilla-central'}, 1,
     ['2013-07-02-03-12-13-mozilla-central', '2013-07-02-04-12-13-mozilla-central']),
    ({'date': '2013-07-02', 'platform': 'win32', 'build_number': 1, 'branch': 'mozilla-central'}, 0,
     ['2013-07-02-03-12-13-mozilla-central', '2013-07-02-04-12-13-mozilla-central'])
])
def test_build_indices(httpd, tmpdir, args, build_index, builds):
    """Testing for correct build_index in DailyScraper"""

    scraper = DailyScraper(destination=tmpdir, base_url=httpd.get_url(), **args)
    assert scraper.build_index == build_index
    assert scraper.builds == builds
