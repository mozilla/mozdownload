# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to store various helper functions used in mozdownload."""

import hashlib


def urljoin(*fragments):
    """Concatenates multi part strings into urls"""

    return '/'.join(fragments)


def create_md5(path):
    """Creates the md5 hash of a file using the hashlib library"""

    m = hashlib.md5()
    # rb necessary to run correctly in windows.
    with open(path, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)

    return m.hexdigest()
