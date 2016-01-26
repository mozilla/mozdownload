# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""Base testcase class for mozdownload unit tests."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import tempfile
import unittest

import mozfile
from wptserve import server

WDIR = 'data'
HERE = os.path.dirname(os.path.abspath(__file__))


class MozHttpdBaseTest(unittest.TestCase):
    """Base test class that uses mozhttpd as server."""

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format=' %(levelname)s | %(message)s',
                            level=logging.CRITICAL)
        cls.logger = logging.getLogger()

        cls.httpd = server.WebTestHttpd(port=8080,
                                        doc_root=os.path.join(HERE, WDIR),
                                        host='127.0.0.1')
        cls.wdir = 'http://{}:{}'.format(cls.httpd.host, cls.httpd.port)
        cls.httpd.start(block=False)

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        mozfile.rmtree(self.temp_dir)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.stop()

if __name__ == '__main__':
    unittest.main()
