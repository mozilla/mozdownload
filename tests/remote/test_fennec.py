#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

import mozdownload


@pytest.mark.parametrize("args", [
    # Support for API level 9 ended on Mar 11th 2016
    {'application': 'fennec', 'platform': 'android-api-9',
     'branch': 'mozilla-central', 'date': '2016-03-11'},
    # Support for API level 11 ended on Jan 28th 2016
    {'application': 'fennec', 'platform': 'android-api-11',
     'branch': 'mozilla-central', 'date': '2016-01-28'},
    # Support for API level 15 ended on Aug 29th 2017
    {'application': 'fennec', 'platform': 'android-api-15',
     'branch': 'mozilla-central', 'date': '2017-08-29'},
    {'application': 'fennec', 'platform': 'android-x86', 'branch': 'mozilla-central'},
])
def test_daily_scraper(tmpdir, args):
    mozdownload.DailyScraper(destination=tmpdir, **args)
