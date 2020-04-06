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


def test_url_not_found(httpd, tmpdir):
    test_url = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper = mozdownload.DirectScraper(url=test_url, destination=str(tmpdir))
    with pytest.raises(errors.NotFoundError):
        scraper.download()


def test_retry_attempts(httpd, tmpdir):
    test_url = urljoin(httpd.get_url(), 'does_not_exist.html')
    scraper = mozdownload.DirectScraper(url=test_url,
                                        destination=str(tmpdir),
                                        retry_attempts=3,
                                        retry_delay=0.1)
    with pytest.raises(errors.NotFoundError):
        scraper.download()


@pytest.mark.parametrize('attr', ['binary', 'binary_regex', 'path_regex'])
def test_not_implemented(tmpdir, attr):
    """test implementations available"""
    scraper = mozdownload.Scraper(destination=str(tmpdir))
    with pytest.raises(errors.NotImplementedError):
        getattr(scraper, attr)

    with pytest.raises(errors.NotImplementedError):
        scraper.build_filename('invalid binary')


def test_invalid_authentication(httpd, tmpdir):
    basic_auth_url = urljoin(httpd.get_url(), 'basic_auth')
    scraper = mozdownload.DirectScraper(destination=str(tmpdir), url=basic_auth_url)
    with pytest.raises(requests.exceptions.HTTPError):
        scraper.download()


def test_valid_authentication(httpd, tmpdir):
    username = 'mozilla'
    password = 'mozilla'
    basic_auth_url = urljoin(httpd.get_url(), 'basic_auth')
    scraper = mozdownload.DirectScraper(destination=str(tmpdir),
                                        url=basic_auth_url,
                                        username=username,
                                        password=password)
    scraper.download()
    assert os.path.isfile(os.path.join(str(tmpdir), 'basic_auth'))


def test_destination_as_directory(httpd, tmpdir):
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=str(tmpdir))
    assert scraper.filename == os.path.join(str(tmpdir), filename)


def test_destination_as_path_with_filename(httpd, tmpdir):
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.filename == destination


def test_destination_as_filename_only(httpd):
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=filename)
    assert scraper.filename == os.path.abspath(filename)


def test_destination_does_not_exist(httpd, tmpdir):
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), 'temp_folder', filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.destination == destination


def test_destination_multiple_dir(httpd, tmpdir):
    """ensure that multiple non existing directories are created"""
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)
    destination = os.path.join(str(tmpdir), 'tmp1', 'tmp2', filename)
    scraper = mozdownload.DirectScraper(url=test_url, destination=destination)
    assert scraper.destination == destination
