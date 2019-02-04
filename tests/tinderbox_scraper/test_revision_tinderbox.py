#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import TinderboxScraper, errors

def test_valid_revision(httpd, tmpdir, mocker):
    query_builds_by_revision = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    build_path = httpd.get_url() + '/firefox/tinderbox-builds/mozilla-central-linux/1374583608/'
    query_builds_by_revision.return_value = [build_path]

    scraper = TinderboxScraper(destination=str(tmpdir),
                               base_url=httpd.get_url(),
                               platform='linux',
                               revision='6b92cb377496')

    assert len(scraper.builds) == 1
    assert scraper.url == build_path + 'firefox-25.0a1.en-US.linux-i686.tar.bz2'

def test_invalid_revision(httpd, tmpdir, mocker):
    query_builds_by_revision = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    query_builds_by_revision.return_value = []

    with pytest.raises(errors.NotFoundError):
        TinderboxScraper(destination=str(tmpdir),
                         base_url=httpd.get_url(),
                         platform='linux',
                         revision='not_valid')
