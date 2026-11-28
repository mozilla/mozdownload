#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import DailyScraper


@pytest.mark.parametrize('args', [
    ({'application': 'fenix', 'platform': 'mac'}),
])
def test_fenix_falls_back_to_firefox_on_desktop_platform(httpd, tmpdir, args):
    """fenix requested on a non-Android platform falls back to firefox"""
    with pytest.warns(DeprecationWarning):
        scraper = DailyScraper(destination=str(tmpdir),
                               base_url=httpd.get_url(), **args)
    assert scraper.application == 'firefox'


def test_fenix_without_platform_defaults_to_android(httpd, tmpdir):
    """fenix without an explicit platform defaults to android-arm64-v8a"""
    with pytest.warns(DeprecationWarning):
        scraper = DailyScraper(destination=str(tmpdir),
                               base_url=httpd.get_url(),
                               application='fenix')
    assert scraper.application == 'fenix'
    assert scraper.platform == 'android-arm64-v8a'


@pytest.mark.parametrize('platform', [
    'android-arm64-v8a', 'android-armeabi-v7a',
    'android-x86', 'android-x86_64'])
def test_firefox_on_android_maps_to_fenix(httpd, tmpdir, platform):
    """firefox requested on an Android platform maps to fenix"""
    scraper = DailyScraper(destination=str(tmpdir),
                           base_url=httpd.get_url(),
                           application='firefox',
                           platform=platform)
    assert scraper.application == 'fenix'
    assert scraper.base_url.endswith('/fenix/')