#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

import mozdownload


@pytest.mark.ci_only
@pytest.mark.parametrize("args", [
    {'application': 'fenix', 'platform': 'android-arm64-v8a', 'date': '2022-11-14'},
    {'application': 'fenix', 'platform': 'android-armeabi-v7a'},
    {'application': 'fenix', 'platform': 'android-x86'},
    {'application': 'fenix', 'platform': 'android-x86_64'},
])
def test_daily_scraper(tmpdir, args):
    mozdownload.DailyScraper(destination=tmpdir, **args)
