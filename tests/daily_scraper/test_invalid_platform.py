#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from mozdownload import DailyScraper


@pytest.mark.parametrize('args', [
    ({'application': 'fenix', 'platform': 'mac'}),
])
def test_invalid_platform_falls_back_to_firefox(httpd, tmpdir, args):
    """fenix requested on a non-Android platform should fall back to firefox"""
    scraper = DailyScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
    assert scraper.application == 'firefox'
