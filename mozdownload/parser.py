# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to parse directory listings on a remote FTP server."""

from __future__ import absolute_import, unicode_literals

import re

import requests
from six.moves.html_parser import HTMLParser
from six.moves.urllib.parse import unquote


class DirectoryParser(HTMLParser):
    """Class to parse directory listings."""

    def __init__(self, url, session=None, authentication=None, timeout=None):
        """Create instance of a directory parser.

        :param url: url of the directory on the web server.
        :param session: a requests Session instance used to fetch the directory
                        content. If None, a new session will be created.
        :param authentication: a tuple (username, password) to authenticate against
                               the web server, or None for no authentication. Note
                               that it will only be used if the given *session* is
                               None.
        :param timeout: timeout in seconds used when fetching the directory
                        content.
        """
        if not session:
            session = requests.Session()
            session.auth = authentication
        self.session = session
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
        """Callback for when a tag gets opened."""
        if not tag == 'a':
            return

        for attr in attrs:
            if attr[0] == 'href':
                # Links look like: /pub/firefox/nightly/2015/
                # We have to trim the fragment down to the last item. Also to ensure we
                # always get it, we remove a possible final slash first
                url = unquote(attr[1])
                self.active_url = url.rstrip('/').split('/')[-1]

                return

    def handle_endtag(self, tag):
        """Callback for when a tag gets closed."""
        if tag == 'a':
            self.active_url = None

    def handle_data(self, data):
        """Callback when the data of a tag has been collected."""
        # Only process the data when we are in an active a tag and have an URL.
        if not self.active_url:
            return

        # The visible text can have a final slash so strip it off
        if data.strip('/') == self.active_url:
            self.entries.append(self.active_url)
