# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class NotSupportedError(Exception):
    """Exception for a build not being supported"""
    def __init__(self, message):
        Exception.__init__(self, message)


class NotFoundError(Exception):
    """Exception for a resource not being found (e.g. no logs)"""
    def __init__(self, message, location):
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))


class NotImplementedError(Exception):
    """Exception for a feature which is not implemented yet"""
    def __init__(self, message):
        Exception.__init__(self, message)


class TimeoutError(Exception):
    """Exception for a download exceeding the allocated timeout"""
    def __init__(self):
        self.message = 'The download exceeded the allocated timeout'
        Exception.__init__(self, self.message)
