#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from mozdownload.parser import DirectoryParser
from mozdownload.utils import urljoin


def test_init(httpd):
    """Testing the basic functionality of the DirectoryParser Class"""

    # DirectoryParser returns output
    parser = DirectoryParser(httpd.get_url())

    # relies on the presence of other files in the directory
    # Checks if DirectoryParser lists the server entries
    assert parser.entries != [], "parser.entries were not listed"

    # path_regex to mozdownload -t release -p win32 -v latest
    testpath = urljoin(httpd.get_url(), 'directoryparser/')
    parser = DirectoryParser(testpath)
    parser.entries.sort()
    testdir = os.listdir(urljoin(httpd.router.doc_root, 'directoryparser'))
    testdir.sort()
    assert parser.entries == testdir


def test_filter(httpd):
    """Testing the DirectoryParser filter method"""
    parser = DirectoryParser(urljoin(httpd.get_url(), 'directoryparser', 'filter/'))
    parser.entries.sort()

    # Get the contents of the folder - dirs and files
    folder_path = urljoin(httpd.router.doc_root, 'directoryparser', 'filter')
    contents = os.listdir(folder_path)
    contents.sort()
    assert parser.entries == contents

    # filter out files
    parser.entries = parser.filter(r'^\d+$')

    # Get only the subdirectories of the folder
    dirs = os.walk(folder_path).__next__()[1]
    dirs.sort()
    assert parser.entries == dirs

    # Test filter method with a function
    parser.entries = parser.filter(lambda x: x == dirs[0])
    assert parser.entries == [dirs[0]]


def test_names_with_spaces(httpd):
    parser = DirectoryParser(urljoin(httpd.get_url(), 'directoryparser', 'some spaces/'))
    parser.entries.sort()

    # Get the contents of the folder - dirs and files
    folder_path = urljoin(httpd.router.doc_root, 'directoryparser', 'some spaces')
    contents = os.listdir(folder_path)
    contents.sort()
    assert parser.entries == contents
