#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to handle downloads for different types of Firefox and Thunderbird builds."""


from datetime import datetime
from optparse import OptionParser, OptionGroup
import os
import re
import sys
import urllib

import mozinfo

from parser import DirectoryParser
from timezones import PacificTimezone


APPLICATIONS = ['b2g', 'firefox', 'thunderbird']

# Base URL for the path to all builds
BASE_URL = 'https://ftp.mozilla.org/pub/mozilla.org'

PLATFORM_FRAGMENTS = {'linux': 'linux-i686',
                      'linux64': 'linux-x86_64',
                      'mac': 'mac',
                      'mac64': 'mac64',
                      'win32': 'win32',
                      'win64': 'win64-x86_64'}

DEFAULT_FILE_EXTENSIONS = {'linux': 'tar.bz2',
                           'linux64': 'tar.bz2',
                           'mac': 'dmg',
                           'mac64': 'dmg',
                           'win32': 'exe',
                           'win64': 'exe'}

class NotFoundException(Exception):
    """Exception for a resource not being found (e.g. no logs)"""
    def __init__(self, message, location):
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))


class Scraper(object):
    """Generic class to download an application from the Mozilla server"""

    def __init__(self, directory, version, platform=None,
                 application='firefox', locale='en-US', extension=None):

        # Private properties for caching
        self._target = None
        self._binary = None

        self.directory = directory
        self.locale = locale
        self.platform = platform or self.detect_platform()
        self.version = version
        self.extension = extension or DEFAULT_FILE_EXTENSIONS[self.platform]

        # build the base URL
        self.application = application
        self.base_url = '/'.join([BASE_URL, self.application])


    @property
    def binary(self):
        """Return the name of the build"""

        if self._binary is None:
            # Retrieve all entries from the remote virtual folder
            parser = DirectoryParser(self.path)
            if not parser.entries:
                raise NotFoundException('No entries found', self.path)
    
            # Download the first matched directory entry
            pattern = re.compile(self.binary_regex, re.IGNORECASE)
            for entry in parser.entries:
                try:
                    self._binary = pattern.match(entry).group()
                    break
                except:
                    # No match, continue with next entry
                    continue

        if self._binary is None:
            raise NotFoundException("Binary not found in folder", self.path)
        else:
            return self._binary


    @property
    def binary_regex(self):
        """Return the regex for the binary filename"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    @property
    def final_url(self):
        """Return the final URL of the build"""

        return '/'.join([self.path, self.binary])


    @property
    def path(self):
        """Return the path to the build"""

        return '/'.join([self.base_url, self.path_regex])


    @property
    def path_regex(self):
        """Return the regex for the path to the build"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        return PLATFORM_FRAGMENTS[self.platform];


    @property
    def target(self):
        """Return the target file name of the build"""

        if self._target is None:
            self._target = os.path.join(self.directory,
                                        self.build_filename(self.binary))
        return self._target


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)


    def detect_platform(self):
        """Detect the current platform"""

        # For Mac and Linux 32bit we do not need the bits appended
        if mozinfo.os == 'mac' or (mozinfo.os == 'linux' and mozinfo.bits == 32):
            return mozinfo.os
        else:
            return "%s%d" % (mozinfo.os, mozinfo.bits)


    def download(self):
        """Download the specified file"""

        tmp_file = None

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        try:
            # Don't re-download the build
            if os.path.isfile(os.path.abspath(self.target)):
                print "Build has already been downloaded: %s" % (self.target)
                return

            print 'Downloading build: %s' % (urllib.unquote(self.final_url))
            tmp_file = self.target + ".part"
            urllib.urlretrieve(self.final_url, tmp_file)
            os.rename(tmp_file, self.target)
        except:
            try:
                if tmp_file:
                    os.remove(tmp_file)
            except OSError:
                pass

            raise


class DailyScraper(Scraper):
    """Class to download a daily build from the Mozilla server"""

    def __init__(self, branch='mozilla-central', build_id=None, date=None,
                 build_number=None, *args, **kwargs):

        Scraper.__init__(self, *args, **kwargs)
        self.branch = branch

        # Internally we access builds via index
        if build_number is not None:
            self.build_index = int(build_number) - 1
        else:
            self.build_index = None

        if build_id:
            # A build id has been specified. Split up its components so the date
            # and time can be extracted: '20111212042025' -> '2011-12-12 04:20:25'
            self.date = datetime.strptime(build_id, '%Y%m%d%H%M%S')
            self.builds, self.build_index = self.get_build_info_for_date(self.date,
                                                                         has_time=True)

        elif date:
            # A date (without time) has been specified. Use its value and the
            # build index to find the requested build for that day.
            self.date = datetime.strptime(date, '%Y-%m-%d')
            self.builds, self.build_index = self.get_build_info_for_date(self.date,
                                                                         build_index=self.build_index)

        else:
            # If no build id nor date have been specified the lastest available
            # build of the given branch has to be identified. We also have to
            # retrieve the date of the build via its build id.
            url = '%s/nightly/latest-%s/' % (self.base_url, self.branch)

            print 'Retrieving the build status file from %s' % url
            parser = DirectoryParser(url)
            parser.entries = parser.filter(r'.*%s\.txt' % self.platform_regex)
            if not parser.entries:
                message = 'Status file for %s build cannot be found' % self.platform_regex
                raise NotFoundException(message, url)

            # Read status file for the platform, retrieve build id, and convert to a date
            status_file = url + parser.entries[-1]
            f = urllib.urlopen(status_file)
            self.date = datetime.strptime(f.readline().strip(), '%Y%m%d%H%M%S')
            self.builds, self.build_index = self.get_build_info_for_date(self.date,
                                                                         has_time=True)


    def get_build_info_for_date(self, date, has_time=False, build_index=None):
        url = '/'.join([self.base_url, self.monthly_build_list_regex])

        print 'Retrieving list of builds from %s' % url
        parser = DirectoryParser(url)
        regex = r'%(DATE)s-(\d+-)+%(BRANCH)s%(L10N)s$' % {
                    'DATE': date.strftime('%Y-%m-%d'),
                    'BRANCH': self.branch,
                    'L10N': '' if self.locale == 'en-US' else '-l10n'}
        parser.entries = parser.filter(regex)
        if not parser.entries:
            message = 'Folder for builds on %s has not been found' % self.date.strftime('%Y-%m-%d')
            raise NotFoundException(message, url)

        if has_time:
            # If a time is included in the date, use it to determine the build's index
            regex = r'.*%s.*' % date.strftime('%H-%M-%S')
            build_index = parser.entries.index(parser.filter(regex)[0])
        else:
            # If no index has been given, set it to the last build of the day.
            if build_index is None:
                build_index = len(parser.entries) - 1

        return (parser.entries, build_index)


    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex_base_name = r'^%(APP)s-.*\.%(LOCALE)s\.%(PLATFORM)s'
        regex_suffix = {'linux': r'\.%(EXT)s$',
                        'linux64': r'\.%(EXT)s$',
                        'mac': r'\.%(EXT)s$',
                        'mac64': r'\.%(EXT)s$',
                        'win32': r'(\.installer)\.%(EXT)s$',
                        'win64': r'(\.installer)\.%(EXT)s$'}
        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'APP': self.application,
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'EXT': self.extension}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        try:
            # Get exact timestamp of the build to build the local file name
            folder = self.builds[self.build_index]
            timestamp = re.search('([\d\-]+)-\D.*', folder).group(1)
        except:
            # If it's not available use the build's date
            timestamp = self.date.strftime('%Y-%m-%d')

        return '%(TIMESTAMP)s-%(BRANCH)s-%(NAME)s' % {
                   'TIMESTAMP': timestamp,
                   'BRANCH': self.branch,
                   'NAME': binary}


    @property
    def monthly_build_list_regex(self):
        """Return the regex for the folder which contains the builds of a month."""

        # Regex for possible builds for the given date
        return r'nightly/%(YEAR)s/%(MONTH)s/' % {
                  'YEAR': self.date.year,
                  'MONTH': str(self.date.month).zfill(2) }


    @property
    def path_regex(self):
        """Return the regex for the path"""

        try:
            return self.monthly_build_list_regex + self.builds[self.build_index]
        except:
            raise NotFoundException("Specified sub folder cannot be found",
                                    self.base_url + self.monthly_build_list_regex)


class ReleaseScraper(Scraper):
    """Class to download a release build from the Mozilla server"""

    def __init__(self, *args, **kwargs):
        Scraper.__init__(self, *args, **kwargs)

    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex = {'linux': r'^%(APP)s-.*\.%(EXT)s$',
                 'linux64': r'^%(APP)s-.*\.%(EXT)s$',
                 'mac': r'^%(APP)s.*\.%(EXT)s$',
                 'mac64': r'^%(APP)s.*\.%(EXT)s$',
                 'win32': r'^%(APP)s.*\.%(EXT)s$',
                 'win64': r'^%(APP)s.*\.%(EXT)s$'}
        return regex[self.platform] % {'APP': self.application,
                                       'EXT': self.extension}


    @property
    def path_regex(self):
        """Return the regex for the path"""

        regex = r'releases/%(VERSION)s/%(PLATFORM)s/%(LOCALE)s'
        return regex % {'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'VERSION': self.version}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s.%(LOCALE)s.%(PLATFORM)s.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'EXT': self.extension}


class ReleaseCandidateScraper(ReleaseScraper):
    """Class to download a release candidate build from the Mozilla server"""

    def __init__(self, build_number=None, no_unsigned=False, *args, **kwargs):
        Scraper.__init__(self, *args, **kwargs)

        # Internally we access builds via index
        if build_number is not None:
            self.build_index = int(build_number) - 1
        else:
            self.build_index = None

        self.builds, self.build_index = self.get_build_info_for_version(self.version, self.build_index)

        self.no_unsigned = no_unsigned
        self.unsigned = False


    def get_build_info_for_version(self, version, build_index=None):
        url = '/'.join([self.base_url, self.candidate_build_list_regex])

        print 'Retrieving list of candidate builds from %s' % url
        parser = DirectoryParser(url)
        if not parser.entries:
            message = 'Folder for specific candidate builds at has not been found'
            raise NotFoundException(message, url)

        # If no index has been given, set it to the last build of the given version.
        if build_index is None:
            build_index = len(parser.entries) - 1

        return (parser.entries, build_index)


    @property
    def candidate_build_list_regex(self):
        """Return the regex for the folder which contains the builds of
           a candidate build."""

        # Regex for possible builds for the given date
        return r'nightly/%(VERSION)s-candidates/' % {
                 'VERSION': self.version }


    @property
    def path_regex(self):
        """Return the regex for the path"""

        regex = r'%(PREFIX)s%(BUILD)s/%(UNSIGNED)s%(PLATFORM)s/%(LOCALE)s'
        return regex % {'PREFIX': self.candidate_build_list_regex,
                        'BUILD': self.builds[self.build_index],
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'UNSIGNED': "unsigned/" if self.unsigned else ""}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s-build%(BUILD)s.%(LOCALE)s.%(PLATFORM)s.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'BUILD': self.builds[self.build_index],
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'EXT': self.extension}


    def download(self):
        """Download the specified file"""

        try:
            # Try to download the signed candidate build
            Scraper.download(self)
        except NotFoundException, e:
            print str(e)

            # If the signed build cannot be downloaded and unsigned builds are
            # allowed, try to download the unsigned build instead
            if self.no_unsigned:
                raise
            else:
                print "Signed build has not been found. Falling back to unsigned build."
                self.unsigned = True
                Scraper.download(self)


class TinderboxScraper(Scraper):
    """Class to download a tinderbox build from the Mozilla server.

    There are two ways to specify a unique build:
    1. If the date (%Y-%m-%d) is given and build_number is given where
       the build_number is the index of the build on the date
    2. If the build timestamp (UNIX) is given, and matches a specific build.
    """

    def __init__(self, branch='mozilla-central', build_number=None, date=None,
                 debug_build=False, *args, **kwargs):
        Scraper.__init__(self, *args, **kwargs)

        self.branch = branch
        self.debug_build = debug_build
        self.locale_build = self.locale != 'en-US'
        self.timestamp = None

        # Currently any time in RelEng is based on the Pacific time zone.
        self.timezone = PacificTimezone();

        # Internally we access builds via index
        if build_number is not None:
            self.build_index = int(build_number) - 1
        else:
            self.build_index = None

        if date is not None:
            try:
                self.date = datetime.fromtimestamp(float(date), self.timezone)
                self.timestamp = date
            except:
                self.date = datetime.strptime(date, '%Y-%m-%d')
        else:
            self.date = None

        # For localized builds we do not have to retrieve the list of builds
        # because only the last build is available
        if not self.locale_build:
            self.builds, self.build_index = self.get_build_info(self.build_index)
    
            try:
                self.timestamp = self.builds[self.build_index]
            except:
                raise NotFoundException("Specified sub folder cannot be found",
                                        self.base_url + self.monthly_build_list_regex)


    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex_base_name = r'^%(APP)s-.*\.%(LOCALE)s\.'
        regex_suffix = {'linux': r'.*\.%(EXT)s$',
                        'linux64': r'.*\.%(EXT)s$',
                        'mac': r'.*\.%(EXT)s$',
                        'mac64': r'.*\.%(EXT)s$',
                        'win32': r'.*\.%(EXT)s$',
                        'win64': r'.*\.%(EXT)s$'}

        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'APP': self.application,
                        'LOCALE': self.locale,
                        'EXT': self.extension}


    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        return '%(TIMESTAMP)s%(BRANCH)s%(DEBUG)s-%(NAME)s' % {
                   'TIMESTAMP': self.timestamp + '-' if self.timestamp else '',
                   'BRANCH': self.branch,
                   'DEBUG': '-debug' if self.debug_build else '',
                   'NAME': binary}


    @property
    def build_list_regex(self):
        """Return the regex for the folder which contains the list of builds"""

        regex = 'tinderbox-builds/%(BRANCH)s-%(PLATFORM)s%(L10N)s%(DEBUG)s'

        return regex % {'BRANCH': self.branch,
                        'PLATFORM': '' if self.locale_build else self.platform_regex,
                        'L10N': 'l10n' if self.locale_build else '',
                        'DEBUG': '-debug' if self.debug_build else ''}


    def date_matches(self, timestamp):
        """Determines whether the timestamp date is equal to the argument date"""

        if self.date is None:
            return False

        timestamp = datetime.fromtimestamp(float(timestamp), self.timezone)
        if self.date.date() == timestamp.date():
            return True
        
        return False


    @property
    def date_validation_regex(self):
        """Return the regex for a valid date argument value"""

        return r'^\d{4}-\d{1,2}-\d{1,2}$|^\d+$'


    def detect_platform(self):
        """Detect the current platform"""

        platform = Scraper.detect_platform(self)

        # On OS X we have to special case the platform detection code and fallback
        # to 64 bit builds for the en-US locale
        if mozinfo.os == 'mac' and self.locale == 'en-US' and mozinfo.bits == 64:
            platform = "%s%d" % (mozinfo.os, mozinfo.bits)

        return platform


    def get_build_info(self, build_index=None):
        url = '/'.join([self.base_url, self.build_list_regex])

        print 'Retrieving list of builds from %s' % url

        # If a timestamp is given, retrieve just that build
        regex = '^' + self.timestamp + '$' if self.timestamp else r'^\d+$'

        parser = DirectoryParser(url)
        parser.entries = parser.filter(regex)

        # If date is given, retrieve the subset of builds on that date
        if self.date is not None:
            parser.entries = filter(self.date_matches, parser.entries)

        if not parser.entries:
            message = 'No builds have been found'
            raise NotFoundException(message, url)

        # If no index has been given, set it to the last build of the day.
        if build_index is None:
            build_index = len(parser.entries) - 1

        return (parser.entries, build_index)


    @property
    def path_regex(self):
        """Return the regex for the path"""

        if self.locale_build:
            return self.build_list_regex

        return '/'.join([self.build_list_regex, self.builds[self.build_index]])


    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        PLATFORM_FRAGMENTS = {'linux': 'linux',
                              'linux64': 'linux64',
                              'mac': 'macosx',
                              'mac64': 'macosx64',
                              'win32': 'win32',
                              'win64': 'win64'}

        return PLATFORM_FRAGMENTS[self.platform]


def cli():
    """Main function for the downloader"""

    BUILD_TYPES = {'release': ReleaseScraper,
                   'candidate': ReleaseCandidateScraper,
                   'daily': DailyScraper,
                   'tinderbox': TinderboxScraper }

    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('--application', '-a',
                      dest='application',
                      choices=APPLICATIONS,
                      default='firefox',
                      metavar='APPLICATION',
                      help='The name of the application to download, '
                           'default: "%default"')
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
                      help='Locale of the application, default: "%default"')
    parser.add_option('--platform', '-p',
                      dest='platform',
                      choices=PLATFORM_FRAGMENTS.keys(),
                      metavar='PLATFORM',
                      help='Platform of the application')
    parser.add_option('--type', '-t',
                      dest='type',
                      choices=BUILD_TYPES.keys(),
                      default='release',
                      metavar='BUILD_TYPE',
                      help='Type of build to download, default: "%default"')
    parser.add_option('--version', '-v',
                      dest='version',
                      metavar='VERSION',
                      help='Version of the application to be used by release and\
                            candidate builds, i.e. "3.6"')
    parser.add_option('--extension',
                      dest='extension',
                      default=None,
                      metavar='EXTENSION',
                      help='File extension of the build (e.g. "zip"), default:\
                            the standard build extension on the platform.')

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
                     help='Name of the branch, default: "%default"')
    group.add_option('--build-id',
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
                        'directory': options.directory,
                        'extension': options.extension}
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
