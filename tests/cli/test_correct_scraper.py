#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest

from mozdownload import cli

tests = {
    'release': {
        'args': ['-v', '23.0.1', '-p', 'win32'],
        'fname': 'firefox-23.0.1.en-US.win32.exe',
    },

    'candidate': {
        'args': ['-t', 'candidate', '-v', '23.0.1', '-p', 'win32'],
        'fname': 'firefox-23.0.1-build3.en-US.win32.exe',
    },

    'daily': {
        'args': ['-t', 'daily', '-p', 'win32'],
        'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
    },

    'tinderbox': {
        'args': ['-t', 'tinderbox', '-p', 'win32'],
        'fname': '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
    },

    'try': {
        'args': ['-t', 'try', '-p', 'win32', '--revision', '8fcac92cfcad'],
        'builds': ['/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-win32/'],
        'fname': '8fcac92cfcad-firefox-38.0a1.en-US.win32.installer.exe',
    },
}


@pytest.mark.parametrize("data", tests.values())
def test_correct_cli_scraper(httpd, tmpdir, data, mocker):
    query_builds_by_revision = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')

    if data.get('builds'):
        query_builds_by_revision.return_value = data['builds']

    args = [
        '--base_url', httpd.get_url(),
        '--destination', str(tmpdir),
    ]
    args.extend(data['args'])
    cli.cli(args)

    dir_content = os.listdir(str(tmpdir))
    assert data['fname'] in dir_content
