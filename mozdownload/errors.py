# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Exception types in use by mozdownload."""

from __future__ import unicode_literals


class NotSupportedError(Exception):
    """Exception for a build not being supported."""

    def __init__(self, message):
        """Create an instance of an exception."""
        Exception.__init__(self, message)


class NotFoundError(Exception):
    """Exception for a resource not being found (e.g. no logs)."""

    def __init__(self, message, location):
        """Create an instance of an exception."""
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))


class NotImplementedError(Exception):
    """Exception for a feature which is not implemented yet."""

    def __init__(self, message):
        """Create an instance of an exception."""
        Exception.__init__(self, message)


class TimeoutError(Exception):
    """Exception for a download exceeding the allocated timeout."""

    def __init__(self):
        """Create an instance of an exception."""
        self.message = 'The download exceeded the allocated timeout'
        Exception.__init__(self, self.message)


class HashMismatchError(Exception):
    """Exception for when the hash of a file does not match with
        what is provided."""

    def __init__(self, filename):
        """Create an instance of an exception."""
        self.message = ('The checksum for %s is different from what was'
                        ' expected' % filename)
        Exception.__init__(self, self.message)


class HashNotFoundError(Exception):
    """Exception for when a file's checksum cannot be found in a
        list of checksums."""

    def __init__(self, filename):
        """Create an instance of an exception."""
        self.message = 'A checksum for %s could not be found' % filename
        Exception.__init__(self, self.message)
