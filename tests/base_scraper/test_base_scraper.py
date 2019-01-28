#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pytest
import requests

import mozdownload
import mozdownload.errors as errors
from mozdownload.scraper import PLATFORM_FRAGMENTS
from mozdownload.utils import create_md5, urljoin

@pytest.mark.parametrize('platform', PLATFORM_FRAGMENTS.items())
def test_platform_regex(tmpdir, platform):
    """Test for correct platform_regex output"""
    tmpdir = str(tmpdir)
    scraper = mozdownload.Scraper(destination=tmpdir,
                                  platform=platform[0])
    assert scraper.platform_regex == platform[1]

def test_download(httpd, tmpdir):
    """Test download method"""
    tmpdir = str(tmpdir)
    filename = 'download_test.txt'
    # standard download
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=tmpdir)
    scraper.download()
    assert os.path.isfile(os.path.join(tmpdir, filename))
    # Compare original and downloaded file via md5 hash
    md5_original = create_md5(os.path.join(httpd.router.doc_root,
                                           filename))
    md5_downloaded = create_md5(os.path.join(tmpdir, filename))
    assert md5_original == md5_downloaded

    # RequestException
    test_url1 = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper1 = mozdownload.DirectScraper(url=test_url1,
                                         destination=tmpdir)
    with pytest.raises(requests.exceptions.RequestException):
        scraper1.download()

    # Covering retry_attempts
    test_url2 = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper2 = mozdownload.DirectScraper(url=test_url2,
                                         destination=tmpdir,
                                         retry_attempts=3,
                                         retry_delay=1.0)
    with pytest.raises(requests.exceptions.RequestException):
        scraper2.download()

@pytest.mark.parametrize('attr', ['binary', 'binary_regex', 'path_regex'])
def test_notimplementedexceptions(tmpdir, attr):
    tmpdir = str(tmpdir)
    scraper = mozdownload.Scraper(destination=tmpdir)
    with pytest.raises(errors.NotImplementedError):
        getattr(scraper, attr)
    with pytest.raises(errors.NotImplementedError):
        scraper.build_filename('invalid binary')

@pytest.mark.skip(reason="Permanent failure due to mozqa.com not available anymore (#492)")
def test_authentication(tmpdir):
    """testing with basic authentication"""
    tmpdir = str(tmpdir)
    username = 'mozilla'
    password = 'mozilla'
    basic_auth_url = 'http://mozqa.com/data/mozqa.com/http_auth/basic/'

    # test with invalid authentication
    scraper = mozdownload.DirectScraper(destination=tmpdir,
                                        url=basic_auth_url)
    with pytest.raises(requests.exceptions.HTTPError):
        scraper.download()

    # testing with valid authentication
    scraper = mozdownload.DirectScraper(destination=tmpdir,
                                        url=basic_auth_url,
                                        username=username,
                                        password=password)
    scraper.download()
    assert os.path.isfile(os.path.join(tmpdir, 'mozqa.com'))

def test_destination(httpd, tmpdir):
    """Test for various destination scenarios"""
    tmpdir = str(tmpdir)
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)

    # destination is directory
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=tmpdir)
    assert scraper.filename == os.path.join(tmpdir, filename)

    # destination has directory path with filename
    destination = os.path.join(tmpdir, filename)
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=destination)
    assert scraper.filename == destination

    # destination only has filename
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=filename)
    assert scraper.filename == os.path.abspath(filename)

    # destination directory does not exist
    destination = os.path.join(tmpdir, 'temp_folder', filename)
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=destination)
    assert scraper.destination == destination

    # ensure that multiple non existing directories are created
    destination = os.path.join(tmpdir, 'tmp1', 'tmp2', filename)
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=destination)
    assert scraper.destination == destination
