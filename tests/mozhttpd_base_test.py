# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""Base testcase class for mozdownload unit tests."""

from __future__ import absolute_import, print_function, unicode_literals

import os
import tempfile
import unittest

import mozfile
import mozhttpd
import mozlog

from mozdownload.utils import urljoin

WDIR = 'data'
HERE = os.path.dirname(os.path.abspath(__file__))


@mozhttpd.handlers.json_response
def resource_get(request, objid):
    """Request handler for JSON responses."""
    return (200, {'id': objid, 'query': request.query})


class MozHttpdBaseTest(unittest.TestCase):
    """Base test class that uses mozhttpd as server."""

    def setUp(self):
        """Run setup routines for the testcase."""
        self.logger = mozlog.unstructured.getLogger(self.__class__.__name__)
        self.logger.setLevel('ERROR')
        self.httpd = mozhttpd.MozHttpd(port=8080, docroot=HERE,
                                       urlhandlers=[{'method': 'GET',
                                                     'path': '/api/resources/([^/]+)/?',
                                                     'function': resource_get}])
        self.logger.debug("Serving '%s' at %s:%s" % (self.httpd.docroot,
                                                     self.httpd.host,
                                                     self.httpd.port))
        self.httpd.start(block=False)
        self.server_address = "http://%s:%s" % (self.httpd.host,
                                                self.httpd.port)
        self.wdir = urljoin(self.server_address, WDIR)

        # Create a temporary directory for potential downloads
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Run teardown routines for the testcase."""
        self.httpd.stop()
        mozfile.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
