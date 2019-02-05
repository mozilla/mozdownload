#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import subprocess
import re

def test_unrecognized_argument():
    try:
        output = subprocess.check_output(['mozdownload', '--abc'],
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    assert re.search(r'mozdownload: error: unrecognized arguments: --abc'.encode('utf-8'), output) is not None
