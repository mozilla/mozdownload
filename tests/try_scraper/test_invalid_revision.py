#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from mozdownload import TryScraper
import mozdownload.errors as errors

def test_invalid_parameters(mocker, httpd, tmpdir):
    """Testing download scenarios with invalid parameters for TryScraper"""
    query_builds_by_revision = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    query_builds_by_revision.return_value = []
    with pytest.raises(errors.NotFoundError):
        assert TryScraper(destination=tmpdir,
                          base_url=httpd.get_url(),
                          platform='win32',
                          revision='abc')