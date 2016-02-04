#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Test runner for mozdownload unit tests."""

from __future__ import absolute_import, print_function, unicode_literals

import imp
import os
import sys
import unittest

from manifestparser import TestManifest
from moztest.results import TestResultCollection

here = os.path.dirname(os.path.abspath(__file__))


def get_tests(path):
    """Return the unittests in a .py file."""
    path = os.path.abspath(path)
    unittests = []
    assert os.path.exists(path)
    modname = os.path.splitext(os.path.basename(path))[0]
    module = imp.load_source(modname, path)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)
    for test in suite:
        unittests.append(test)
    return unittests


def test_all(manifest):
    """Run all tests."""
    print('\n#################')
    print('# Running tests #')
    print('#################\n')

    # gather the tests
    tests = manifest.active_tests(disabled=False)
    unittestlist = []
    for test in tests:
        unittestlist.extend(get_tests(test['path']))

    # run the tests
    suite = unittest.TestSuite(unittestlist)
    # default=1 does not show success of unittests
    runner = unittest.TextTestRunner(verbosity=2)
    unittest_results = runner.run(suite)
    return unittest_results


def main(args=sys.argv[1:]):
    """Main method."""
    # read the manifest
    if args:
        manifests = args
    else:
        manifests = [os.path.join(here, 'manifest.ini')]
    missing = []
    for manifest_file in manifests:
        # ensure manifests exist
        if not os.path.exists(manifest_file):
            missing.append(manifest_file)
    assert not missing, 'manifest%s not found: %s' % (
        (len(manifests) == 1 and '' or 's'), ', '.join(missing))
    manifest = TestManifest(manifests=manifests)
    unittest_results = test_all(manifest)
    results = TestResultCollection.from_unittest_results(
        None, unittest_results)

    # exit according to results
    sys.exit(1 if results.num_failures else 0)

if __name__ == '__main__':
    main()
