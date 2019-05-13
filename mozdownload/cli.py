# !/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tool to download different Gecko based applications (version {})."""

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import os
import sys

from mozdownload import factory, scraper

__version__ = '1.26.0'


def parse_arguments(argv):
    """Setup argument parser for command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.format(__version__))
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
    parser.add_argument('--build-number',
                        dest='build_number',
                        type=int,
                        metavar='BUILD_NUMBER',
                        help='Number of the build (for candidate, daily, and tinderbox builds)')
    parser.add_argument('--debug-build',
                        dest='debug_build',
                        action='store_true',
                        help='Download a debug build (for tinderbox, and try builds)')
    parser.add_argument('--destination', '-d',
                        dest='destination',
                        default=os.getcwd(),
                        metavar='DESTINATION',
                        help='Directory or file name to download the '
                             'file to, default: current working directory')
    parser.add_argument('--extension',
                        dest='extension',
                        metavar='EXTENSION',
                        help='File extension of the build (e.g. "zip"), default: '
                             'the standard build extension on the platform.')
    parser.add_argument('--locale', '-l',
                        dest='locale',
                        metavar='LOCALE',
                        help='Locale of the application, default: "en-US" or "multi"')
    parser.add_argument('--log-level',
                        action='store',
                        dest='log_level',
                        default=logging.INFO,
                        metavar='LOG_LEVEL',
                        help='Threshold for log output (default: INFO')
    parser.add_argument('--password',
                        dest='password',
                        metavar='PASSWORD',
                        help='Password for basic HTTP authentication.')
    parser.add_argument('--platform', '-p',
                        dest='platform',
                        choices=scraper.PLATFORM_FRAGMENTS.keys(),
                        metavar='PLATFORM',
                        help='Platform of the application')
    parser.add_argument('--print-url',
                        dest='print_url',
                        action='store_true',
                        help='Print final URL instead of downloading the file.')
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
    parser.add_argument('--revision',
                        dest='revision',
                        help='Revision of the build (for daily, tinderbox, and try builds)')
    parser.add_argument('--stub',
                        dest='is_stub_installer',
                        action='store_true',
                        help='Stub installer (Only applicable to Windows builds).')
    parser.add_argument('--timeout',
                        dest='timeout',
                        type=float,
                        metavar='TIMEOUT',
                        help='Amount of time (in seconds) until a download times out.')
    parser.add_argument('--type', '-t',
                        dest='scraper_type',
                        choices=factory.scraper_types.keys(),
                        default='release',
                        metavar='SCRAPER_TYPE',
                        help='Type of build to download, default: "%(default)s"')
    parser.add_argument('--url',
                        dest='url',
                        metavar='URL',
                        help='URL to download. Note: Reserved characters (such '
                             'as &) must be escaped or put in quotes otherwise '
                             'CLI output may be abnormal.')
    parser.add_argument('--username',
                        dest='username',
                        metavar='USERNAME',
                        help='Username for basic HTTP authentication.')
    parser.add_argument('--version', '-v',
                        dest='version',
                        metavar='VERSION',
                        help='Version of the application to be downloaded for release '
                             'and candidate builds (special values: %s)' % ', '.join(
                                scraper.RELEASE_AND_CANDIDATE_LATEST_VERSIONS.keys()))

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
                       help='ID of the build to download.')
    group.add_argument('--date',
                       dest='date',
                       metavar='DATE',
                       help='Date of the build, default: latest build')

    return vars(parser.parse_args(argv))


def cli(argv=None):
    """CLI entry point for mozdownload."""
    kwargs = parse_arguments(argv or sys.argv[1:])

    log_level = kwargs.pop('log_level')
    logging.basicConfig(format='%(levelname)s | %(message)s', level=log_level)
    logger = logging.getLogger(__name__)

    # Configure logging levels for sub modules. Set to ERROR by default.
    sub_log_level = logging.ERROR
    if log_level == logging.getLevelName(logging.DEBUG):
        sub_log_level = logging.DEBUG
    logging.getLogger('redo').setLevel(sub_log_level)
    logging.getLogger('requests').setLevel(sub_log_level)
    logging.getLogger('thclient').setLevel(sub_log_level)

    try:
        scraper_type = kwargs.pop('scraper_type')

        # If a URL has been specified use the direct scraper
        if kwargs.get('url'):
            scraper_type = 'direct'

        build = factory.FactoryScraper(scraper_type, **kwargs)
        if kwargs.get('print_url'):
            logger.info(build.url)
        else:
            build.download()
    except KeyboardInterrupt:
        logger.error('Download interrupted by the user')


if __name__ == '__main__':
    sys.exit(cli())
