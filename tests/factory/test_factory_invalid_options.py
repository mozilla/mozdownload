import copy
import os

import mozfile

from mozdownload import FactoryScraper
from mozdownload.utils import urljoin

import mozhttpd_base_test as mhttpd


tests = [
    # ReleaseScraper
    {
        'scraper_type': 'release',
        'fname': 'firefox-23.0.1.en-US.win32.exe',
        'kwargs': {
            'version': '23.0.1',
            'platform': 'win32',

            'branch': 'mozilla-central',
            'build_id': '20131001030204',
            'build_number': '1',
            'changeset': '8fcac92cfcad',
            'date': '2013-10-01',
            'debug_build': True,
            'url': 'http://localhost',
        }
    },

    # ReleaseCandidateScraper
    {
        'scraper_type': 'candidate',
        'fname': 'firefox-23.0.1-build3.en-US.win32.exe',
        'kwargs': {
            'platform': 'win32',
            'version': '23.0.1',

            'branch': 'mozilla-central',
            'build_id': '20131001030204',
            'changeset': '8fcac92cfcad',
            'date': '2013-10-01',
            'debug_build': True,
            'url': 'http://localhost',
        },
    },

    # DailyScraper
    {
        'scraper_type': 'daily',
        'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
        'kwargs': {
            'platform': 'win32',

            'changeset': '8fcac92cfcad',
            'debug_build': True,
            'url': 'http://localhost',
            'version': '23.0.1',
        },
    },

    # TinderboxScraper
    {
        'scraper_type': 'tinderbox',
        'fname': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
        'kwargs': {
            'platform': 'win32',

            'changeset': '8fcac92cfcad',
            'url': 'http://localhost',
            'version': '23.0.1',
        },
    },

    # TryScraper
    {
        'scraper_type': 'try',
        'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
        'kwargs': {
            'changeset': '8fcac92cfcad',
            'platform': 'mac64',

            'build_id': '20131001030204',
            'build_number': '1',
            'url': 'http://localhost',
            'version': '23.0.1',
        },
    },
]


class TestFactoryMissingMandatoryOptions(mhttpd.MozHttpdBaseTest):

    def test_release_without_version(self):
        """Test that missing mandatory options for release builds raise an exception"""
        self.assertRaises(ValueError, FactoryScraper,
                          scraper_type='release',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          log_level='ERROR')

    def test_candidate_without_version(self):
        """Test that missing mandatory options for candidate builds raise an exception"""
        self.assertRaises(ValueError, FactoryScraper,
                          scraper_type='release',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          log_level='ERROR')


class TestFactoryUnusedOptions(mhttpd.MozHttpdBaseTest):

    def test_unknown_options(self):
        """Test that unknown optional options do not break the given scraper."""

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

    def test_unknown_options_direct_scraper(self):
        filename = 'download_test.txt'
        test_url = urljoin(self.wdir, filename)

        scraper = FactoryScraper(scraper_type='direct',
                                 url=test_url,
                                 destination=self.temp_dir,
                                 log_level='ERROR',

                                 platform='win32',
                                 branch='mozilla-central',
                                 build_id='20131001030204',
                                 changeset='8fcac92cfcad',
                                 date='2013-10-01',
                                 debug_build=True,
                                 version='23.0.1',
                                 )

        self.assertEqual(scraper.url, test_url)
        self.assertEqual(scraper.filename,
                         os.path.join(self.temp_dir, filename))
