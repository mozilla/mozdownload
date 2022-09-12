#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""Test all scraper classes for Firefox Developer Edition against the remote server"""

import pytest
from urllib.parse import unquote

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({'application': 'devedition', 'platform': 'linux', 'version': '60.0b1'},
     'devedition/releases/60.0b1/linux-i686/en-US/firefox-60.0b1.tar.bz2'),
    ({'application': 'devedition', 'platform': 'linux64', 'version': '60.0b1'},
     'devedition/releases/60.0b1/linux-x86_64/en-US/firefox-60.0b1.tar.bz2'),
    ({'application': 'devedition', 'platform': 'mac', 'version': '60.0b1'},
     'devedition/releases/60.0b1/mac/en-US/Firefox 60.0b1.dmg'),
    ({'application': 'devedition', 'platform': 'win32', 'version': '60.0b1'},
     'devedition/releases/60.0b1/win32/en-US/Firefox Setup 60.0b1.exe'),
    ({'application': 'devedition', 'platform': 'win64', 'version': '60.0b1'},
     'devedition/releases/60.0b1/win64/en-US/Firefox Setup 60.0b1.exe'),
    ({'application': 'devedition', 'platform': 'win32', 'version': '60.0b1', 'locale': 'de'},
     'devedition/releases/60.0b1/win32/de/Firefox Setup 60.0b1.exe'),
])
def test_release_scraper(tmpdir, args, url):
    """Test release scraper against the remote server."""
    scraper = mozdownload.ReleaseScraper(destination=tmpdir, **args)

    if url:
        assert unquote(scraper.url) == urljoin(BASE_URL, url)


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({'application': 'devedition', 'platform': 'linux', 'version': '60.0b1', 'build_number': 3},
     'devedition/candidates/60.0b1-candidates/build3/linux-i686/en-US/firefox-60.0b1.tar.bz2'),
    ({'application': 'devedition', 'platform': 'linux64', 'version': '60.0b1', 'build_number': 3},
     'devedition/candidates/60.0b1-candidates/build3/linux-x86_64/en-US/firefox-60.0b1.tar.bz2'),  # noqa
    ({'application': 'devedition', 'platform': 'mac', 'version': '60.0b1', 'build_number': 3},
     'devedition/candidates/60.0b1-candidates/build3/mac/en-US/Firefox 60.0b1.dmg'),
    ({'application': 'devedition', 'platform': 'win32', 'version': '60.0b1', 'build_number': 3},
     'devedition/candidates/60.0b1-candidates/build3/win32/en-US/Firefox Setup 60.0b1.exe'),
    ({'application': 'devedition', 'platform': 'mac', 'version': '60.0b1', 'build_number': 3,
      'locale': 'de'},
     'devedition/candidates/60.0b1-candidates/build3/mac/de/Firefox 60.0b1.dmg'),
    ({'application': 'devedition', 'platform': 'mac', 'version': '60.0b1', 'build_number': 3,
      'extension': 'json'},
     'devedition/candidates/60.0b1-candidates/build3/mac/en-US/firefox-60.0b1.json'),
])
def test_candidate_scraper(tmpdir, args, url):
    """Test release candidate scraper against the remote server."""
    scraper = mozdownload.ReleaseCandidateScraper(destination=tmpdir, **args)

    assert unquote(scraper.url) == urljoin(BASE_URL, url)
