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

@pytest.mark.parametrize('platform_key,platform_value', PLATFORM_FRAGMENTS.items())
def test_platform_regex(tmpdir, platform_key, platform_value):
    """Test for correct platform_regex output"""
    scraper = mozdownload.Scraper(destination=str(tmpdir), platform=platform_key)
    assert scraper.platform_regex == platform_value

def test_standard_download(httpd, tmpdir):
    """Test standard download method"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=str(tmpdir))
    scraper.download()
    assert os.path.isfile(os.path.join(str(tmpdir), filename))

def test_compare_download(httpd, tmpdir):
    """Compare original and downloaded file via md5 hash"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=str(tmpdir))
    scraper.download()
    md5_original = create_md5(os.path.join(httpd.router.doc_root, filename))
    md5_downloaded = create_md5(os.path.join(str(tmpdir), filename))
    assert md5_original == md5_downloaded

def test_request_exception(httpd, tmpdir):
    """RequestException"""
    test_url1 = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper1 = mozdownload.DirectScraper(url=test_url1, destination=str(tmpdir))
    with pytest.raises(requests.exceptions.RequestException):
        scraper1.download()

def test_retry_attempts(httpd, tmpdir):
    """Covering retry attempts"""
    test_url2 = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper2 = mozdownload.DirectScraper(url=test_url2,
                                         destination=str(tmpdir),
                                         retry_attempts=3,
                                         retry_delay=1.0)
    with pytest.raises(requests.exceptions.RequestException):
        scraper2.download()

@pytest.mark.parametrize('attr', ['binary', 'binary_regex', 'path_regex'])
def test_notimplementedexceptions(tmpdir, attr):
    """test implementations available"""
    scraper = mozdownload.Scraper(destination=str(tmpdir))
    with pytest.raises(errors.NotImplementedError):
        getattr(scraper, attr)
    with pytest.raises(errors.NotImplementedError):
        scraper.build_filename('invalid binary')

@pytest.mark.skip(reason="Permanent failure due to mozqa.com not available anymore (#492)")
def test_invalid_authentication(tmpdir):
    """test with invalid authentication"""
    basic_auth_url = 'http://mozqa.com/data/mozqa.com/http_auth/basic/'
    scraper = mozdownload.DirectScraper(destination=str(tmpdir), url=basic_auth_url)
    with pytest.raises(requests.exceptions.HTTPError):
        scraper.download()

@pytest.mark.skip(reason="Permanent failure due to mozqa.com not available anymore (#492)")
def test_valid_authentication(tmpdir):
    """testing with valid authentication"""
    username = 'mozilla'
    password = 'mozilla'
    basic_auth_url = 'http://mozqa.com/data/mozqa.com/http_auth/basic/'
    scraper = mozdownload.DirectScraper(destination=str(tmpdir),
                                        url=basic_auth_url,
                                        username=username,
                                        password=password)
    scraper.download()
    assert os.path.isfile(os.path.join(str(tmpdir), 'mozqa.com'))

def test_destination_isdirectory(httpd, tmpdir):
    """destination is directory"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=str(tmpdir))
    assert scraper.filename == os.path.join(str(tmpdir), filename)


def test_destination_hasdirectory(httpd, tmpdir):
    """destination has directory path with filename"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.filename == destination

def test_destination_hasfile(httpd):
    """destination only has filename"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=filename)
    assert scraper.filename == os.path.abspath(filename)

def test_destination_doesnotexist(httpd, tmpdir):
    """destination directory does not exist"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), 'temp_folder', filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.destination == destination

def test_destination_multipledir(httpd, tmpdir):
    """ensure that multiple non existing directories are created"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), 'tmp1', 'tmp2', filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.destination == destination
