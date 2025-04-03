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
    ({'application': 'thunderbird', 'platform': 'win32', 'version': 'latest'},
     None),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.0'},
     'thunderbird/releases/52.0/win32/en-US/Thunderbird Setup 52.0.exe'),
    ({'application': 'thunderbird', 'platform': 'linux', 'version': '52.0'},
     'thunderbird/releases/52.0/linux-i686/en-US/thunderbird-52.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': '52.0'},
     'thunderbird/releases/52.0/linux-x86_64/en-US/thunderbird-52.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': '52.0'},
     'thunderbird/releases/52.0/mac/en-US/Thunderbird 52.0.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.0', 'locale': 'de'},
     'thunderbird/releases/52.0/win32/de/Thunderbird Setup 52.0.exe'),
])
def test_release_scraper(tmpdir, args, url):
    """Test release scraper against the remote server."""
    args.update({"retry_attempts": 5, "retry_delay": 0.1})
    scraper = mozdownload.ReleaseScraper(destination=tmpdir, **args)

    if url:
        assert unquote(scraper.url) == urljoin(BASE_URL, url)


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({'application': 'thunderbird', 'platform': 'linux', 'version': '52.7.0'},
     'thunderbird/candidates/52.7.0-candidates/build1/linux-i686/en-US/thunderbird-52.7.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'linux64', 'version': '52.7.0'},
     'thunderbird/candidates/52.7.0-candidates/build1/linux-x86_64/en-US/thunderbird-52.7.0.tar.bz2'),
    ({'application': 'thunderbird', 'platform': 'mac', 'version': '52.7.0'},
     'thunderbird/candidates/52.7.0-candidates/build1/mac/en-US/Thunderbird 52.7.0.dmg'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.7.0'},
     'thunderbird/candidates/52.7.0-candidates/build1/win32/en-US/Thunderbird Setup 52.7.0.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.7.0', 'locale': 'cs'},
     'thunderbird/candidates/52.7.0-candidates/build1/win32/cs/Thunderbird Setup 52.7.0.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.7.0', 'locale': 'en-GB'},
     'thunderbird/candidates/52.7.0-candidates/build1/win32/en-GB/Thunderbird Setup 52.7.0.exe'),
    ({'application': 'thunderbird', 'platform': 'win32', 'version': '52.7.0', 'build_number': 1},
     'thunderbird/candidates/52.7.0-candidates/build1/win32/en-US/Thunderbird Setup 52.7.0.exe'),
])
def test_candidate_scraper(tmpdir, args, url):
    """Test release candidate scraper against the remote server."""
    args.update({"retry_attempts": 5, "retry_delay": 0.1})
    scraper = mozdownload.ReleaseCandidateScraper(destination=tmpdir, **args)

    assert unquote(scraper.url) == urljoin(BASE_URL, url)


@pytest.mark.ci_only
@pytest.mark.parametrize("args", [
    {'application': 'thunderbird', 'platform': 'linux', 'branch': 'comm-central'},
    {'application': 'thunderbird', 'platform': 'linux64', 'branch': 'comm-central'},
    {'application': 'thunderbird', 'platform': 'mac', 'branch': 'comm-central'},
    {'application': 'thunderbird', 'platform': 'win32', 'branch': 'comm-central'},
    {'application': 'thunderbird', 'platform': 'win64', 'branch': 'comm-central'},
    {'application': 'thunderbird', 'platform': 'win64',
        'branch': 'comm-central', 'date': '2024-01-02'},
    {'application': 'thunderbird', 'platform': 'win64',
        'branch': 'comm-central', 'date': '2024-01-02', 'build_number': 1},
    {'application': 'thunderbird', 'platform': 'win64',
        'branch': 'comm-central', 'build_id': '20240102101857'},
    {'application': 'thunderbird', 'platform': 'linux',
        'branch': 'comm-central', 'build_id': '20240102101857', 'extension': 'txt'},
    {'application': 'thunderbird', 'platform': 'linux64',
        'branch': 'comm-central', 'build_id': '20240103103152', 'locale': 'de'},
])
def test_daily_scraper(tmpdir, args):
    """Test daily scraper against the remote server."""
    args.update({"retry_attempts": 5, "retry_delay": 0.1})
    mozdownload.DailyScraper(destination=tmpdir, **args)


@pytest.mark.skip(reason='Not testable as long as we cannot grab a latest build')
def test_try_scraper():
    pass
