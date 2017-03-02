#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import tempfile
import unittest
import urllib

import mozfile

import mozdownload
from mozdownload.scraper import BASE_URL
from mozdownload.utils import urljoin


tests_release_scraper = [
    # -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '52.0.2'},
     'url': 'https://archive.mozilla.org/pub/firefox/releases/52.0.2/SHA512SUMS',
     'hash': 'e6b055194d1bd6255d634e8e2f23d019cdb853578667076d3249774ba3e1af436' \
             '6e8c926406bcc0ae620788a367bb2ee2bedede30c54b13eea777591a753bf59'},
     # -p win64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'win64',
               'version': '52.0.2'},
      'url': 'https://archive.mozilla.org/pub/firefox/releases/52.0.2/SHA512SUMS',
      'hash': '5317f274990c8587a7079f3a79374d7a5a1831c69c185e04ead2f06f5ac0eae7' \
              'accbed369d4c96d28493baf45b3e2e7ec3a17631f23c54d3db24fcd5a81f1877'},
      # -p linux -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux',
               'version': '52.0.2'},
      'url': 'https://archive.mozilla.org/pub/firefox/releases/52.0.2/SHA512SUMS',
      'hash': '0b7a25e0df55a7607aa9e6478b5aa188fb545842a6a8ef2279f7997faa725555' \
              'd966b276aa1201cc1be45b1428faee846d59e0af39cbadb8ae4dee92d9dbb2c9'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux64',
               'version': '52.0.2'},
      'url': 'https://archive.mozilla.org/pub/firefox/releases/52.0.2/SHA512SUMS',
      'hash': 'f84b186c83e7cc3cc2bcab136029e299cfb4cbf89891f07a7f0c79584df18c91' \
              '4c24c51615e6bdb677571e194e964cd6d49cdf10f76f68f3b7b9bcaae50ceb3e'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'mac',
               'version': '52.0.2'},
      'url': 'https://archive.mozilla.org/pub/firefox/releases/52.0.2/SHA512SUMS',
      'hash': '51bbac18a401b12dbb0a7e52519de6631cd217e312682d01d10a202b52e029be' \
              '71f601cb026866b78f1c76e6176c4197982df2657e61f77a789283b41ad0da1b'},
]

tests_candidate_scraper = [
    # -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': '53.0b9'},
     'url': 'https://archive.mozilla.org/pub/firefox/candidates/53.0b9-candidates/build1/SHA512SUMS',
     'hash': 'c0be3e32850ee3cfe4c6d4bee112df8488da248b907b801e7a33eef0dfd0385f0' \
             'cf1031ee39c2dda51c10661c0d822e70bdf7fb86d23a2af8464d2594a4f7fbc'},
     # -p win64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'win64',
               'version': '53.0b9'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/53.0b9-candidates/build1/SHA512SUMS',
      'hash': '215095f65bf9fc5029cb2d1befce91a54283263552281dad92b34dbcbb8a40e2' \
              '2ebc36501b34827906a2da44d0981ae2652b101af21df6d59f7880ecb1b238b4'},
      # -p linux -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux',
               'version': '53.0b9'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/53.0b9-candidates/build1/SHA512SUMS',
      'hash': '3a32f608aa3252db784d50a1beec2654e1ebd31e7985446d312d8df8a809303e' \
              '4581bcad8572aa37a91d4d09ded0defe4290c528142dbe2d9f820d0261bf17a3'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux64',
               'version': '53.0b9'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/53.0b9-candidates/build1/SHA512SUMS',
      'hash': 'a71d5b34a58b7c440711f838e268a17a7a515d6f641c1c29e1fde5e5313aab73' \
              '2dfc38970e40f3cd209bbb32ad1618358fa5ebba77b0e6d88c2a44c46f630cc0'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'mac',
               'version': '53.0b9'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/53.0b9-candidates/build1/SHA512SUMS',
      'hash': 'ec13593e7ba46c4f86ab15b888c33346a05efe0144120f8ac7d65633b5d7e259' \
              '6e317bf073647cf04db400ae0f5d97411a24bf1f0a9691f49ca51ac995f339d6'},
]

tests_daily_scraper = [
    # -p win32 -v latest
    {'args': {'application': 'firefox',
              'platform': 'win32',
              'version': 'latest'},
     'url': 'https://archive.mozilla.org/pub/firefox/candidates/52.0.2-candidates/build1/SHA256SUMS',
     'hash': '197c5d03735b3c1084abee7a19aa23a2ec705cf5ee2e7accf88e0669cc99427a'},
     # -p win64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'win64',
               'version': 'latest'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/52.0.2-candidates/build1/SHA256SUMS',
      'hash': '4662484c180bad22e4077c14553f98dd8456b2b169f82299ed24de2b92cdd3de'},
      # -p linux -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux',
               'version': 'latest'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/52.0.2-candidates/build1/SHA256SUMS',
      'hash': '489a029538f8980458e49d7128d4791443038a6f150cfee472b59c7d04867f12'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'linux64',
               'version': 'latest'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/52.0.2-candidates/build1/SHA256SUMS',
      'hash': 'a37f817182da13dd34520039da8d0ddeb8bad7dd260ec8fb79c61e770bbaf83f'},
       # -p linux64 -v latest
     {'args': {'application': 'firefox',
               'platform': 'mac',
               'version': 'latest'},
      'url': 'https://archive.mozilla.org/pub/firefox/candidates/52.0.2-candidates/build1/SHA256SUMS',
      'hash': 'f9a91e0d57652566ba7f0d2e191cdc3db3219b3cf29a83ed145a9110a0bda108'},
]


class FirefoxHashTests(unittest.TestCase):
    """Test all scraper classes for Firefox against the remote server"""

    def setUp(self):
        logging.basicConfig(format=' %(levelname)s | %(message)s', level=logging.ERROR)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    def test_release_scraper(self):
        for test in tests_release_scraper:
          scraper = mozdownload.ReleaseScraper(destination=self.temp_dir,
                                               logger=self.logger,
                                               **test['args'])
          checksum_url = test.get('url')
          checksum_code = scraper.has_checksum(checksum_url)
          if checksum_code:
            checksum_file = scraper.download_checksum(checksum_url)
            checksum_data = scraper.parse_checksum_file(checksum_file)
            if checksum_data:
              self.assertEqual(checksum_data,
                               test['hash'])

    def test_candidate_scraper(self):
        for test in tests_candidate_scraper:
            scraper = mozdownload.ReleaseCandidateScraper(destination=self.temp_dir,
                                                          logger=self.logger,
                                                          **test['args'])
            url = test.get('url')
            file = scraper.download_checksum(url)
            checksum = scraper.parse_checksum_file(file)
            self.assertEqual(checksum,
                            test.get('hash'))

if __name__ == '__main__':
    unittest.main()
