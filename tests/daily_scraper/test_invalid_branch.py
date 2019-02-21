#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdownload import DailyScraper
import mozdownload.errors as errors

@pytest.mark.parametrize('args', [
    ({'application': 'firefox', 'branch': 'invalid', 'platform': 'win32'})
])
def test_invalid_branch(httpd, tmpdir, args):
    """Testing download scenarios with invalid branch parameters for DailyScraper"""

    with pytest.raises(errors.NotFoundError):
        DailyScraper(destination=str(tmpdir), base_url=httpd.get_url(), **args)
