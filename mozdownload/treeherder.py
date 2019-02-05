# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module to retrieve builds via revision."""

from __future__ import absolute_import, unicode_literals

import logging
import six

from thclient import TreeherderClient

from mozdownload.errors import NotSupportedError

PLATFORM_MAP = {
    'android-api-9': {'build_platform': 'android-2-3-armv7-api9'},
    'android-api-11': {'build_platform': 'android-4-0-armv7-api11'},
    'android-api-15': {'build_platform': 'android-4-0-armv7-api15'},
    'android-x86': {'build_platform': 'android-4-2-x86'},
    'linux': {'build_platform': 'linux32'},
    'linux64': {'build_platform': 'linux64'},
    'mac': {'build_os': 'mac', 'build_architecture': 'x86_64'},
    'mac64': {'build_os': 'mac', 'build_architecture': 'x86_64'},
    'win32': {'build_os': 'win', 'build_architecture': 'x86'},
    'win64': {'build_os': 'win', 'build_architecture': 'x86_64'},
}

TREEHERDER_URL = 'https://treeherder.mozilla.org'


class Treeherder(object):
    """Wrapper class for TreeherderClient to ease the use of its API."""

    def __init__(self, application, branch, platform, server_url=TREEHERDER_URL):
        """Create a new instance of the Treeherder class.

        :param application: The name of the application to download.
        :param branch: Name of the branch.
        :param platform: Platform of the application.
        :param server_url: The URL of the Treeherder instance to access.
        """
        self.logger = logging.getLogger(__name__)

        self.client = TreeherderClient(server_url=server_url)
        self.application = application
        self.branch = branch
        self.platform = platform

    def get_treeherder_platform(self, platform):
        """Return the internal Treeherder platform identifier.

        :param platform: Platform of the application.
        """
        try:
            return PLATFORM_MAP[platform]
        except KeyError:
            raise NotSupportedError('Platform "{}" is not supported.'.format(platform))

    def query_builds_by_revision(self, revision, job_type_name='Build', debug_build=False):
        """Retrieve build folders for a given revision with the help of Treeherder.

        :param revision: Revision of the build to download.
        :param job_type_name: Name of the job to look for. For builds it should be
            'Build', 'Nightly', and 'L10n Nightly'. Defaults to `Build`.
        :param debug_build: Download a debug build.
        """
        builds = set()

        try:
            self.logger.info('Querying {url} for list of builds for revision: {revision}'.format(
                url=self.client.server_url, revision=revision))

            # Retrieve the option hash to filter for type of build (opt, and debug for now)
            option_hash = None
            for key, values in six.iteritems(self.client.get_option_collection_hash()):
                for value in values:
                    if value['name'] == ('debug' if debug_build else 'opt'):
                        option_hash = key
                        break
                if option_hash:
                    break

            resultsets = self.client.get_pushes(self.branch, revision=revision)

            # Set filters to speed-up querying jobs
            kwargs = {
                'option_collection_hash': option_hash,
                'job_type_name': job_type_name,
                'exclusion_profile': False,
            }
            kwargs.update(self.get_treeherder_platform(self.platform))

            for resultset in resultsets:
                kwargs.update({'result_set_id': resultset['id']})
                jobs = self.client.get_jobs(self.branch, **kwargs)
                for job in jobs:
                    log_urls = self.client.get_job_log_url(self.branch, job_id=job['id'])
                    for log_url in log_urls:
                        if self.application in log_url['url']:
                            self.logger.debug('Found build folder: {}'.format(log_url['url']))
                            builds.update([log_url['url']])

        except Exception:
            self.logger.exception('Failure occurred when querying Treeherder for builds')

        return list(builds)
