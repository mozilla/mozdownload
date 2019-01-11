#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from wptserve import server

from mozdownload import ReleaseCandidateScraper
import conftest



@pytest.mark.parametrize("args,build_index,build_number,builds", [
    ({'application': 'firefox', 'build_number': '1', 'platform': 'win32', 'version': '23.0.1'},
     '0', '1', ['build1']),
    ({'application': 'firefox', 'build_number': '3', 'platform': 'mac', 'version': '23.0.1'},
     '0', '3', ['build3']),
    ({'application': 'firefox', 'build_number': '2', 'platform': 'linux', 'version': '23.0.1'},
     '1', '2', ['build1', 'build3']),
])

def test_build_indices(httpd, tmpdir, args, build_index, build_number, builds):
    """Testing indices in choosing builds for ReleaseCandidateScraper"""

    return httpd.start(block=False)

    scraper = ReleaseCandidateScraper(destination=tmpdir, base_url=httpd.get_url(), **args)
    assert scraper.build_index == int(build_index)
    assert scraper.build_number == build_number
    assert scraper.builds == builds

    httpd.stop()
