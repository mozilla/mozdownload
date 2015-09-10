#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from optparse import OptionParser, OptionGroup
import os
import pkg_resources
import sys

from . import errors
from . import scraper


version = pkg_resources.require("mozdownload")[0].version

__doc__ = """
Module to handle downloads for different types of archive.mozilla.org hosted \
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

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('--application', '-a',
                      dest='application',
                      choices=scraper.APPLICATIONS,
                      default='firefox',
                      metavar='APPLICATION',
                      help='The name of the application to download, '
                           'default: "%default"')
    parser.add_option('--base_url',
                      dest='base_url',
                      default=scraper.BASE_URL,
                      metavar='BASE_URL',
                      help='The base url to be used, '
                           'default: "%default"')
    parser.add_option('--destination', '-d',
                      dest='destination',
                      default=os.getcwd(),
                      metavar='DESTINATION',
                      help='Directory or file name to download the '
                           'file to, default: current working directory')
    parser.add_option('--build-number',
                      dest='build_number',
                      type="int",
                      metavar='BUILD_NUMBER',
                      help='Number of the build (for candidate, daily, '
                           'and tinderbox builds)')
    parser.add_option('--locale', '-l',
                      dest='locale',
                      metavar='LOCALE',
                      help='Locale of the application, default: "en-US or '
                           'multi"')
    parser.add_option('--platform', '-p',
                      dest='platform',
                      choices=scraper.PLATFORM_FRAGMENTS.keys(),
                      metavar='PLATFORM',
                      help='Platform of the application')
    parser.add_option('--stub',
                      dest='is_stub_installer',
                      action='store_true',
                      help='Stub installer. '
                           'Only applicable to Windows builds.')
    parser.add_option('--type', '-t',
                      dest='type',
                      choices=build_types.keys(),
                      default='release',
                      metavar='BUILD_TYPE',
                      help='Type of build to download, default: "%default"')
    parser.add_option('--url',
                      dest='url',
                      metavar='URL',
                      help='URL to download. Note: Reserved characters (such '
                           'as &) must be escaped or put in quotes otherwise '
                           'CLI output may be abnormal.')
    parser.add_option('--version', '-v',
                      dest='version',
                      metavar='VERSION',
                      help='Version of the application to be used by release\
                            and candidate builds, i.e. "3.6"')
    parser.add_option('--extension',
                      dest='extension',
                      metavar='EXTENSION',
                      help='File extension of the build (e.g. "zip"), default:\
                            the standard build extension on the platform.')
    parser.add_option('--username',
                      dest='username',
                      metavar='USERNAME',
                      help='Username for basic HTTP authentication.')
    parser.add_option('--password',
                      dest='password',
                      metavar='PASSWORD',
                      help='Password for basic HTTP authentication.')
    parser.add_option('--retry-attempts',
                      dest='retry_attempts',
                      default=0,
                      type=int,
                      metavar='RETRY_ATTEMPTS',
                      help='Number of times the download will be attempted in '
                           'the event of a failure, default: %default')
    parser.add_option('--retry-delay',
                      dest='retry_delay',
                      default=10.,
                      type=float,
                      metavar='RETRY_DELAY',
                      help='Amount of time (in seconds) to wait between retry '
                           'attempts, default: %default')
    parser.add_option('--timeout',
                      dest='timeout',
                      type=float,
                      metavar='TIMEOUT',
                      help='Amount of time (in seconds) until a download times'
                           ' out')
    parser.add_option('--log-level',
                      action='store',
                      dest='log_level',
                      default='INFO',
                      metavar='LOG_LEVEL',
                      help='Threshold for log output (default: %default)')

    # Option group for daily builds
    group = OptionGroup(parser, "Daily builds",
                        "Extra options for daily builds.")
    group.add_option('--branch',
                     dest='branch',
                     default='mozilla-central',
                     metavar='BRANCH',
                     help='Name of the branch, default: "%default"')
    group.add_option('--build-id',
                     dest='build_id',
                     metavar='BUILD_ID',
                     help='ID of the build to download')
    group.add_option('--date',
                     dest='date',
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

    # Option group for try builds
    group = OptionGroup(parser, 'Try builds',
                        'Extra options for try builds.')
    group.add_option('--changeset',
                     dest='changeset',
                     help='Changeset of the try build to download')
    parser.add_option_group(group)

    # TODO: option group for nightly builds
    (options, args) = parser.parse_args()

    # Gives instructions to user when no arguments were passed
    if len(sys.argv) == 1:
        print __doc__
        parser.print_usage()
        print "Specify --help for more information on options. " \
              "Please see the README for examples."
        return

    # Check for required options and arguments
    # Note: Will be optional when ini file support has been landed
    if not options.url \
       and options.type not in ['daily', 'tinderbox', 'try'] \
       and not options.version:
        parser.error('The version of the application to download has not'
                     ' been specified.')

    # Instantiate scraper and download the build
    scraper_keywords = {'application': options.application,
                        'base_url': options.base_url,
                        'locale': options.locale,
                        'platform': options.platform,
                        'version': options.version,
                        'destination': options.destination,
                        'extension': options.extension,
                        'username': options.username,
                        'password': options.password,
                        'retry_attempts': options.retry_attempts,
                        'retry_delay': options.retry_delay,
                        'is_stub_installer': options.is_stub_installer,
                        'timeout': options.timeout,
                        'log_level': options.log_level}

    scraper_options = {
        'candidate': {'build_number': options.build_number},
        'daily': {'branch': options.branch,
                  'build_number': options.build_number,
                  'build_id': options.build_id,
                  'date': options.date},
        'tinderbox': {'branch': options.branch,
                      'build_number': options.build_number,
                      'date': options.date,
                      'debug_build': options.debug_build},
        'try': {'changeset': options.changeset,
                'debug_build': options.debug_build},
    }

    kwargs = scraper_keywords.copy()
    kwargs.update(scraper_options.get(options.type, {}))

    if options.application == 'b2g' and \
            options.type in ('candidate', 'release'):
        error_msg = "%s build is not yet supported for B2G" % options.type
        raise errors.NotSupportedError(error_msg)
    if options.application == 'fennec' and options.type != 'daily':
        error_msg = "%s build is not yet supported for fennec" % options.type
        raise errors.NotSupportedError(error_msg)
    if options.url:
        build = scraper.DirectScraper(options.url, **kwargs)
    else:
        build = build_types[options.type](**kwargs)

    try:
        build.download()
    except KeyboardInterrupt:
        print "\nDownload interrupted by the user"

if __name__ == "__main__":
    cli()
