#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import subprocess

from mozdownload import __version__, cli


def test_cli_executes():
    """Test that cli will start and print usage message"""
    output = subprocess.check_output(['mozdownload', '--help'])
    assert cli.__doc__.format(__version__) in output.decode("utf-8")
