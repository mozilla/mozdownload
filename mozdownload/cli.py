#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import os
import pkg_resources
import sys

from . import errors
from . import scraper


version = pkg_resources.require("mozdownload")[0].version

__doc__ = """
Module to handle downloads for different types of archive.mozilla.org hosted
applications.

mozdownload version: %(version)s
""" % {'version': version}


def cli():
    """Main function for the downloader"""

    build_types = {'release': scraper.ReleaseScraper,
                   'candidate': scraper.ReleaseCandidateScraper,
                   'daily': scraper.DailyScraper,
                   'tinderbox': scraper.TinderboxScraper,
                   'try': scraper.TryScraper,
                   }

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application', '-a',
                        dest='application',
                        choices=scraper.APPLICATIONS,
                        default='firefox',
                        metavar='APPLICATION',
                        help='The name of the application to download, default: "%(default)s"')
    parser.add_argument('--base_url',
                        dest='base_url',
                        default=scraper.BASE_URL,
                        metavar='BASE_URL',
                        help='The base url to be used, default: "%(default)s"')
    parser.add_argument('--destination', '-d',
                        dest='destination',
                        default=os.getcwd(),
                        metavar='DESTINATION',
                        help='Directory or file name to download the '
                             'file to, default: current working directory')
    parser.add_argument('--build-number',
                        dest='build_number',
                        type=int,
                        metavar='BUILD_NUMBER',
                        help='Number of the build (for candidate, daily, and tinderbox builds)')
    parser.add_argument('--locale', '-l',
                        dest='locale',
                        metavar='LOCALE',
                        help='Locale of the application, default: "en-US" or "multi"')
    parser.add_argument('--platform', '-p',
                        dest='platform',
                        choices=scraper.PLATFORM_FRAGMENTS.keys(),
                        metavar='PLATFORM',
                        help='Platform of the application')
    parser.add_argument('--stub',
                        dest='is_stub_installer',
                        action='store_true',
                        help='Stub installer. Only applicable to Windows builds.')
    parser.add_argument('--type', '-t',
                        dest='type',
                        choices=build_types.keys(),
                        default='release',
                        metavar='BUILD_TYPE',
                        help='Type of build to download, default: "%(default)s"')
    parser.add_argument('--url',
                        dest='url',
                        metavar='URL',
                        help='URL to download. Note: Reserved characters (such '
                             'as &) must be escaped or put in quotes otherwise '
                             'CLI output may be abnormal.')
    parser.add_argument('--version', '-v',
                        dest='version',
                        metavar='VERSION',
                        help='Version of the application to be used by release '
                             'and candidate builds, i.e. "3.6"')
    parser.add_argument('--extension',
                        dest='extension',
                        metavar='EXTENSION',
                        help='File extension of the build (e.g. "zip"), default: '
                             'the standard build extension on the platform.')
    parser.add_argument('--username',
                        dest='username',
                        metavar='USERNAME',
                        help='Username for basic HTTP authentication.')
    parser.add_argument('--password',
                        dest='password',
                        metavar='PASSWORD',
                        help='Password for basic HTTP authentication.')
    parser.add_argument('--retry-attempts',
                        dest='retry_attempts',
                        default=0,
                        type=int,
                        metavar='RETRY_ATTEMPTS',
                        help='Number of times the download will be attempted in '
                             'the event of a failure, default: %(default)s')
    parser.add_argument('--retry-delay',
                        dest='retry_delay',
                        default=10.,
                        type=float,
                        metavar='RETRY_DELAY',
                        help='Amount of time (in seconds) to wait between retry '
                             'attempts, default: %(default)s')
    parser.add_argument('--timeout',
                        dest='timeout',
                        type=float,
                        metavar='TIMEOUT',
                        help='Amount of time (in seconds) until a download times out')
    parser.add_argument('--log-level',
                        action='store',
                        dest='log_level',
                        default='INFO',
                        metavar='LOG_LEVEL',
                        help='Threshold for log output (default: %(default)s)')

    # Group for daily builds
    group = parser.add_argument_group('Daily builds', 'Extra options for daily builds.')
    group.add_argument('--branch',
                       dest='branch',
                       default='mozilla-central',
                       metavar='BRANCH',
                       help='Name of the branch, default: "%(default)s"')
    group.add_argument('--build-id',
                       dest='build_id',
                       metavar='BUILD_ID',
                       help='ID of the build to download')
    group.add_argument('--date',
                       dest='date',
                       metavar='DATE',
                       help='Date of the build, default: latest build')

    # Group for tinderbox builds
    group = parser.add_argument_group('Tinderbox builds', 'Extra options for tinderbox builds.')
    group.add_argument('--debug-build',
                       dest='debug_build',
                       action='store_true',
                       help='Download a debug build')

    # Group for try builds
    group = parser.add_argument_group('Try builds', 'Extra options for try builds.')
    group.add_argument('--changeset',
                       dest='changeset',
                       help='Changeset of the try build to download')

    args = parser.parse_args()

    # Gives instructions to user when no arguments were passed
    if len(sys.argv) == 1:
        print(__doc__)
        parser.format_usage()
        print('Specify --help for more information on args. '
              'Please see the README for examples.')
        return

    # Check for required options and arguments
    if not args.url and args.type not in ['daily', 'tinderbox', 'try'] \
       and not args.version:
        parser.error('The version of the application to download has not'
                     ' been specified.')

    # Instantiate scraper and download the build
    scraper_keywords = {'application': args.application,
                        'base_url': args.base_url,
                        'locale': args.locale,
                        'platform': args.platform,
                        'version': args.version,
                        'destination': args.destination,
                        'extension': args.extension,
                        'username': args.username,
                        'password': args.password,
                        'retry_attempts': args.retry_attempts,
                        'retry_delay': args.retry_delay,
                        'is_stub_installer': args.is_stub_installer,
                        'timeout': args.timeout,
                        'log_level': args.log_level}

    scraper_args = {
        'candidate': {'build_number': args.build_number},
        'daily': {'branch': args.branch,
                  'build_number': args.build_number,
                  'build_id': args.build_id,
                  'date': args.date},
        'tinderbox': {'branch': args.branch,
                      'build_number': args.build_number,
                      'date': args.date,
                      'debug_build': args.debug_build},
        'try': {'changeset': args.changeset,
                'debug_build': args.debug_build},
    }

    kwargs = scraper_keywords.copy()
    kwargs.update(scraper_args.get(args.type, {}))

    if args.application == 'b2g' and args.type in ('candidate', 'release'):
        error_msg = '%s build is not yet supported for B2G' % args.type
        raise errors.NotSupportedError(error_msg)
    if args.application == 'fennec' and args.type != 'daily':
        error_msg = '%s build is not yet supported for fennec' % args.type
        raise errors.NotSupportedError(error_msg)
    if args.url:
        build = scraper.DirectScraper(args.url, **kwargs)
    else:
        build = build_types[args.type](**kwargs)

    try:
        build.download()
    except KeyboardInterrupt:
        print('\nDownload interrupted by the user')


if __name__ == '__main__':
    cli()
