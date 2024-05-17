#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""Test all scraper classes for Firefox against the remote server"""

import pytest
from urllib.parse import unquote

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({'application': 'firefox', 'platform': 'linux', 'version': 'latest'},
     None),
    ({'application': 'firefox', 'platform': 'linux', 'version': '42.0b2'},
     'firefox/releases/42.0b2/linux-i686/en-US/firefox-42.0b2.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': '42.0b2'},
     'firefox/releases/42.0b2/linux-x86_64/en-US/firefox-42.0b2.tar.bz2'),
    ({'application': 'firefox', 'platform': 'mac', 'version': '42.0b2'},
     'firefox/releases/42.0b2/mac/en-US/Firefox 42.0b2.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '42.0b2'},
     'firefox/releases/42.0b2/win32/en-US/Firefox Setup 42.0b2.exe'),
    ({'application': 'firefox', 'platform': 'win64', 'version': '42.0b2'},
     'firefox/releases/42.0b2/win64/en-US/Firefox Setup 42.0b2.exe'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '42.0b2', 'locale': 'de'},
     'firefox/releases/42.0b2/win32/de/Firefox Setup 42.0b2.exe'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '42.0b2',
      'is_stub_installer': True},  # old format
     'firefox/releases/42.0b2/win32/en-US/Firefox Setup Stub 42.0b2.exe'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '55.0',
      'is_stub_installer': True},  # new format
     'firefox/releases/55.0/win32/en-US/Firefox Installer.exe'),
])
def test_release_scraper(tmpdir, args, url):
    """Test release scraper against the remote server."""
    scraper = mozdownload.ReleaseScraper(destination=tmpdir, **args)

    if url:
        assert unquote(scraper.url) == urljoin(BASE_URL, url)


@pytest.mark.ci_only
@pytest.mark.parametrize("args,url", [
    ({'application': 'firefox', 'platform': 'linux', 'version': '45.4.0esr', 'build_number': 1},
     'firefox/candidates/45.4.0esr-candidates/build1/linux-i686/en-US/firefox-45.4.0esr.tar.bz2'),
    ({'application': 'firefox', 'platform': 'linux64', 'version': '45.4.0esr', 'build_number': 1},
     'firefox/candidates/45.4.0esr-candidates/build1/linux-x86_64/en-US/firefox-45.4.0esr.tar.bz2'),  # noqa
    ({'application': 'firefox', 'platform': 'mac', 'version': '45.4.0esr', 'build_number': 1},
     'firefox/candidates/45.4.0esr-candidates/build1/mac/en-US/Firefox 45.4.0esr.dmg'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '45.4.0esr', 'build_number': 1},
     'firefox/candidates/45.4.0esr-candidates/build1/win32/en-US/Firefox Setup 45.4.0esr.exe'),
    ({'application': 'firefox', 'platform': 'mac', 'version': '45.4.0esr', 'build_number': 1,
      'locale': 'de'},
     'firefox/candidates/45.4.0esr-candidates/build1/mac/de/Firefox 45.4.0esr.dmg'),
    ({'application': 'firefox', 'platform': 'mac', 'version': '45.4.0esr', 'build_number': 1,
      'extension': 'json'},
     'firefox/candidates/45.4.0esr-candidates/build1/mac/en-US/firefox-45.4.0esr.json'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '52.0', 'build_number': 1,
      'is_stub_installer': True},  # old format
     'firefox/candidates/52.0-candidates/build1/win32/en-US/Firefox Setup Stub 52.0.exe'),
    ({'application': 'firefox', 'platform': 'win32', 'version': '55.0', 'build_number': 1,
      'is_stub_installer': True},
     'firefox/candidates/55.0-candidates/build1/win32/en-US/Firefox Installer.exe'),
])
def test_candidate_scraper(tmpdir, args, url):
    """Test release candidate scraper against the remote server."""
    scraper = mozdownload.ReleaseCandidateScraper(destination=tmpdir, **args)

    assert unquote(scraper.url) == urljoin(BASE_URL, url)


@pytest.mark.ci_only
@pytest.mark.parametrize("args", [
    {'branch': 'mozilla-central', 'platform': 'linux'},
    {'branch': 'mozilla-central', 'platform': 'linux64'},
    {'branch': 'mozilla-central', 'platform': 'linux-arm64'},
    {'branch': 'mozilla-central', 'platform': 'mac'},
    {'branch': 'mozilla-central', 'platform': 'win32'},
    {'branch': 'mozilla-central', 'platform': 'win64'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'date': '2015-10-21'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'date': '2015-10-21', 'build_number': 2},
    {'branch': 'mozilla-central', 'platform': 'win32', 'build_id': '20151021065025'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'build_id': '20151021030212',
     'locale': 'de'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'build_id': '20151021030212',
     'extension': 'txt'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'build_id': '20151021030212',
     'is_stub_installer': True},  # old format
    {'branch': 'mozilla-central', 'platform': 'win32', 'build_id': '20170821100350',
     'is_stub_installer': True},  # new format
    {'branch': 'mozilla-central', 'platform': 'win64', 'build_id': '20170821100350',
     'is_stub_installer': True},
])
def test_daily_scraper(tmpdir, args):
    """Test daily scraper against the remote server."""
    mozdownload.DailyScraper(destination=tmpdir, **args)


@pytest.mark.ci_only
@pytest.mark.parametrize("args", [
    {'branch': 'mozilla-release', 'platform': 'linux'},
    {'branch': 'mozilla-release', 'platform': 'linux64'},
    {'branch': 'mozilla-release', 'platform': 'mac'},
    {'branch': 'mozilla-release', 'platform': 'win32'},
    {'branch': 'mozilla-release', 'platform': 'win64'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'debug_build': True},
    {'branch': 'mozilla-central', 'platform': 'win32', 'locale': 'de'},
    {'branch': 'mozilla-central', 'platform': 'win32', 'extension': 'txt'},
])
def test_tinderbox_scraper(tmpdir, args):
    """Test tinderbox scraper against the remote server."""
    mozdownload.TinderboxScraper(destination=tmpdir, **args)


@pytest.mark.skip(reason='Not testable as long as we cannot grab a latest build')
def test_try_scraper():
    pass
