# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

from thclient import TreeherderClient

# TODO get logger working for treeherder client
logger = logging.getLogger(__name__)

PLATFORM_MAP = {
    'android-api-9': {'build_platform': 'android-2-3-armv7-api9'},
    'android-api-11': {'build_platform': 'android-4-0-armv7-api11'},
    'android-x86': {'build_platform': 'android-4-2-x86'},
    'linux': {'build_platform': 'linux32'},
    'linux64': {'build_platform': 'linux64'},
    'mac': {'build_os': 'mac', 'build_architecture': 'x86_64'},
    'mac64': {'build_os': 'mac', 'build_architecture': 'x86_64'},
    'win32': {'build_os': 'win', 'build_architecture': 'x86'},
    'win64': {'build_os': 'win', 'build_architecture': 'x86_64'},
}


def get_builds_from_revision(application, branch, revision, platform, job_type_name,
                             debug_build=False):
    """Retrieve builds from a given revision with the help of Treeherder."""
    logger.info('Querying Treeherder to retrieve the list of builds for revision: %s' % revision)

    builds = set()

    try:
        client = TreeherderClient(protocol='https', host='treeherder.mozilla.org')

        # Retrieve the option hash to filter for type of build (opt, and debug for now)
        option_hash = None
        for key, values in client.get_option_collection_hash().iteritems():
            for value in values:
                if value['name'] == ('debug' if debug_build else 'opt'):
                    option_hash = key
                    break
            if option_hash:
                break

        resultsets = client.get_resultsets(branch, revision=revision)

        # Set filters to speed-up querying jobs
        kwargs = {
            'result': 'success',
            'option_collection_hash': option_hash,
            'job_type_name': job_type_name,
            'exclusion_profile': False,
        }
        kwargs.update(PLATFORM_MAP.get(platform, platform))

        for resultset in resultsets:
            kwargs.update({'result_set_id': resultset['id']})
            jobs = client.get_jobs(branch, **kwargs)
            for job in jobs:
                log_urls = client.get_job_log_url(branch, job_id=job['id'])
                for log_url in log_urls:
                    if application in log_url['url']:
                        builds.update([log_url['url'].rsplit('/', 2)[1]])

    except Exception:
        logger.exception('Failure occurred when querying Treeherder for builds')

    return list(builds)
