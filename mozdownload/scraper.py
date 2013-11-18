#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from optparse import OptionParser, OptionGroup
import os
import pkg_resources
import re
import requests
import sys
import time
import urllib
from urlparse import urlparse

import mozinfo
import mozlog

from parser import DirectoryParser
from timezones import PacificTimezone
from utils import urljoin

import progressbar

version = pkg_resources.require("mozdownload")[0].version

__doc__ = """
Module to handle downloads for different types of ftp.mozilla.org hosted \
applications.

mozdownload version: %(version)s
""" % {'version': version}

APPLICATIONS = ['b2g', 'firefox', 'thunderbird']

# Base URL for the path to all builds
BASE_URL = 'https://ftp.mozilla.org/pub/mozilla.org'

# Chunk size when downloading a file
CHUNK_SIZE = 16 * 1024

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


class NotFoundError(Exception):
    """Exception for a resource not being found (e.g. no logs)"""
    def __init__(self, message, location):
        self.location = location
        Exception.__init__(self, ': '.join([message, location]))


class NotImplementedError(Exception):
    """Exception for a feature which is not implemented yet"""
    def __init__(self, message):
        Exception.__init__(self, message)


class TimeoutError(Exception):
    """Exception for a download exceeding the allocated timeout"""
    def __init__(self):
        self.message = 'The download exceeded the allocated timeout'
        Exception.__init__(self, self.message)


class Scraper(object):
    """Generic class to download an application from the Mozilla server"""

    def __init__(self, directory, version, platform=None,
                 application='firefox', locale='en-US', extension=None,
                 authentication=None, retry_attempts=0, retry_delay=10.,
                 is_stub_installer=False, timeout=None, log_level='INFO',
                 base_url=BASE_URL):

        # Private properties for caching
        self._target = None
        self._binary = None

        self.directory = directory
        self.locale = locale
        self.platform = platform or self.detect_platform()
        self.version = version
        self.extension = extension or DEFAULT_FILE_EXTENSIONS[self.platform]
        self.authentication = authentication
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.is_stub_installer = is_stub_installer
        self.timeout_download = timeout
        self.timeout_network = 60.

        self.logger = mozlog.getLogger(' ')
        self.logger.setLevel(getattr(mozlog, log_level.upper()))

        # build the base URL
        self.application = application
        self.base_url = urljoin(base_url, self.application)

        attempt = 0
        while True:
            attempt += 1
            try:
                self.get_build_info()
                break
            except (NotFoundError, requests.exceptions.RequestException), e:
                if self.retry_attempts > 0:
                    # Log only if multiple attempts are requested
                    self.logger.warning("Build not found: '%s'" % e.message)
                    self.logger.info('Will retry in %s seconds...' %
                                     (self.retry_delay))
                    time.sleep(self.retry_delay)
                    self.logger.info("Retrying... (attempt %s)" % attempt)

                if attempt >= self.retry_attempts:
                    if hasattr(e, 'response') and \
                            e.response.status_code == 404:
                        message = "Specified build has not been found"
                        raise NotFoundError(message, e.response.url)
                    else:
                        raise

    @property
    def binary(self):
        """Return the name of the build"""

        attempt = 0

        while self._binary is None:
            attempt += 1
            try:
                # Retrieve all entries from the remote virtual folder
                parser = DirectoryParser(self.path,
                                         authentication=self.authentication,
                                         timeout=self.timeout_network)
                if not parser.entries:
                    raise NotFoundError('No entries found', self.path)

                # Download the first matched directory entry
                pattern = re.compile(self.binary_regex, re.IGNORECASE)
                for entry in parser.entries:
                    try:
                        self._binary = pattern.match(entry).group()
                        break
                    except:
                        # No match, continue with next entry
                        continue
                else:
                    raise NotFoundError("Binary not found in folder",
                                        self.path)
            except (NotFoundError, requests.exceptions.RequestException), e:
                if self.retry_attempts > 0:
                    # Log only if multiple attempts are requested
                    self.logger.warning("Build not found: '%s'" % e.message)
                    self.logger.info('Will retry in %s seconds...' %
                                     (self.retry_delay))
                    time.sleep(self.retry_delay)
                    self.logger.info("Retrying... (attempt %s)" % attempt)

                if attempt >= self.retry_attempts:
                    if hasattr(e, 'response') and \
                            e.response.status_code == 404:
                        message = "Specified build has not been found"
                        raise NotFoundError(message, self.path)
                    else:
                        raise

        return self._binary

    @property
    def binary_regex(self):
        """Return the regex for the binary filename"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def final_url(self):
        """Return the final URL of the build"""

        return urljoin(self.path, self.binary)

    @property
    def path(self):
        """Return the path to the build"""

        return urljoin(self.base_url, self.path_regex)

    @property
    def path_regex(self):
        """Return the regex for the path to the build"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        return PLATFORM_FRAGMENTS[self.platform]

    @property
    def target(self):
        """Return the target file name of the build"""

        if self._target is None:
            self._target = os.path.join(self.directory,
                                        self.build_filename(self.binary))
        return self._target

    def get_build_info(self):
        """Returns additional build information in subclasses if necessary"""
        pass

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        raise NotImplementedError(sys._getframe(0).f_code.co_name)

    def detect_platform(self):
        """Detect the current platform"""

        # For Mac and Linux 32bit we do not need the bits appended
        if mozinfo.os == 'mac' or \
                (mozinfo.os == 'linux' and mozinfo.bits == 32):
            return mozinfo.os
        else:
            return "%s%d" % (mozinfo.os, mozinfo.bits)

    def download(self):
        """Download the specified file"""

        def total_seconds(td):
            # Keep backward compatibility with Python 2.6 which doesn't have
            # this method
            if hasattr(td, 'total_seconds'):
                return td.total_seconds()
            else:
                return (td.microseconds +
                        (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6

        attempt = 0

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        # Don't re-download the file
        if os.path.isfile(os.path.abspath(self.target)):
            self.logger.info("File has already been downloaded: %s" %
                             (self.target))
            return

        self.logger.info('Downloading from: %s' %
                         (urllib.unquote(self.final_url)))
        tmp_file = self.target + ".part"

        while True:
            attempt += 1
            try:
                start_time = datetime.now()

                # Enable streaming mode so we can download content in chunks
                r = requests.get(self.final_url, stream=True,
                                 auth=self.authentication)
                r.raise_for_status()

                # ValueError: Value out of range if only total_size given
                total_size = int(r.headers.get('Content-length').strip())
                max_value = ((total_size / CHUNK_SIZE) + 1) * CHUNK_SIZE
                bytes_downloaded = 0
                widgets = [progressbar.Percentage(), ' ', progressbar.Bar(),
                           ' ', progressbar.ETA(), ' ',
                           progressbar.FileTransferSpeed()]
                pbar = progressbar.ProgressBar(widgets=widgets,
                                               maxval=max_value).start()

                with open(tmp_file, 'wb') as f:
                    for chunk in iter(lambda: r.raw.read(CHUNK_SIZE), ''):
                        f.write(chunk)
                        bytes_downloaded += CHUNK_SIZE
                        pbar.update(bytes_downloaded)

                        t1 = total_seconds(datetime.now() - start_time)
                        if self.timeout_download and \
                                t1 >= self.timeout_download:
                            raise TimeoutError
                pbar.finish()
                break
            except (requests.exceptions.RequestException, TimeoutError), e:
                if tmp_file and os.path.isfile(tmp_file):
                    os.remove(tmp_file)
                if self.retry_attempts > 0:
                    # Log only if multiple attempts are requested
                    self.logger.warning('Download failed: "%s"' % e.message)
                    self.logger.info('Will retry in %s seconds...' %
                                     (self.retry_delay))
                    time.sleep(self.retry_delay)
                    self.logger.info("Retrying... (attempt %s)" % attempt)
                if attempt >= self.retry_attempts:
                    raise
                time.sleep(self.retry_delay)

        os.rename(tmp_file, self.target)

    def show_matching_builds(self, builds):
        """Output the matching builds"""
        self.logger.info('Found %s build%s: %s' % (
            len(builds),
            len(builds) > 1 and 's' or '',
            len(builds) > 10 and
            ' ... '.join([', '.join(builds[:5]), ', '.join(builds[-5:])]) or
            ', '.join(builds)))


class DailyScraper(Scraper):
    """Class to download a daily build from the Mozilla server"""

    def __init__(self, branch='mozilla-central', build_id=None, date=None,
                 build_number=None, *args, **kwargs):

        self.branch = branch
        self.build_id = build_id
        self.date = date
        self.build_number = build_number

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Defines additional build information"""

        # Internally we access builds via index
        if self.build_number is not None:
            self.build_index = int(self.build_number) - 1
        else:
            self.build_index = None

        if self.build_id:
            # A build id has been specified. Split up its components so the
            # date and time can be extracted:
            # '20111212042025' -> '2011-12-12 04:20:25'
            self.date = datetime.strptime(self.build_id, '%Y%m%d%H%M%S')

        elif self.date:
            # A date (without time) has been specified. Use its value and the
            # build index to find the requested build for that day.
            self.date = datetime.strptime(self.date, '%Y-%m-%d')

        else:
            # If no build id nor date have been specified the latest available
            # build of the given branch has to be identified. We also have to
            # retrieve the date of the build via its build id.
            self.date = self.get_latest_build_date()

        self.builds, self.build_index = self.get_build_info_for_date(
            self.date, self.build_index)

    def get_latest_build_date(self):
        """ Returns date of latest available nightly build."""
        url = urljoin(self.base_url, 'nightly', 'latest-%s/' % self.branch)

        self.logger.info('Retrieving the build status file from %s' % url)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        parser.entries = parser.filter(r'.*%s\.txt' % self.platform_regex)
        if not parser.entries:
            message = 'Status file for %s build cannot be found' % \
                self.platform_regex
            raise NotFoundError(message, url)

        # Read status file for the platform, retrieve build id,
        # and convert to a date
        headers = {'Cache-Control': 'max-age=0'}
        r = requests.get(url + parser.entries[-1],
                         auth=self.authentication, headers=headers)
        r.raise_for_status()

        return datetime.strptime(r.text.split('\n')[0], '%Y%m%d%H%M%S')

    def is_build_dir(self, dir):
        """Return whether or not the given dir contains a build."""

        url = urljoin(self.base_url, self.monthly_build_list_regex, dir)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)

        pattern = re.compile(self.binary_regex, re.IGNORECASE)
        for entry in parser.entries:
            try:
                pattern.match(entry).group()
                return True
            except:
                # No match, continue with next entry
                continue
        return False

    def get_build_info_for_date(self, date, build_index=None):
        url = urljoin(self.base_url, self.monthly_build_list_regex)
        has_time = date and date.time()

        self.logger.info('Retrieving list of builds from %s' % url)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        regex = r'%(DATE)s-(\d+-)+%(BRANCH)s%(L10N)s$' % {
            'DATE': date.strftime('%Y-%m-%d'),
            'BRANCH': self.branch,
            'L10N': '' if self.locale == 'en-US' else '(-l10n)?'}
        parser.entries = parser.filter(regex)
        parser.entries = parser.filter(self.is_build_dir)

        if has_time:
            # If a time is included in the date, use it to determine the
            # build's index
            regex = r'.*%s.*' % date.strftime('%H-%M-%S')
            parser.entries = parser.filter(regex)

        if not parser.entries:
            date_format = '%Y-%m-%d-%H-%M-%S' if has_time else '%Y-%m-%d'
            message = 'Folder for builds on %s has not been found' % \
                self.date.strftime(date_format)
            raise NotFoundError(message, url)

        # If no index has been given, set it to the last build of the day.
        self.show_matching_builds(parser.entries)
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
                        'win32': r'(\.installer%(STUB)s)?\.%(EXT)s$',
                        'win64': r'(\.installer%(STUB)s)?\.%(EXT)s$'}
        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'APP': self.application,
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'EXT': self.extension,
                        'STUB': '-stub' if self.is_stub_installer else ''}

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
        """Return the regex for the folder containing builds of a month."""

        # Regex for possible builds for the given date
        return r'nightly/%(YEAR)s/%(MONTH)s' % {
            'YEAR': self.date.year,
            'MONTH': str(self.date.month).zfill(2)}

    @property
    def path_regex(self):
        """Return the regex for the path"""

        try:
            path = urljoin(self.monthly_build_list_regex,
                           self.builds[self.build_index])
            return path
        except:
            folder = urljoin(self.base_url, self.monthly_build_list_regex)
            raise NotFoundError("Specified sub folder cannot be found",
                                folder)


class DirectScraper(Scraper):
    """Class to download a file from a specified URL"""

    def __init__(self, url, *args, **kwargs):
        self.url = url

        Scraper.__init__(self, *args, **kwargs)

    @property
    def target(self):
        target = urlparse(self.final_url)
        filename = target.path.rpartition('/')[-1] or target.hostname
        return os.path.join(self.directory, filename)

    @property
    def final_url(self):
        return self.url


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
                 'win32': r'^%(APP)s.*%(STUB)s.*\.%(EXT)s$',
                 'win64': r'^%(APP)s.*%(STUB)s.*\.%(EXT)s$'}
        return regex[self.platform] % {
            'APP': self.application,
            'EXT': self.extension,
            'STUB': 'Stub' if self.is_stub_installer else ''}

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

        self.build_number = build_number
        self.no_unsigned = no_unsigned
        self.unsigned = False

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        "Defines additional build information"

        # Internally we access builds via index
        self.builds, self.build_index = self.get_build_info_for_version(
            self.version)
        if self.build_number is not None:
            self.builds = ['build%s' % self.build_number]
            self.build_index = 0

    def get_build_info_for_version(self, version, build_index=None):
        url = urljoin(self.base_url, self.candidate_build_list_regex)

        self.logger.info('Retrieving list of candidate builds from %s' % url)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        if not parser.entries:
            message = 'Folder for specific candidate builds at %s has not' \
                'been found' % url
            raise NotFoundError(message, url)

        self.show_matching_builds(parser.entries)

        # If no index has been given, set it to the last build of the given
        # version.
        if build_index is None:
            build_index = len(parser.entries) - 1

        return (parser.entries, build_index)

    @property
    def candidate_build_list_regex(self):
        """Return the regex for the folder which contains the builds of
           a candidate build."""

        # Regex for possible builds for the given date
        return r'nightly/%(VERSION)s-candidates/' % {
            'VERSION': self.version}

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

        template = '%(APP)s-%(VERSION)s-%(BUILD)s.%(LOCALE)s.' \
                   '%(PLATFORM)s.%(EXT)s'
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
        except NotFoundError, e:
            self.logger.exception(str(e))

            # If the signed build cannot be downloaded and unsigned builds are
            # allowed, try to download the unsigned build instead
            if self.no_unsigned:
                raise
            else:
                self.logger.warning("Signed build has not been found. "
                                    "Falling back to unsigned build.")
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

        self.branch = branch
        self.build_number = build_number
        self.debug_build = debug_build
        self.date = date

        self.timestamp = None
        # Currently any time in RelEng is based on the Pacific time zone.
        self.timezone = PacificTimezone()

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        "Defines additional build information"

        # Internally we access builds via index
        if self.build_number is not None:
            self.build_index = int(self.build_number) - 1
        else:
            self.build_index = None

        if self.date is not None:
            try:
                # date is provided in the format 2013-07-23
                self.date = datetime.strptime(self.date, '%Y-%m-%d')
            except:
                # date is provided as a unix timestamp
                self.timestamp = self.date

        self.locale_build = self.locale != 'en-US'
        # For localized builds we do not have to retrieve the list of builds
        # because only the last build is available
        if not self.locale_build:
            self.builds, self.build_index = self.get_build_info_for_index(
                self.build_index)

    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex_base_name = r'^%(APP)s-.*\.%(LOCALE)s\.%(PLATFORM)s'
        regex_suffix = {'linux': r'.*\.%(EXT)s$',
                        'linux64': r'.*\.%(EXT)s$',
                        'mac': r'.*\.%(EXT)s$',
                        'mac64': r'.*\.%(EXT)s$',
                        'win32': r'.*(\.installer%(STUB)s)\.%(EXT)s$',
                        'win64': r'.*(\.installer%(STUB)s)\.%(EXT)s$'}

        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'APP': self.application,
                        'LOCALE': self.locale,
                        'PLATFORM': PLATFORM_FRAGMENTS[self.platform],
                        'STUB': '-stub' if self.is_stub_installer else '',
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

        return regex % {
            'BRANCH': self.branch,
            'PLATFORM': '' if self.locale_build else self.platform_regex,
            'L10N': 'l10n' if self.locale_build else '',
            'DEBUG': '-debug' if self.debug_build else ''}

    def date_matches(self, timestamp):
        """
        Determines whether the timestamp date is equal to the argument date
        """

        if self.date is None:
            return False

        timestamp = datetime.fromtimestamp(float(timestamp), self.timezone)
        if self.date.date() == timestamp.date():
            return True

        return False

    def detect_platform(self):
        """Detect the current platform"""

        platform = Scraper.detect_platform(self)

        # On OS X we have to special case the platform detection code and
        # fallback to 64 bit builds for the en-US locale
        if mozinfo.os == 'mac' and self.locale == 'en-US' and \
                mozinfo.bits == 64:
            platform = "%s%d" % (mozinfo.os, mozinfo.bits)

        return platform

    def get_build_info_for_index(self, build_index=None):
        url = urljoin(self.base_url, self.build_list_regex)

        self.logger.info('Retrieving list of builds from %s' % url)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        parser.entries = parser.filter(r'^\d+$')

        if self.timestamp:
            # If a timestamp is given, retrieve the folder with the timestamp
            # as name
            parser.entries = self.timestamp in parser.entries and \
                [self.timestamp]

        elif self.date:
            # If date is given, retrieve the subset of builds on that date
            parser.entries = filter(self.date_matches, parser.entries)

        if not parser.entries:
            message = 'No builds have been found'
            raise NotFoundError(message, url)

        self.show_matching_builds(parser.entries)

        # If no index has been given, set it to the last build of the day.
        if build_index is None:
            build_index = len(parser.entries) - 1

        return (parser.entries, build_index)

    @property
    def path_regex(self):
        """Return the regex for the path"""

        if self.locale_build:
            return self.build_list_regex

        return urljoin(self.build_list_regex, self.builds[self.build_index])

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
                   'tinderbox': TinderboxScraper}

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
    parser.add_option('--stub',
                      dest='is_stub_installer',
                      action='store_true',
                      help='Stub installer. '
                           'Only applicable to Windows builds.')
    parser.add_option('--type', '-t',
                      dest='type',
                      choices=BUILD_TYPES.keys(),
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
       and not options.type in ['daily', 'tinderbox'] \
       and not options.version:
        parser.error('The version of the application to download has not'
                     ' been specified.')

    # Instantiate scraper and download the build
    scraper_keywords = {'application': options.application,
                        'locale': options.locale,
                        'platform': options.platform,
                        'version': options.version,
                        'directory': options.directory,
                        'extension': options.extension,
                        'authentication': (options.username, options.password),
                        'retry_attempts': options.retry_attempts,
                        'retry_delay': options.retry_delay,
                        'is_stub_installer': options.is_stub_installer,
                        'timeout': options.timeout,
                        'log_level': options.log_level}

    scraper_options = {
        'candidate': {'build_number': options.build_number,
                      'no_unsigned': options.no_unsigned},
        'daily': {'branch': options.branch,
                  'build_number': options.build_number,
                  'build_id': options.build_id,
                  'date': options.date},
        'tinderbox': {'branch': options.branch,
                      'build_number': options.build_number,
                      'date': options.date,
                      'debug_build': options.debug_build}
    }

    kwargs = scraper_keywords.copy()
    kwargs.update(scraper_options.get(options.type, {}))

    if options.url:
        build = DirectScraper(options.url, **kwargs)
    else:
        build = BUILD_TYPES[options.type](**kwargs)

    build.download()

if __name__ == "__main__":
    cli()
