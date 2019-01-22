#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import urllib
import pytest
from mock import patch
from mozdownload import TryScraper
from mozdownload.utils import urljoin

@pytest.mark.parametrize("args,filename,url", [
    # -p mac64 --revision=8fcac92cfcad
    ({'platform': 'mac64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-macosx64/firefox-38.0a1.en-US.mac.dmg'),
    # -p mac --revision=8fcac92cfcad
    ({'platform': 'mac', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-macosx64/firefox-38.0a1.en-US.mac.dmg'),
    # -a firefox -p linux64 --revision=8fcac92cfcad
    ({'platform': 'linux64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.linux-x86_64.tar.bz2',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-linux64/firefox-38.0a1.en-US.linux-x86_64.tar.bz2'),
    # -a firefox -p linux --revision=8fcac92cfcad --debug-build
    ({'platform': 'linux', 'revision': '8fcac92cfcad', 'debug_build': True},
     '8fcac92cfcad-debug-firefox-38.0a1.en-US.linux-i686.tar.bz2',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-linux-debug/firefox-38.0a1.en-US.linux-i686.tar.bz2'),
    # -a firefox -p win32 --revision=8fcac92cfcad
    ({'platform': 'win32', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.win32.installer.exe',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-win32/firefox-38.0a1.en-US.win32.installer.exe'),
    # -a firefox -p win64 --revision=8fcac92cfcad
    ({'platform': 'win64', 'revision': '8fcac92cfcad'},
     '8fcac92cfcad-firefox-38.0a1.en-US.win64.installer.exe',
     'firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/'
     'try-win64/firefox-38.0a1.en-US.win64.installer.exe')
])


@patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
def test_scraper(mock_query_builds_by_revision, httpd, tmpdir, args, filename, url):
    """Testing various download scenarios for TryScraper"""
    mock_query_builds_by_revision.return_value = [
        '/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'
    ]
    baseurl = httpd.get_url()
    scraper = TryScraper(destination=str(tmpdir),
                         base_url=baseurl,
                         **args)
    expected_filename = os.path.join(str(tmpdir), filename)
    assert scraper.filename == expected_filename
    assert urllib.unquote(scraper.url) == urljoin(baseurl, url)
