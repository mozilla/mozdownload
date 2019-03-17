#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import TinderboxScraper


@pytest.mark.parametrize("args", [
    ({'application': 'firefox', 'branch': 'mozilla-central', 'date': '20140317030202',
    'locale': 'pt-PT', 'platform': 'win32'}),
    ({'branch': 'mozilla-central', 'date': 'invalid', 'locale': 'pt-PT', 'platform': 'win32'}),
    ({'branch': 'mozilla-central', 'date': '2013/07/02', 'platform': 'win64'}),
    ({'branch': 'mozilla-central', 'date': '2013-March-15', 'platform': 'win32'}),
])
def test_scraper(httpd, tmpdir, args):
    """Testing download scenarios with invalid parameters for TinderboxScraper"""

    with pytest.raises(ValueError):
        TinderboxScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
