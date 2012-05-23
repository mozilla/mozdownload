#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Script to download builds for Firefox and Thunderbird from the Mozilla server."""


from optparse import OptionParser, OptionGroup
import os
import sys

import scraper


APPLICATIONS = ['firefox', 'thunderbird']

BUILD_TYPES = {'release': scraper.ReleaseScraper,
               'candidate': scraper.ReleaseCandidateScraper,
               'daily': scraper.DailyScraper,
               'tinderbox': scraper.TinderboxScraper }


def cli():
    """Main function for the downloader"""

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('--application', '-a',
                      dest='application',
                      choices=APPLICATIONS,
                      default=APPLICATIONS[0],
                      metavar='APPLICATION',
                      help='The name of the application to download, '
                           'default: "%s"' % APPLICATIONS[0])
    parser.add_option('--directory', '-d',
                      dest='directory',
                      default=os.getcwd(),
                      metavar='DIRECTORY',
                      help='Target directory for the download, default: '
                           'current working directory')
    parser.add_option('--build-number',
                      dest='build_number',
                      default=None,
                      type="int",
                      metavar='BUILD_NUMBER',
                      help='Number of the build (for candidate, daily, '
                           'and tinderbox builds)')
    parser.add_option('--locale', '-l',
                      dest='locale',
                      default='en-US',
                      metavar='LOCALE',
                      help='Locale of the application, default: "en-US"')
    parser.add_option('--platform', '-p',
                      dest='platform',
                      choices=scraper.PLATFORM_FRAGMENTS.keys(),
                      metavar='PLATFORM',
                      help='Platform of the application')
    parser.add_option('--type', '-t',
                      dest='type',
                      choices=BUILD_TYPES.keys(),
                      default=BUILD_TYPES.keys()[0],
                      metavar='BUILD_TYPE',
                      help='Type of build to download, default: "%s"' %
                           BUILD_TYPES.keys()[0])
    parser.add_option('--version', '-v',
                      dest='version',
                      metavar='VERSION',
                      help='Version of the application to be used by release and\
                            candidate builds, i.e. "3.6"')

    # Option group for candidate builds
    group = OptionGroup(parser, "Candidate builds",
                        "Extra options for candidate builds.")
    group.add_option('--no-unsigned',
                     dest='no_unsigned',
                     action="store_true",
                     help="Don't allow to download unsigned builds if signed\
                           builds are not available")
    parser.add_option_group(group)

    # Option group for daily builds
    group = OptionGroup(parser, "Daily builds",
                        "Extra options for daily builds.")
    group.add_option('--branch',
                     dest='branch',
                     default='mozilla-central',
                     metavar='BRANCH',
                     help='Name of the branch, default: "mozilla-central"')
    parser.add_option('--build-id',
                      dest='build_id',
                      default=None,
                      metavar='BUILD_ID',
                      help='ID of the build to download')
    group.add_option('--date',
                     dest='date',
                     default=None,
                     metavar='DATE',
                     help='Date of the build, default: latest build')
    parser.add_option_group(group)

    # Option group for tinderbox builds
    group = OptionGroup(parser, "Tinderbox builds",
                        "Extra options for tinderbox builds.")
    group.add_option('--debug-build',
                     dest='debug_build',
                     action="store_true",
                     help="Download a debug build")
    parser.add_option_group(group)

    # TODO: option group for nightly builds
    (options, args) = parser.parse_args()

    # Check for required options and arguments
    # Note: Will be optional when ini file support has been landed
    if not options.type in ['daily', 'tinderbox'] \
       and not options.version:
        parser.error('The version of the application to download has not been specified.')

    # Instantiate scraper and download the build
    scraper_keywords = {'application': options.application,
                        'locale': options.locale,
                        'platform': options.platform,
                        'version': options.version,
                        'directory': options.directory}
    scraper_options = {'candidate': {
                           'build_number': options.build_number,
                           'no_unsigned': options.no_unsigned},
                       'daily': {
                           'branch': options.branch,
                           'build_number': options.build_number,
                           'build_id': options.build_id,
                           'date': options.date},
                       'tinderbox': {
                           'branch': options.branch,
                           'build_number': options.build_number,
                           'date': options.date,
                           'debug_build': options.debug_build}
                       }

    kwargs = scraper_keywords.copy()
    kwargs.update(scraper_options.get(options.type, {}))
    build = BUILD_TYPES[options.type](**kwargs)

    build.download()

if __name__ == "__main__":
    cli()
