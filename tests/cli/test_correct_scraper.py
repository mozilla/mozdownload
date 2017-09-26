#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import mozfile
from mock import patch

from mozdownload import cli
import mozhttpd_base_test as mhttpd


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


class TestCLICorrectScraper(mhttpd.MozHttpdBaseTest):
    """Test mozdownload for correct choice of scraper"""

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_cli_scraper(self, query_builds_by_revision):
        for scraper_type, data in tests.iteritems():
            if data.get('builds'):
                query_builds_by_revision.return_value = data['builds']

            args = [
                '--base_url', self.wdir,
                '--destination', self.temp_dir,
            ]
            args.extend(data['args'])
            cli.cli(args)

            dir_content = os.listdir(self.temp_dir)
            self.assertTrue(data['fname'] in dir_content)

            mozfile.remove(os.path.join(self.temp_dir, data['fname']))
