#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pytest

from mozdownload import DirectScraper
import mozdownload.errors as errors
from mozdownload.utils import urljoin

def test_url_download(httpd, tmpdir):
    """test mozdownload direct url scraper"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = DirectScraper(url=test_url, destination=str(tmpdir))
    assert scraper.url == test_url
    assert scraper.filename == os.path.join(str(tmpdir), filename)

    scraper.download()
    assert os.path.isfile(os.path.join(str(tmpdir), scraper.filename))


@pytest.mark.parametrize('attr', ['binary', 'binary_regex', 'path', 'path_regex'])
def test_implementation_error(httpd, tmpdir, attr):
    """test implementations available"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = DirectScraper(url=test_url, destination=str(tmpdir))
    with pytest.raises(errors.NotImplementedError):
        getattr(scraper, attr)
