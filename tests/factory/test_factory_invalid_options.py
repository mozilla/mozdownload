import copy
import os

import mozfile
from mock import patch

from mozdownload import FactoryScraper
from mozdownload.utils import urljoin
from mozdownload.errors import NotSupportedError

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
            'revision': '8fcac92cfcad',
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
            'revision': '8fcac92cfcad',
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

            'debug_build': True,
            'url': 'http://localhost',
            'version': '23.0.1',
        },
    },

    # TinderboxScraper
    {
        'scraper_type': 'tinderbox',
        'fname': '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
        'kwargs': {
            'platform': 'win32',

            'url': 'http://localhost',
            'version': '23.0.1',
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
                          logger=self.logger)

    def test_candidate_without_version(self):
        """Test that missing mandatory options for candidate builds raise an exception"""
        self.assertRaises(ValueError, FactoryScraper,
                          scraper_type='release',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          logger=self.logger)

    def test_try_without_revision(self):
        """Test that missing mandatory options for try builds raise an exception"""
        self.assertRaises(ValueError, FactoryScraper,
                          scraper_type='try',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          logger=self.logger)

    def test_non_daily_fennic(self):
        """Test that non-daily scrapper_type for fennec raises exception"""
        self.assertRaises(NotSupportedError, FactoryScraper,
                          scraper_type='candidate',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          logger=self.logger,
                          application='fennec',
                          version='60.0b1')

    def test_non_release_non_candidate_devedition(self):
        """Test that non-relase and non-candidate scrapper type for devedition raises exception"""
        self.assertRaises(NotSupportedError, FactoryScraper,
                          scraper_type='daily',
                          destination=self.temp_dir,
                          base_url=self.wdir,
                          logger=self.logger,
                          application='devedition',
                          version='60.0b1')


class TestFactoryUnusedOptions(mhttpd.MozHttpdBaseTest):

    @patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    def test_unknown_options(self, query_builds_by_revision):
        """Test that unknown optional options do not break the given scraper."""

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

    def test_unknown_options_direct_scraper(self):
        filename = 'download_test.txt'
        test_url = urljoin(self.wdir, filename)

        scraper = FactoryScraper(scraper_type='direct',
                                 url=test_url,
                                 destination=self.temp_dir,
                                 logger=self.logger,

                                 platform='win32',
                                 branch='mozilla-central',
                                 build_id='20131001030204',
                                 revision='8fcac92cfcad',
                                 date='2013-10-01',
                                 debug_build=True,
                                 version='23.0.1',
                                 )

        self.assertEqual(scraper.url, test_url)
        self.assertEqual(scraper.filename,
                         os.path.join(self.temp_dir, filename))
