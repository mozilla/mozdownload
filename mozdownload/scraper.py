# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Scrapers for various kinds of build types."""

from __future__ import absolute_import, unicode_literals

import logging
import os
import re
import sys
from datetime import datetime

import mozinfo
import progressbar as pb
import redo
import requests
from six.moves.urllib.parse import quote, urlparse

from mozdownload import errors
from mozdownload import treeherder
from mozdownload.parser import DirectoryParser
from mozdownload.timezones import PacificTimezone
from mozdownload.utils import urljoin

APPLICATIONS = ('devedition', 'firefox', 'fennec', 'thunderbird')

# Some applications contain all locales in a single build
APPLICATIONS_MULTI_LOCALE = ('fennec')

# Used if the application is named differently than the subfolder on the server
APPLICATIONS_TO_FTP_DIRECTORY = {'fennec': 'mobile'}
# Used if the application is named differently then the binary on the server
APPLICATIONS_TO_BINARY_NAME = {'devedition': 'firefox'}

# Base URL for the path to all builds
BASE_URL = 'https://archive.mozilla.org/pub/'

# Chunk size when downloading a file
CHUNK_SIZE = 16 * 1024

DEFAULT_FILE_EXTENSIONS = {'android-api-9': 'apk',
                           'android-api-11': 'apk',
                           'android-api-15': 'apk',
                           'android-api-16': 'apk',
                           'android-x86': 'apk',
                           'linux': 'tar.bz2',
                           'linux64': 'tar.bz2',
                           'mac': 'dmg',
                           'mac64': 'dmg',
                           'win32': 'exe',
                           'win64': 'exe'}

PLATFORM_FRAGMENTS = {'android-api-9': r'android-arm',
                      'android-api-11': r'android-arm',
                      'android-api-15': r'android-arm',
                      'android-api-16': r'android-arm',
                      'android-x86': r'android-i386',
                      'linux': r'linux-i686',
                      'linux64': r'linux-x86_64',
                      'mac': r'mac',
                      'mac64': r'mac(64)?',
                      'win32': r'win32',
                      'win64': r'win64(-x86_64)?'}

# Special versions for release and candidate builds
RELEASE_AND_CANDIDATE_LATEST_VERSIONS = {
    'latest': r'^\d+(\.\d+)+(-candidates)?$',
    'latest-beta': r'^\d+(\.\d+)+b\d+(-candidates)?$',
    'latest-esr': r'^\d+(\.\d+)+esr(-candidates)?$',
}


class Scraper(object):
    """Generic class to download a Gecko based application."""

    def __init__(self, destination=None, platform=None,
                 application='firefox', locale=None, extension=None,
                 username=None, password=None,
                 retry_attempts=0, retry_delay=10.,
                 is_stub_installer=False, timeout=None,
                 logger=None,
                 base_url=BASE_URL):
        """Create an instance of the generic scraper."""
        # Private properties for caching
        self._filename = None
        self._binary = None

        self.logger = logger or logging.getLogger(self.__module__)

        self.destination = destination or os.getcwd()

        if not locale:
            if application in APPLICATIONS_MULTI_LOCALE:
                self.locale = 'multi'
            else:
                self.locale = 'en-US'
        else:
            self.locale = locale
        self.locale_build = self.locale not in ('en-US', 'multi')

        self.platform = platform or self.detect_platform()

        self.session = requests.Session()
        if (username, password) != (None, None):
            self.session.auth = (username, password)

        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.is_stub_installer = is_stub_installer
        self.timeout_download = timeout
        # this is the timeout used in requests.get. Unlike "auth",
        # it does not work if we attach it on the session, so we handle
        # it independently.
        self.timeout_network = 60.

        # build the base URL
        self.application = application
        self.base_url = '%s/' % urljoin(
            base_url,
            APPLICATIONS_TO_FTP_DIRECTORY.get(self.application, self.application)
        )

        if extension:
            self.extension = extension
        else:
            if self.application in APPLICATIONS_MULTI_LOCALE and \
                    self.platform in ('win32', 'win64'):
                # builds for APPLICATIONS_MULTI_LOCALE only exist in zip
                self.extension = 'zip'
            else:
                self.extension = DEFAULT_FILE_EXTENSIONS[self.platform]

        self._retry_check_404(self.get_build_info)

    def _retry(self, func, **retry_kwargs):
        retry_kwargs.setdefault('jitter', 0)
        retry_kwargs.setdefault('sleeptime', self.retry_delay)
        retry_kwargs.setdefault('attempts', self.retry_attempts + 1)
        return redo.retry(func, **retry_kwargs)

    def _retry_check_404(self, func,
                         err_message="Specified build has not been found",
                         **retry_kwargs):
        retry_kwargs.setdefault('retry_exceptions',
                                (errors.NotFoundError,
                                 requests.exceptions.RequestException))
        try:
            self._retry(func, **retry_kwargs)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 404:
                raise errors.NotFoundError(err_message, exc.response.url)
            else:
                raise

    def _create_directory_parser(self, url):
        return DirectoryParser(url,
                               session=self.session,
                               timeout=self.timeout_network)

    @property
    def binary(self):
        """Return the name of the build."""

        def _get_binary():
            # Retrieve all entries from the remote virtual folder
            parser = self._create_directory_parser(self.path)
            if not parser.entries:
                raise errors.NotFoundError('No entries found', self.path)

            # Download the first matched directory entry
            pattern = re.compile(self.binary_regex, re.IGNORECASE)
            for entry in parser.entries:
                try:
                    self._binary = pattern.match(entry).group()
                    break
                except Exception:
                    # No match, continue with next entry
                    continue
            else:
                raise errors.NotFoundError("Binary not found in folder",
                                           self.path)

        self._retry_check_404(_get_binary)

        return self._binary

    @property
    def binary_regex(self):
        """Return the regex for the binary filename."""
        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def url(self):
        """Return the URL of the build."""
        return quote(urljoin(self.path, self.binary),
                     safe='%/:=&?~#+!$,;\'@()*[]|')

    @property
    def path(self):
        """Return the path to the build folder."""
        return urljoin(self.base_url, self.path_regex)

    @property
    def path_regex(self):
        """Return the regex for the path to the build folder."""
        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL."""
        return PLATFORM_FRAGMENTS[self.platform]

    @property
    def filename(self):
        """Return the local filename of the build."""
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
        """Return additional build information in subclasses if necessary."""
        pass

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""
        raise errors.NotImplementedError(sys._getframe(0).f_code.co_name)

    def detect_platform(self):
        """Detect the current platform."""
        # For Mac and Linux 32bit we do not need the bits appended
        if mozinfo.os == 'mac' or \
                (mozinfo.os == 'linux' and mozinfo.bits == 32):
            return mozinfo.os
        else:
            return "%s%d" % (mozinfo.os, mozinfo.bits)

    def download(self):
        """Download the specified file."""

        def total_seconds(td):
            # Keep backward compatibility with Python 2.6 which doesn't have
            # this method
            if hasattr(td, 'total_seconds'):
                return td.total_seconds()
            else:
                return (td.microseconds +
                        (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6

        # Don't re-download the file
        if os.path.isfile(os.path.abspath(self.filename)):
            self.logger.info("File has already been downloaded: %s" %
                             (self.filename))
            return self.filename

        directory = os.path.dirname(self.filename)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        self.logger.info('Downloading from: %s' % self.url)
        self.logger.info('Saving as: %s' % self.filename)

        tmp_file = self.filename + ".part"

        def _download():
            try:
                start_time = datetime.now()

                # Enable streaming mode so we can download content in chunks
                r = self.session.get(self.url, stream=True)
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
                    for chunk in r.iter_content(CHUNK_SIZE):
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
            except Exception:
                if os.path.isfile(tmp_file):
                    os.remove(tmp_file)
                raise

        self._retry(_download,
                    retry_exceptions=(requests.exceptions.RequestException,
                                      errors.TimeoutError))

        os.rename(tmp_file, self.filename)

        return self.filename

    def show_matching_builds(self, builds):
        """Output the matching builds."""
        self.logger.info('Found %s build%s: %s' % (
            len(builds),
            len(builds) > 1 and 's' or '',
            len(builds) > 10 and
            ' ... '.join([', '.join(builds[:5]), ', '.join(builds[-5:])]) or
            ', '.join(builds)))


class DailyScraper(Scraper):
    """Class to download a daily build from the Mozilla server."""

    def __init__(self, branch='mozilla-central', build_id=None, date=None,
                 build_number=None, revision=None, *args, **kwargs):
        """Create an instance of the daily scraper."""
        self.branch = branch
        self.build_id = build_id
        self.date = date
        self.build_number = build_number
        self.revision = revision

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Define additional build information."""
        # Retrieve build by revision
        if self.revision:
            th = treeherder.Treeherder(
                APPLICATIONS_TO_FTP_DIRECTORY.get(self.application, self.application),
                self.branch,
                self.platform)
            builds = th.query_builds_by_revision(
                self.revision,
                job_type_name='L10n Nightly' if self.locale_build else 'Nightly')

            if not builds:
                raise errors.NotFoundError('No builds have been found for revision', self.revision)

            # Extract the build folders which are prefixed with the buildid
            self.builds = [build.rsplit('/', 2)[1] for build in builds]
            self.show_matching_builds(self.builds)

            # There is only a single build per revision and platform
            self.build_index = 0
            self.logger.info('Selected build: %s' % self.builds[self.build_index])

            # Retrieve the date from the build folder which is always 19 chars long
            self.date = datetime.strptime(self.builds[self.build_index][:19],
                                          '%Y-%m-%d-%H-%M-%S')

            return

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
            except Exception:
                raise ValueError('%s is not a valid date' % self.date)
        else:
            # If no querying option has been specified the latest available
            # build of the given branch has to be identified. We also have to
            # retrieve the date of the build via its build id.
            self.date = self.get_latest_build_date()

        self.builds, self.build_index = self.get_build_info_for_date(
            self.date, self.build_index)

    def get_latest_build_date(self):
        """Return date of latest available nightly build."""
        if self.application not in ('fennec'):
            url = urljoin(self.base_url, 'nightly', 'latest-%s/' % self.branch)
        else:
            url = urljoin(self.base_url, 'nightly', 'latest-%s-%s/' %
                          (self.branch, self.platform))

        self.logger.info('Retrieving the build status file from %s' % url)
        parser = self._create_directory_parser(url)
        parser.entries = parser.filter(r'.*%s\.txt' % self.platform_regex)
        if not parser.entries:
            message = 'Status file for %s build cannot be found' % \
                      self.platform_regex
            raise errors.NotFoundError(message, url)

        # Read status file for the platform, retrieve build id,
        # and convert to a date
        headers = {'Cache-Control': 'max-age=0'}

        r = self.session.get(url + parser.entries[-1], headers=headers)
        try:
            r.raise_for_status()

            return datetime.strptime(r.text.replace('\r\n', '\n').split('\n')[0], '%Y%m%d%H%M%S')
        finally:
            r.close()

    def is_build_dir(self, folder_name):
        """Return whether or not the given dir contains a build."""
        # Cannot move up to base scraper due to parser.entries call in
        # get_build_info_for_date (see below)

        url = '%s/' % urljoin(self.base_url, self.monthly_build_list_regex, folder_name)
        if self.application in APPLICATIONS_MULTI_LOCALE \
                and self.locale != 'multi':
            url = '%s/' % urljoin(url, self.locale)

        parser = self._create_directory_parser(url)

        pattern = re.compile(self.binary_regex, re.IGNORECASE)
        for entry in parser.entries:
            try:
                pattern.match(entry).group()
                return True
            except Exception:
                # No match, continue with next entry
                continue
        return False

    def get_build_info_for_date(self, date, build_index=None):
        """Return the build information for a given date."""
        url = urljoin(self.base_url, self.monthly_build_list_regex)
        has_time = date and date.time() and date.strftime('%H-%M-%S') != '00-00-00'

        self.logger.info('Retrieving list of builds from %s' % url)
        parser = self._create_directory_parser(url)
        regex = r'%(DATE)s-(\d+-)+%(BRANCH)s%(L10N)s%(PLATFORM)s$' % {
            'DATE': date.strftime('%Y-%m-%d'),
            'BRANCH': self.branch,
            # ensure to select the correct subfolder for localized builds
            'L10N': '(-l10n)?' if self.locale_build else '',
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
        """Return the regex for the binary."""
        regex_base_name = (r'^%(BINARY_NAME)s(\s%(STUB_NEW)s\.%(LOCALE)s|' +
                           r'-.*\.%(LOCALE)s\.%(PLATFORM)s)')
        regex_suffix = {'android-api-9': r'\.%(EXT)s$',
                        'android-api-11': r'\.%(EXT)s$',
                        'android-api-15': r'\.%(EXT)s$',
                        'android-api-16': r'\.%(EXT)s$',
                        'android-x86': r'\.%(EXT)s$',
                        'linux': r'\.%(EXT)s$',
                        'linux64': r'\.%(EXT)s$',
                        'mac': r'\.%(EXT)s$',
                        'mac64': r'\.%(EXT)s$',
                        'win32': r'(\.installer%(STUB)s)?\.%(EXT)s$',
                        'win64': r'(\.installer%(STUB)s)?\.%(EXT)s$'}
        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'BINARY_NAME': APPLICATIONS_TO_BINARY_NAME.get(self.application,
                                                                       self.application),
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'EXT': self.extension,
                        'STUB': '-stub' if self.is_stub_installer else '',
                        'STUB_NEW': 'Installer' if self.is_stub_installer else ''}

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""
        try:
            # Get exact timestamp of the build to build the local file name
            folder = self.builds[self.build_index]
            timestamp = re.search(r'([\d\-]+)-\D.*', folder).group(1)
        except Exception:
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
        return r'nightly/%(YEAR)s/%(MONTH)s/' % {
            'YEAR': self.date.year,
            'MONTH': str(self.date.month).zfill(2)}

    @property
    def path_regex(self):
        """Return the regex for the path to the build folder."""
        try:
            path = '%s/' % urljoin(self.monthly_build_list_regex,
                                   self.builds[self.build_index])
            if self.application in APPLICATIONS_MULTI_LOCALE \
                    and self.locale != 'multi':
                path = '%s/' % urljoin(path, self.locale)
            return path
        except Exception:
            folder = urljoin(self.base_url, self.monthly_build_list_regex)
            raise errors.NotFoundError("Specified sub folder cannot be found",
                                       folder)


class DirectScraper(Scraper):
    """Class to download a file from a specified URL."""

    def __init__(self, url, *args, **kwargs):
        """Create an instance of the direct scraper."""
        self._url = url

        Scraper.__init__(self, *args, **kwargs)

    @property
    def filename(self):
        """File name of the downloaded file."""
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
        """Location of the file to be downloaded."""
        return self._url


class ReleaseScraper(Scraper):
    """Class to download a release build of a Gecko based application."""

    def __init__(self, version, *args, **kwargs):
        """Create instance of a release scraper."""
        self.version = version

        Scraper.__init__(self, *args, **kwargs)

    @property
    def binary_regex(self):
        """Return the regex for the binary."""
        regex = {'linux': r'^%(BINARY_NAME)s-%(VERSION)s\.%(EXT)s$',
                 'linux64': r'^%(BINARY_NAME)s-%(VERSION)s\.%(EXT)s$',
                 'mac': r'^%(BINARY_NAME)s(?:\s|-)%(VERSION)s\.%(EXT)s$',
                 'mac64': r'^%(BINARY_NAME)s(?:\s|-)%(VERSION)s\.%(EXT)s$',
                 'win32':
                     r'^%(BINARY_NAME)s(%(STUB_NEW)s|(?:\sSetup\s|-)%(STUB)s%(VERSION)s)\.%(EXT)s$',
                 'win64':
                     r'^%(BINARY_NAME)s(%(STUB_NEW)s|(?:\sSetup\s|-)%(STUB)s%(VERSION)s)\.%(EXT)s$',
                 }
        return regex[self.platform] % {
            'BINARY_NAME': APPLICATIONS_TO_BINARY_NAME.get(self.application, self.application),
            'EXT': self.extension,
            'STUB': 'Stub ' if self.is_stub_installer else '',
            'STUB_NEW': ' Installer' if self.is_stub_installer else '',
            'VERSION': self.version,
        }

    @property
    def path_regex(self):
        """Return the regex for the path to the build folder."""
        regex = r'releases/%(VERSION)s/%(PLATFORM)s/%(LOCALE)s/'
        return regex % {'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex,
                        'VERSION': self.version}

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL."""
        if self.platform == 'win64':
            return self.platform

        return PLATFORM_FRAGMENTS[self.platform]

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""
        template = '%(APP)s-%(VERSION)s.%(LOCALE)s.%(PLATFORM)s%(STUB)s' \
                   '.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'STUB': '-stub' if self.is_stub_installer else '',
                           'EXT': self.extension}

    def get_build_info(self):
        """Define additional build information."""
        self.version = self.query_versions(self.version)[0]

    def query_versions(self, version=None):
        """Check specified version and resolve special values."""
        if version not in RELEASE_AND_CANDIDATE_LATEST_VERSIONS:
            return [version]

        url = urljoin(self.base_url, 'releases/')
        parser = self._create_directory_parser(url)
        if version:
            versions = parser.filter(RELEASE_AND_CANDIDATE_LATEST_VERSIONS[version])
            from packaging.version import LegacyVersion
            versions.sort(key=LegacyVersion)
            return [versions[-1]]
        else:
            return parser.entries


class ReleaseCandidateScraper(ReleaseScraper):
    """Class to download a release candidate build of a Gecko based application."""

    def __init__(self, build_number=None, *args, **kwargs):
        """Create an instance of a release candidate scraper."""
        self.build_number = build_number

        ReleaseScraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Define additional build information."""
        ReleaseScraper.get_build_info(self)

        # Internally we access builds via index
        url = urljoin(self.base_url, self.candidate_build_list_regex)
        self.logger.info('Retrieving list of candidate builds from %s' % url)

        parser = self._create_directory_parser(url)
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
            self.logger.info('Selected build: %s' %
                             (parser.entries[self.build_index]))

    @property
    def candidate_build_list_regex(self):
        """Return the regex for the folder with the list of candidate builds."""
        # Regex for possible builds for the given date
        return r'candidates/%(VERSION)s-candidates/' % {
            'VERSION': self.version}

    @property
    def path_regex(self):
        """Return the regex for the path to the build folder."""
        regex = r'%(PREFIX)s%(BUILD)s/%(PLATFORM)s/%(LOCALE)s/'
        return regex % {'PREFIX': self.candidate_build_list_regex,
                        'BUILD': self.builds[self.build_index],
                        'LOCALE': self.locale,
                        'PLATFORM': self.platform_regex}

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL."""
        if self.platform == 'win64':
            return self.platform

        return PLATFORM_FRAGMENTS[self.platform]

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""
        template = '%(APP)s-%(VERSION)s-%(BUILD)s.%(LOCALE)s.' \
                   '%(PLATFORM)s%(STUB)s.%(EXT)s'
        return template % {'APP': self.application,
                           'VERSION': self.version,
                           'BUILD': self.builds[self.build_index],
                           'LOCALE': self.locale,
                           'PLATFORM': self.platform,
                           'STUB': '-stub' if self.is_stub_installer else '',
                           'EXT': self.extension}


class TinderboxScraper(Scraper):
    """Class to download a tinderbox build of a Gecko based application."""

    def __init__(self, branch='mozilla-central', build_number=None, date=None,
                 debug_build=False, revision=None, *args, **kwargs):
        """Create instance of a tinderbox scraper."""
        self.branch = branch
        self.build_number = build_number
        self.debug_build = debug_build
        self.date = date
        self.revision = revision

        self.timestamp = None
        # Currently any time in RelEng is based on the Pacific time zone.
        self.timezone = PacificTimezone()

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Define additional build information."""
        # Retrieve build by revision
        if self.revision:
            th = treeherder.Treeherder(
                APPLICATIONS_TO_FTP_DIRECTORY.get(self.application, self.application),
                self.branch,
                self.platform)
            builds = th.query_builds_by_revision(
                self.revision, job_type_name='Build', debug_build=self.debug_build)

            if not builds:
                raise errors.NotFoundError('No builds have been found for revision', self.revision)

            # Extract timestamp from each build folder
            self.builds = [build.rsplit('/', 2)[1] for build in builds]
            self.show_matching_builds(self.builds)

            # There is only a single build
            self.build_index = 0
            self.logger.info('Selected build: %s' % self.builds[self.build_index])

            return

        # Internally we access builds via index
        if self.build_number is not None:
            self.build_index = int(self.build_number) - 1
        else:
            self.build_index = None

        if self.date is not None:
            try:
                # date is provided in the format 2013-07-23
                self.date = datetime.strptime(self.date, '%Y-%m-%d')
            except Exception:
                try:
                    # date is provided as a unix timestamp
                    datetime.fromtimestamp(float(self.date))
                    self.timestamp = self.date
                except Exception:
                    raise ValueError('%s is not a valid date' % self.date)

        # For localized builds we do not have to retrieve the list of builds
        # because only the last build is available
        if not self.locale_build:
            self.builds, self.build_index = self.get_build_info_for_index(
                self.build_index)
            # Always force a timestamp prefix in the filename
            self.timestamp = self.builds[self.build_index]

    @property
    def binary_regex(self):
        """Return the regex for the binary."""
        regex_base_name = (r'^(%(STUB_NEW)s|%(BINARY_NAME)s-.*\.%(LOCALE)s\.%(PLATFORM)s)')
        regex_suffix = {'linux': r'.*\.%(EXT)s$',
                        'linux64': r'.*\.%(EXT)s$',
                        'mac': r'.*\.%(EXT)s$',
                        'mac64': r'.*\.%(EXT)s$',
                        'win32': r'(\.installer%(STUB)s)?\.%(EXT)s$',
                        'win64': r'(\.installer%(STUB)s)?\.%(EXT)s$'}

        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'BINARY_NAME': APPLICATIONS_TO_BINARY_NAME.get(self.application,
                                                                       self.application),
                        'LOCALE': self.locale,
                        'PLATFORM': PLATFORM_FRAGMENTS[self.platform],
                        'STUB': '-stub' if self.is_stub_installer else '',
                        'STUB_NEW': 'setup' if self.is_stub_installer else '',
                        'EXT': self.extension}

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""

        return '%(TIMESTAMP)s%(BRANCH)s%(DEBUG)s-%(NAME)s' % {
            'TIMESTAMP': self.timestamp + '-' if self.timestamp else '',
            'BRANCH': self.branch,
            'DEBUG': '-debug' if self.debug_build else '',
            'NAME': binary}

    @property
    def build_list_regex(self):
        """Return the regex for the folder which contains the list of builds."""
        regex = 'tinderbox-builds/%(BRANCH)s-%(PLATFORM)s%(L10N)s%(DEBUG)s/'

        return regex % {
            'BRANCH': self.branch,
            'PLATFORM': '' if self.locale_build else self.platform_regex,
            'L10N': 'l10n' if self.locale_build else '',
            'DEBUG': '-debug' if self.debug_build else ''}

    def date_matches(self, timestamp):
        """Determine whether the timestamp date is equal to the argument date."""
        if self.date is None:
            return False

        timestamp = datetime.fromtimestamp(float(timestamp), self.timezone)
        if self.date.date() == timestamp.date():
            return True

        return False

    def detect_platform(self):
        """Detect the current platform."""
        platform = Scraper.detect_platform(self)

        # On OS X we have to special case the platform detection code and
        # fallback to 64 bit builds for the en-US locale
        if mozinfo.os == 'mac' and self.locale == 'en-US' and \
                mozinfo.bits == 64:
            platform = "%s%d" % (mozinfo.os, mozinfo.bits)

        return platform

    def is_build_dir(self, folder_name):
        """Return whether or not the given dir contains a build."""
        # Cannot move up to base scraper due to parser.entries call in
        # get_build_info_for_index (see below)
        url = '%s/' % urljoin(self.base_url, self.build_list_regex, folder_name)

        if self.application in APPLICATIONS_MULTI_LOCALE \
                and self.locale != 'multi':
            url = '%s/' % urljoin(url, self.locale)

        parser = self._create_directory_parser(url)

        pattern = re.compile(self.binary_regex, re.IGNORECASE)
        for entry in parser.entries:
            try:
                pattern.match(entry).group()
                return True
            except Exception:
                # No match, continue with next entry
                continue
        return False

    def get_build_info_for_index(self, build_index=None):
        """Get additional information for the build at the given index."""
        url = urljoin(self.base_url, self.build_list_regex)

        self.logger.info('Retrieving list of builds from %s' % url)
        parser = self._create_directory_parser(url)
        parser.entries = parser.filter(r'^\d+$')

        if self.timestamp:
            # If a timestamp is given, retrieve the folder with the timestamp
            # as name
            parser.entries = self.timestamp in parser.entries and \
                             [self.timestamp]

        elif self.date:
            # If date is given, retrieve the subset of builds on that date
            parser.entries = list(filter(self.date_matches, parser.entries))

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
        """Return the regex for the path to the build folder."""
        if self.locale_build:
            return self.build_list_regex

        return '%s/' % urljoin(self.build_list_regex, self.builds[self.build_index])

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL."""
        platform_fragments = {'linux': 'linux',
                              'linux64': 'linux64',
                              'mac': 'macosx64',
                              'mac64': 'macosx64',
                              'win32': 'win32',
                              'win64': 'win64'}

        return platform_fragments[self.platform]


class TryScraper(Scraper):
    """Class to download a try build of a Gecko based application."""

    def __init__(self, revision=None, debug_build=False, *args, **kwargs):
        """Create an instance of a try scraper."""
        self.debug_build = debug_build
        self.revision = revision

        Scraper.__init__(self, *args, **kwargs)

    def get_build_info(self):
        """Define additional build information."""
        # Retrieve build by revision
        th = treeherder.Treeherder(
            APPLICATIONS_TO_FTP_DIRECTORY.get(self.application, self.application),
            'try',
            self.platform)
        builds = th.query_builds_by_revision(
            self.revision, job_type_name='Build', debug_build=self.debug_build)

        if not builds:
            raise errors.NotFoundError('No builds have been found for revision', self.revision)

        # Extract username and revision from build folders
        self.builds = [build.rsplit('/', 3)[1] for build in builds]
        self.show_matching_builds(self.builds)

        # There is only a single build per revision and platform
        self.build_index = 0
        self.logger.info('Selected build: %s' % self.builds[self.build_index])

    @property
    def binary_regex(self):
        """Return the regex for the binary."""
        regex_base_name = (r'^(%(STUB_NEW)s|%(BINARY_NAME)s-.*\.%(LOCALE)s\.%(PLATFORM)s)')
        regex_suffix = {'linux': r'.*\.%(EXT)s$',
                        'linux64': r'.*\.%(EXT)s$',
                        'mac': r'.*\.%(EXT)s$',
                        'mac64': r'.*\.%(EXT)s$',
                        'win32': r'.*(\.installer%(STUB)s)\.%(EXT)s$',
                        'win64': r'.*(\.installer%(STUB)s)\.%(EXT)s$'}

        regex = regex_base_name + regex_suffix[self.platform]

        return regex % {'BINARY_NAME': APPLICATIONS_TO_BINARY_NAME.get(self.application,
                                                                       self.application),
                        'LOCALE': self.locale,
                        'PLATFORM': PLATFORM_FRAGMENTS[self.platform],
                        'STUB': '-stub' if self.is_stub_installer else '',
                        'STUB_NEW': 'setup' if self.is_stub_installer else '',
                        'EXT': self.extension}

    def build_filename(self, binary):
        """Return the proposed filename with extension for the binary."""
        return '%(REVISION)s%(DEBUG)s-%(NAME)s' % {
            'REVISION': self.revision,
            'DEBUG': '-debug' if self.debug_build else '',
            'NAME': binary}

    @property
    def build_list_regex(self):
        """Return the regex for the folder which contains the list of builds."""
        return 'try-builds/'

    def detect_platform(self):
        """Detect the current platform."""
        platform = Scraper.detect_platform(self)

        # On OS X we have to special case the platform detection code and
        # fallback to 64 bit builds for the en-US locale
        if mozinfo.os == 'mac' and self.locale == 'en-US' and \
                mozinfo.bits == 64:
            platform = "%s%d" % (mozinfo.os, mozinfo.bits)

        return platform

    @property
    def path_regex(self):
        """Return the regex for the path to the build folder."""
        build_dir = 'try-%(PLATFORM)s%(DEBUG)s/' % {
            'PLATFORM': self.platform_regex,
            'DEBUG': '-debug' if self.debug_build else ''}
        return urljoin(self.build_list_regex,
                       self.builds[self.build_index],
                       build_dir)

    @property
    def platform_regex(self):
        """Return the platform fragment of the URL."""
        platform_fragments = {'linux': 'linux',
                              'linux64': 'linux64',
                              'mac': 'macosx64',
                              'mac64': 'macosx64',
                              'win32': 'win32',
                              'win64': 'win64'}

        return platform_fragments[self.platform]
