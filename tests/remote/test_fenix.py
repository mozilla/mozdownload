#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from urllib.parse import unquote

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({
        'application': 'fenix',
        'platform': 'android-arm64-v8a',
        'version': '123.0',
    },
        'fenix/releases/123.0/android/fenix-123.0-android-arm64-v8a/fenix-123.0.multi.android-arm64-v8a.apk'
    ),
    ({
        'application': 'fenix',
        'platform': 'android-armeabi-v7a',
        'version': '123.0',
    },
        'fenix/releases/123.0/android/fenix-123.0-android-armeabi-v7a/fenix-123.0.multi.android-armeabi-v7a.apk'
    ),
    ({
        'application': 'fenix',
        'platform': 'android-x86',
        'version': '123.0',
    },
        'fenix/releases/123.0/android/fenix-123.0-android-x86/fenix-123.0.multi.android-x86.apk'),
    ({
        'application': 'fenix',
        'platform': 'android-x86_64',
        'version': '123.0',
    },
        'fenix/releases/123.0/android/fenix-123.0-android-x86_64/fenix-123.0.multi.android-x86_64.apk'),
    ({
        'application': 'fenix',
        'platform': 'android-x86_64',
        'version': 'latest',
    },
        None),
    ({
        'application': 'fenix',
        'platform': 'android-x86_64',
        'version': '123.0',
        'locale': 'de',
    },
        'fenix/releases/123.0/android/fenix-123.0-android-x86_64/fenix-123.0.multi.android-x86_64.apk'),
])
def test_release_scraper(tmpdir, args, url):
    """Test release scraper against the remote server."""
    scraper = mozdownload.ReleaseScraper(destination=tmpdir, **args)

    if url:
        assert unquote(scraper.url) == urljoin(BASE_URL, url)

@pytest.mark.ci_only
@pytest.mark.parametrize("args", [
    {'application': 'fenix', 'branch': 'mozilla-central',
        'platform': 'android-arm64-v8a'},
    {'application': 'fenix', 'branch': 'mozilla-central',
        'platform': 'android-armeabi-v7a'},
    {'application': 'fenix', 'branch': 'mozilla-central', 'platform': 'android-x86'},
    {'application': 'fenix', 'branch': 'mozilla-central',
        'platform': 'android-x86_64'},
    {'application': 'fenix', 'branch': 'mozilla-central',
        'platform': 'android-arm64-v8a', 'date': '2024-01-02'},
    {'application': 'fenix', 'branch': 'mozilla-central', 'platform': 'android-x86_64',
        'date': '2024-01-02', 'build_number': 2},
    {'application': 'fenix', 'branch': 'mozilla-central', 'platform': 'android-x86_64',
        'build_id': '20240102160221'},
    {'application': 'fenix', 'branch': 'mozilla-central', 'platform': 'android-x86_64',
        'extension': 'apk'},
])
def test_daily_scraper(tmpdir, args):
    mozdownload.DailyScraper(destination=tmpdir, **args)
