import copy
import os

import mozfile

from mozdownload import FactoryScraper
import mozhttpd_base_test as mhttpd


tests = [
    # ReleaseScraper
    {
        'scraper_type': 'release',
        'fname': 'firefox-latest.en-US.linux64.tar.bz2',
        'kwargs': {
            'version': 'latest',
        }
    },

    # ReleaseCandidateScraper
    {
        'scraper_type': 'candidate',
        'fname': 'firefox-21.0-build3.en-US.win32.exe',
        'kwargs': {
            'platform': 'win32',
            'version': '21.0',
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
        'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
        'kwargs': {
            'changeset': '8fcac92cfcad',
            'platform': 'mac64',
        },
    },
]


class TestFactoryCorrectScraper(mhttpd.MozHttpdBaseTest):
    """Test mozdownload for the factory scraper."""

    def test_factory(self):
        """Testing various download scenarios for the factory."""

        base_kwargs = {
            'base_url': self.wdir,
            'destination': self.temp_dir,
            'log_level': 'ERROR',
        }

        for test in tests:
            kwargs = copy.deepcopy(base_kwargs)
            kwargs.update(test.get('kwargs'))

            build = FactoryScraper(test['scraper_type'], **kwargs)
            build.download()

            dir_content = os.listdir(self.temp_dir)
            self.assertTrue(test['fname'] in dir_content)

            mozfile.remove(os.path.join(self.temp_dir, test['fname']))
