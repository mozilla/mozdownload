# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to store various helper functions used in mozdownload."""


def urljoin(*fragments):
    """Concatenates multi part strings into urls"""

    return '/'.join(fragments)
