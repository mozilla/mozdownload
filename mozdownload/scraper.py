# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
import logging
import os
import re
import requests
import sys
import time
import urllib
from urlparse import urlparse

import mozinfo
import progressbar as pb

import errors

from parser import DirectoryParser
from timezones import PacificTimezone
from utils import urljoin


APPLICATIONS = ('b2g', 'firefox', 'fennec', 'thunderbird')

# Some applications contain all locales in a single build
APPLICATIONS_MULTI_LOCALE = ('b2g', 'fennec')

# Used if the application is named differently than the subfolder on the server
APPLICATIONS_TO_FTP_DIRECTORY = {'fennec': 'mobile'}

# Base URL for the path to all builds
BASE_URL = 'http://ftp-origin-scl3.mozilla.org/pub'

# Chunk size when downloading a file
CHUNK_SIZE = 16 * 1024

DEFAULT_FILE_EXTENSIONS = {'android-api-9': 'apk',
                           'android-api-11': 'apk',
                           'android-x86': 'apk',
                           'linux': 'tar.bz2',
                           'linux64': 'tar.bz2',
                           'mac': 'dmg',
                           'mac64': 'dmg',
                           'win32': 'exe',
                           'win64': 'exe'}

PLATFORM_FRAGMENTS = {'android-api-9': r'android-arm',
                      'android-api-11': r'android-arm',
                      'android-x86': r'android-i386',
                      'linux': r'linux-i686',
                      'linux64': r'linux-x86_64',
                      'mac': r'mac',
                      'mac64': r'mac(64)?',
                      'win32': r'win32',
                      'win64': r'win64(-x86_64)?'}


class Scraper(object):
    """Generic class to download an application from the Mozilla server"""

    def __init__(self, destination=None, platform=None,
                 application='firefox', locale=None, extension=None,
                 username=None, password=None,
                 retry_attempts=0, retry_delay=10.,
                 is_stub_installer=False, timeout=None,
                 log_level='INFO',
                 base_url=BASE_URL):

        # Private properties for caching
        self._filename = None
        self._binary = None

        self.destination = destination or os.getcwd()

        if not locale:
            if application in APPLICATIONS_MULTI_LOCALE:
                self.locale = 'multi'
            else:
                self.locale = 'en-US'
        else:
            self.locale = locale

        self.platform = platform or self.detect_platform()

        if (username, password) == (None, None):
            self.authentication = None
        else:
            self.authentication = (username, password)

        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.is_stub_installer = is_stub_installer
        self.timeout_download = timeout
        self.timeout_network = 60.

        logging.basicConfig(format=' %(levelname)s | %(message)s')
        self.logger = logging.getLogger(self.__module__)
        self.logger.setLevel(log_level)

        # build the base URL
        self.application = application
        self.base_url = urljoin(base_url, APPLICATIONS_TO_FTP_DIRECTORY.get(
            self.application, self.application))

        if extension:
            self.extension = extension
        else:
            if self.application in APPLICATIONS_MULTI_LOCALE and \
                    self.platform in ('win32', 'win64'):
                # builds for APPLICATIONS_MULTI_LOCALE only exist in zip
                self.extension = 'zip'
            else:
                self.extension = DEFAULT_FILE_EXTENSIONS[self.platform]

        attempt = 0
        while True:
            attempt += 1
            try:
                self.get_build_info()
                break
            except (errors.NotFoundError, requests.exceptions.RequestException), e:
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
                        raise errors.NotFoundError(message, e.response.url)
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
                    raise errors.NotFoundError('No entries found', self.path)

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
                    raise errors.NotFoundError("Binary not found in folder",
                                               self.path)
            except (errors.NotFoundError, requests.exceptions.RequestException), e:
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
                        raise errors.NotFoundError(message, self.path)
                    else:
                        raise

        return self._binary

    @property
    def binary_regex(self):
        """Return the regex for the binary filename"""

        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def url(self):
        """Return the URL of the build"""

        return urljoin(self.path, self.binary)

    @property
    def path(self):
        """Return the path to the build"""

        return urljoin(self.base_url, self.path_regex)

    @property
    def path_regex(self):
        """Return the regex for the path to the build"""

        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        return PLATFORM_FRAGMENTS[self.platform]

    @property
    def filename(self):
        """Return the local filename of the build"""

        if self._filename is None:
            if os.path.splitext(self.destination)[1]:
                # If the filename has been given make use of it
                target_file = self.destination
            else:
                # Otherwise create it from the build details
                target_file = os.path.join(self.destination,
                                           self.build_filename(self.binary))

            self._filename = os.path.abspath(target_file)

        return self._filename

    def get_build_info(self):
        """Returns additional build information in subclasses if necessary"""
        pass

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

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

        # Don't re-download the file
        if os.path.isfile(os.path.abspath(self.filename)):
            self.logger.info("File has already been downloaded: %s" %
                             (self.filename))
            return self.filename

        directory = os.path.dirname(self.filename)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        self.logger.info('Downloading from: %s' %
                         (urllib.unquote(self.url)))
        self.logger.info('Saving as: %s' % self.filename)

        tmp_file = self.filename + ".part"

        while True:
            attempt += 1
            try:
                start_time = datetime.now()

                # Enable streaming mode so we can download content in chunks
                r = requests.get(self.url, stream=True,
                                 auth=self.authentication)
                r.raise_for_status()

                content_length = r.headers.get('Content-length')
                # ValueError: Value out of range if only total_size given
                if content_length:
                    total_size = int(content_length.strip())
                    max_value = ((total_size / CHUNK_SIZE) + 1) * CHUNK_SIZE

                bytes_downloaded = 0

                log_level = self.logger.getEffectiveLevel()
                if log_level <= logging.INFO and content_length:
                    widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.ETA(),
                               ' ', pb.FileTransferSpeed()]
                    pbar = pb.ProgressBar(widgets=widgets,
                                          maxval=max_value).start()

                with open(tmp_file, 'wb') as f:
                    for chunk in iter(lambda: r.raw.read(CHUNK_SIZE), ''):
                        f.write(chunk)
                        bytes_downloaded += CHUNK_SIZE

                        if log_level <= logging.INFO and content_length:
                            pbar.update(bytes_downloaded)

                        t1 = total_seconds(datetime.now() - start_time)
                        if self.timeout_download and \
                                t1 >= self.timeout_download:
                            raise errors.TimeoutError

                if log_level <= logging.INFO and content_length:
                    pbar.finish()
                break
            except (requests.exceptions.RequestException, errors.TimeoutError), e:
                if tmp_file and os.path.isfile(tmp_file):
                    os.remove(tmp_file)
                if self.retry_attempts > 0:
                    # Log only if multiple attempts are requested
                    self.logger.warning('Download failed: "%s"' % str(e))
                    self.logger.info('Will retry in %s seconds...' %
                                     (self.retry_delay))
                    time.sleep(self.retry_delay)
                    self.logger.info("Retrying... (attempt %s)" % attempt)
                if attempt >= self.retry_attempts:
                    raise
                time.sleep(self.retry_delay)

        os.rename(tmp_file, self.filename)

        return self.filename

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
            try:
                self.date = datetime.strptime(self.date, '%Y-%m-%d')
            except:
                raise ValueError('%s is not a valid date' % self.date)
        else:
            # If no build id nor date have been specified the latest available
            # build of the given branch has to be identified. We also have to
            # retrieve the date of the build via its build id.
            self.date = self.get_latest_build_date()

        self.builds, self.build_index = self.get_build_info_for_date(
            self.date, self.build_index)

    def get_latest_build_date(self):
        """ Returns date of latest available nightly build."""
        if self.application not in ('fennec'):
            url = urljoin(self.base_url, 'nightly', 'latest-%s/' % self.branch)
        else:
            url = urljoin(self.base_url, 'nightly', 'latest-%s-%s/' %
                          (self.branch, self.platform))

        self.logger.info('Retrieving the build status file from %s' % url)
        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        parser.entries = parser.filter(r'.*%s\.txt' % self.platform_regex)
        if not parser.entries:
            message = 'Status file for %s build cannot be found' % \
                self.platform_regex
            raise errors.NotFoundError(message, url)

        # Read status file for the platform, retrieve build id,
        # and convert to a date
        headers = {'Cache-Control': 'max-age=0'}

        r = requests.get(url + parser.entries[-1],
                         auth=self.authentication, headers=headers)
        try:
            r.raise_for_status()

            return datetime.strptime(r.text.split('\n')[0], '%Y%m%d%H%M%S')
        finally:
            r.close()

    def is_build_dir(self, dir):
        """Return whether or not the given dir contains a build."""

        # Cannot move up to base scraper due to parser.entries call in
        # get_build_info_for_date (see below)
        url = urljoin(self.base_url, self.monthly_build_list_regex, dir)

        if self.application in APPLICATIONS_MULTI_LOCALE \
                and self.locale != 'multi':
            url = urljoin(url, self.locale)

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
        regex = r'%(DATE)s-(\d+-)+%(BRANCH)s%(L10N)s%(PLATFORM)s$' % {
            'DATE': date.strftime('%Y-%m-%d'),
            'BRANCH': self.branch,
            # ensure to select the correct subfolder for localized builds
            'L10N': '' if self.locale in ('en-US', 'multi') else '(-l10n)?',
            'PLATFORM': '' if self.application not in (
                        'fennec') else '-' + self.platform
        }
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
            raise errors.NotFoundError(message, url)

        # If no index has been given, set it to the last build of the day.
        self.show_matching_builds(parser.entries)
        # If no index has been given, set it to the last build of the day.
        if build_index is None:
            # Find the most recent non-empty entry.
            build_index = len(parser.entries)
            for build in reversed(parser.entries):
                build_index -= 1
                if not build_index or self.is_build_dir(build):
                    break
        self.logger.info('Selected build: %s' % parser.entries[build_index])

        return (parser.entries, build_index)

    @property
    def binary_regex(self):
        """Return the regex for the binary"""

        regex_base_name = r'^%(APP)s-.*\.%(LOCALE)s\.%(PLATFORM)s'
        regex_suffix = {'android-api-9': r'\.%(EXT)s$',
                        'android-api-11': r'\.%(EXT)s$',
                        'android-x86': r'\.%(EXT)s$',
                        'linux': r'\.%(EXT)s$',
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
            if self.application in APPLICATIONS_MULTI_LOCALE \
                    and self.locale != 'multi':
                path = urljoin(path, self.locale)
            return path
        except:
            folder = urljoin(self.base_url, self.monthly_build_list_regex)
            raise errors.NotFoundError("Specified sub folder cannot be found",
                                       folder)


class DirectScraper(Scraper):
    """Class to download a file from a specified URL"""

    def __init__(self, url, *args, **kwargs):
        self._url = url

        Scraper.__init__(self, *args, **kwargs)

    @property
    def filename(self):
        if os.path.splitext(self.destination)[1]:
            # If the filename has been given make use of it
            target_file = self.destination
        else:
            # Otherwise determine it from the url.
            parsed_url = urlparse(self.url)
            source_filename = (parsed_url.path.rpartition('/')[-1] or
                               parsed_url.hostname)
            target_file = os.path.join(self.destination, source_filename)

        return os.path.abspath(target_file)

    @property
    def url(self):
        return self._url


class ReleaseScraper(Scraper):
    """Class to download a release build from the Mozilla server"""

    def __init__(self, version, *args, **kwargs):
        self.version = version

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

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        if self.platform == 'win64':
            return self.platform

        return PLATFORM_FRAGMENTS[self.platform]

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s.%(LOCALE)s.%(PLATFORM)s%(STUB)s' \
                   '.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'STUB': '-stub' if self.is_stub_installer else '',
                           'EXT': self.extension}


class ReleaseCandidateScraper(ReleaseScraper):
    """Class to download a release candidate build from the Mozilla server"""

    def __init__(self, version, build_number=None, *args, **kwargs):
        self.version = version
        self.build_number = build_number

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Defines additional build information"""

        # Internally we access builds via index
        url = urljoin(self.base_url, self.candidate_build_list_regex)
        self.logger.info('Retrieving list of candidate builds from %s' % url)

        parser = DirectoryParser(url, authentication=self.authentication,
                                 timeout=self.timeout_network)
        if not parser.entries:
            message = 'Folder for specific candidate builds at %s has not' \
                'been found' % url
            raise errors.NotFoundError(message, url)

        self.show_matching_builds(parser.entries)
        self.builds = parser.entries
        self.build_index = len(parser.entries) - 1

        if self.build_number and \
                ('build%s' % self.build_number) in self.builds:
            self.builds = ['build%s' % self.build_number]
            self.build_index = 0
            self.logger.info('Selected build: build%s' % self.build_number)
        else:
            self.logger.info('Selected build: build%d' %
                             (self.build_index + 1))

    @property
    def candidate_build_list_regex(self):
        """Return the regex for the folder which contains the builds of
           a candidate build."""

        # Regex for possible builds for the given date
        return r'candidates/%(VERSION)s-candidates/' % {
            'VERSION': self.version}

    @property
    def path_regex(self):
        """Return the regex for the path"""

        regex = r'%(PREFIX)s%(BUILD)s/%(PLATFORM)s/%(LOCALE)s'
        return regex % {'PREFIX': self.candidate_build_list_regex,
                        'BUILD': self.builds[self.build_index],
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex}

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        if self.platform == 'win64':
            return self.platform

        return PLATFORM_FRAGMENTS[self.platform]

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary"""

        template = '%(APP)s-%(VERSION)s-%(BUILD)s.%(LOCALE)s.' \
                   '%(PLATFORM)s%(STUB)s.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'BUILD': self.builds[self.build_index],
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'STUB': '-stub' if self.is_stub_installer else '',
                           'EXT': self.extension}

    def download(self):
        """Download the specified file"""

        try:
            # Try to download the signed candidate build
            Scraper.download(self)
        except errors.NotFoundError, e:
            self.logger.exception(str(e))


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
                try:
                    # date is provided as a unix timestamp
                    datetime.fromtimestamp(float(self.date))
                    self.timestamp = self.date
                except:
                    raise ValueError('%s is not a valid date' % self.date)

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
                        'win32': r'(\.installer%(STUB)s)?\.%(EXT)s$',
                        'win64': r'(\.installer%(STUB)s)?\.%(EXT)s$'}

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

    def is_build_dir(self, dir):
        """Return whether or not the given dir contains a build."""

        # Cannot move up to base scraper due to parser.entries call in
        # get_build_info_for_index (see below)
        url = urljoin(self.base_url, self.build_list_regex, dir)

        if self.application in APPLICATIONS_MULTI_LOCALE \
                and self.locale != 'multi':
            url = urljoin(url, self.locale)

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
            raise errors.NotFoundError(message, url)

        self.show_matching_builds(parser.entries)

        # If no index has been given, set it to the last build of the day.
        if build_index is None:
            # Find the most recent non-empty entry.
            build_index = len(parser.entries)
            for build in reversed(parser.entries):
                build_index -= 1
                if not build_index or self.is_build_dir(build):
                    break

        self.logger.info('Selected build: %s' % parser.entries[build_index])

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
                              'mac': 'macosx64',
                              'mac64': 'macosx64',
                              'win32': 'win32',
                              'win64': 'win64'}

        return PLATFORM_FRAGMENTS[self.platform]


class TryScraper(Scraper):
    "Class to download a try build from the Mozilla server."

    def __init__(self, changeset=None, debug_build=False, *args, **kwargs):

        self.debug_build = debug_build
        self.changeset = changeset

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        "Defines additional build information"

        self.builds, self.build_index = self.get_build_info_for_index()

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

        return '%(CHANGESET)s%(DEBUG)s-%(NAME)s' % {
            'CHANGESET': self.changeset,
            'DEBUG': '-debug' if self.debug_build else '',
            'NAME': binary}

    @property
    def build_list_regex(self):
        """Return the regex for the folder which contains the list of builds"""

        return 'try-builds'

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
        parser.entries = parser.filter('.*-%s$' % self.changeset)

        if not parser.entries:
            raise errors.NotFoundError('No builds have been found', url)

        self.show_matching_builds(parser.entries)

        self.logger.info('Selected build: %s' % parser.entries[0])

        return (parser.entries, 0)

    @property
    def path_regex(self):
        """Return the regex for the path"""

        build_dir = 'try-%(PLATFORM)s%(DEBUG)s' % {
            'PLATFORM': self.platform_regex,
            'DEBUG': '-debug' if self.debug_build else ''}
        return urljoin(self.build_list_regex,
                       self.builds[self.build_index],
                       build_dir)

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL"""

        PLATFORM_FRAGMENTS = {'linux': 'linux',
                              'linux64': 'linux64',
                              'mac': 'macosx64',
                              'mac64': 'macosx64',
                              'win32': 'win32',
                              'win64': 'win64'}

        return PLATFORM_FRAGMENTS[self.platform]
