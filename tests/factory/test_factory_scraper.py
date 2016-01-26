import copy
import os

import mozfile
from mock import patch

from mozdownload import FactoryScraper
import mozhttpd_base_test as mhttpd


tests = [
    # ReleaseScraper
    {
        'scraper_type': 'release',
        'fname': 'firefox-23.0.1.en-US.linux64.tar.bz2',
        'kwargs': {
            'version': '23.0.1',
        }
    },

    # ReleaseCandidateScraper
    {
        'scraper_type': 'candidate',
        'fname': 'firefox-23.0.1-build3.en-US.win32.exe',
        'kwargs': {
            'platform': 'win32',
            'version': '23.0.1',
        },
    },

    # DailyScraper
    {
        'scraper_type': 'daily',
        'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
        'kwargs': {
            'platform': 'win32',
        },
    },

    # TinderboxScraper
    {
        'scraper_type': 'tinderbox',
        'fname': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
        'kwargs': {
            'platform': 'win32',
        },
    },

    # TryScraper
    {
        'scraper_type': 'try',
        'builds': ['/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'],
        'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
        'kwargs': {
            'revision': '8fcac92cfcad',
            'platform': 'mac64',
        },
    },
]


class TestFactoryCorrectScraper(mhttpd.MozHttpdBaseTest):
    """Test mozdownload for the factory scraper."""

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_factory(self, query_builds_by_revision):
        """Testing various download scenarios for the factory."""

        base_kwargs = {
            'base_url': self.wdir,
            'destination': self.temp_dir,
            'log_level': 'ERROR',
        }

        for test in tests:
            if test.get('builds'):
                query_builds_by_revision.return_value = test['builds']

            kwargs = copy.deepcopy(base_kwargs)
            kwargs.update(test.get('kwargs'))

            build = FactoryScraper(test['scraper_type'], **kwargs)
            build.download()

            dir_content = os.listdir(self.temp_dir)
            self.assertTrue(test['fname'] in dir_content)

            mozfile.remove(os.path.join(self.temp_dir, test['fname']))
