#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pytest

from mozdownload import DirectScraper
import mozdownload.errors as errors
from mozdownload.utils import urljoin

@pytest.mark.parametrize('attr', ['binary', 'binary_regex', 'path', 'path_regex'])
def test_url_download(httpd, tmpdir, attr):
    """test mozdownload direct url scraper"""
    tmpdir = str(tmpdir)
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = DirectScraper(url=test_url, destination=tmpdir)
    assert scraper.url == test_url
    assert scraper.filename == os.path.join(tmpdir, filename)
    with pytest.raises(errors.NotImplementedError):
        getattr(scraper, attr)
    scraper.download()
    assert os.path.isfile(os.path.join(tmpdir, scraper.filename))
