#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import mozhttpd

WDIR = os.path.join('tests', 'downloadable_tests')


@mozhttpd.handlers.json_response
def resource_get(request, objid):
    return (200, {'id': objid, 'query': request.query})


class MozHttpdTest(unittest.TestCase):
    """Generic test class that uses a mozhttpd server"""

    def setUp(self):
        """Starts server that lists all files in the directory"""
        self.httpd = mozhttpd.MozHttpd(port=8080, docroot='.',
                                       urlhandlers=[{'method': 'GET',
                                                    'path': '/api/resources/([^/]+)/?',
                                                    'function': resource_get}])
        print "\nServing '%s' at %s:%s" % (self.httpd.docroot,
                                           self.httpd.host, self.httpd.port)
        self.httpd.start(block=False)

    def tearDown(self):
        self.httpd.stop()

if __name__ == '__main__':
    unittest.main()
