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

    def __init__(self, url, session=None, timeout=None):
        self.session = session or requests.Session()
        self.timeout = timeout

        self.active_url = None
        self.entries = []

        HTMLParser.__init__(self)

        # Force the server to not send cached content
        headers = {'Cache-Control': 'max-age=0'}
        r = self.session.get(url, headers=headers, timeout=self.timeout)

        try:
            r.raise_for_status()
            self.feed(r.text)
        finally:
            r.close()

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
                # Links look like: /pub/firefox/nightly/2015/
                # We have to trim the fragment down to the last item. Also to ensure we
                # always get it, we remove a possible final slash first
                has_final_slash = attr[1][-1] == '/'
                self.active_url = attr[1].rstrip('/').split('/')[-1]

                # Add back slash in case of sub folders
                if has_final_slash:
                    self.active_url = '%s/' % self.active_url

                return

    def handle_endtag(self, tag):
        if tag == 'a':
            self.active_url = None

    def handle_data(self, data):
        # Only process the data when we are in an active a tag and have an URL
        if not self.active_url:
            return

        if self.active_url in (data, urllib.quote(data)):
            self.entries.append(self.active_url.strip('/'))
