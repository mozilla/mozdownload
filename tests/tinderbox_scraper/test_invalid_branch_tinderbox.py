#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import TinderboxScraper
import mozdownload.errors as errors

@pytest.mark.parametrize('args', [
    ({'platform': 'win32', 'branch': 'invalid'}),
])
def test_invalid_branch_tinderbox(httpd, tmpdir, args):
    """Testing download scenarios with invalid branch parameters for TinderboxScraper"""

    with pytest.raises(errors.NotFoundError):
        TinderboxScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
