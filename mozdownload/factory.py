# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from . import errors
from . import scraper


# List of known download scrapers
scraper_types = {'candidate': scraper.ReleaseCandidateScraper,
                 'daily': scraper.DailyScraper,
                 'direct': scraper.DirectScraper,
                 'release': scraper.ReleaseScraper,
                 'tinderbox': scraper.TinderboxScraper,
                 'try': scraper.TryScraper,
                 }


class FactoryScraper(scraper.Scraper):

    def __init__(self, scraper_type, **kwargs):
        """Creates an instance of a scraper class based on the given type.

        :param scraper_type: The type of scraper to use.

        Scraper:
        :param application: The name of the application to download.
        :param base_url: The base url to be used
        :param build_number: Number of the build (for candidate, daily, and tinderbox builds).
        :param destination: Directory or file name to download the file to.
        :param extension: File extension of the build (e.g. ".zip").
        :param is_stub_installer: Stub installer (Only applicable to Windows builds).
        :param locale: Locale of the application.
        :param log_level: Threshold for log output.
        :param password: Password for basic HTTP authentication.
        :param platform: Platform of the application
        :param retry_attempts: Number of times the download will be attempted
            in the event of a failure
        :param retry_delay: Amount of time (in seconds) to wait between retry attempts.
        :param timeout: Amount of time (in seconds) until a download times out.
        :param url: URL to download.
        :param username: Username for basic HTTP authentication.
        :param version: Version of the application to be downloaded.

        Daily builds:
        :param branch: Name of the branch.
        :param build_id: ID of the build to download.
        :param date: Date of the build.

        Tinderbox:
        :param debug_build: Download a debug build.

        Try:
        :param changeset: Changeset of the try build to download.

        """
        # Check for valid arguments
        if scraper_type in ('candidate', 'release') and not kwargs.get('version'):
            raise ValueError('The version to download has to be specified.')

        if kwargs.get('application') == 'b2g' and scraper_type in ('candidate', 'release'):
            error_msg = '%s build is not yet supported for B2G' % scraper_type
            raise errors.NotSupportedError(error_msg)

        if kwargs.get('application') == 'fennec' and scraper_type not in ('daily'):
            error_msg = '%s build is not yet supported for fennec' % scraper_type
            raise errors.NotSupportedError(error_msg)

        # Instantiate scraper and download the build
        scraper_keywords = {'application': kwargs.get('application', 'firefox'),
                            'base_url': kwargs.get('base_url', scraper.BASE_URL),
                            'destination': kwargs.get('destination'),
                            'extension': kwargs.get('extension'),
                            'is_stub_installer': kwargs.get('is_stub_installer'),
                            'locale': kwargs.get('locale'),
                            'log_level': kwargs.get('log_level', 'INFO'),
                            'password': kwargs.get('password'),
                            'platform': kwargs.get('platform'),
                            'retry_attempts': kwargs.get('retry_attempts', 0),
                            'retry_delay': kwargs.get('retry_delay', 10),
                            'timeout': kwargs.get('timeout'),
                            'username': kwargs.get('username'),
                            }

        scraper_type_keywords = {
            'release': {
                'version': kwargs.get('version'),
            },
            'candidate': {
                'build_number': kwargs.get('build_number'),
                'version': kwargs.get('version'),
            },
            'daily': {
                'branch': kwargs.get('branch', 'mozilla-central'),
                'build_number': kwargs.get('build_number'),
                'build_id': kwargs.get('build_id'),
                'date': kwargs.get('date'),
            },
            'direct': {
                'url': kwargs.get('url'),
            },
            'tinderbox': {
                'branch': kwargs.get('branch', 'mozilla-central'),
                'build_number': kwargs.get('build_number'),
                'date': kwargs.get('date'),
                'debug_build': kwargs.get('debug_build', False),
            },
            'try': {
                'changeset': kwargs.get('changeset'),
                'debug_build': kwargs.get('debug_build', False),
            },
        }

        kwargs = scraper_keywords.copy()
        kwargs.update(scraper_type_keywords.get(scraper_type, {}))

        self.__class__ = scraper_types[scraper_type]
        scraper_types[scraper_type].__init__(self, **kwargs)
