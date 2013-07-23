# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to parse directory listings on a remote FTP server."""

from HTMLParser import HTMLParser
import re
import requests
import urllib


class DirectoryParser(HTMLParser):
    """Class to parse directory listings"""

    def __init__(self, url, authentication=None, timeout=None):
        self.authentication = authentication
        self.timeout = timeout

        self.active_url = None
        self.entries = []

        HTMLParser.__init__(self)

        # Force the server to not send cached content
        headers = {'Cache-Control': 'max-age=0'}
        r = requests.get(url, auth=self.authentication,
                         headers=headers, timeout=self.timeout)
        r.raise_for_status()
        self.feed(r.text)

    def filter(self, filter):
        """Filter entries by calling function or applying regex."""

        if hasattr(filter, '__call__'):
            return [entry for entry in self.entries if filter(entry)]
        else:
            pattern = re.compile(filter, re.IGNORECASE)
            return [entry for entry in self.entries if pattern.match(entry)]

    def handle_starttag(self, tag, attrs):
        if not tag == 'a':
            return

        for attr in attrs:
            if attr[0] == 'href':
                self.active_url = attr[1].strip('/')
                return

    def handle_endtag(self, tag):
        if tag == 'a':
            self.active_url = None

    def handle_data(self, data):
        # Only process the data when we are in an active a tag and have an URL
        if not self.active_url:
            return

        name = urllib.quote(data.strip('/'))
        if self.active_url == name:
            self.entries.append(self.active_url)
