import copy
import os

import pytest

from mozdownload import FactoryScraper


@pytest.mark.parametrize('filename,args', [
    # ReleaseScraper
    ('release',
     {
         'fname': 'firefox-23.0.1.en-US.win32.exe',
         'kwargs': {
             'platform': 'win32',
             'version': '23.0.1',
         }
     }),

    # ReleaseCandidateScraper
    ('candidate',
     {
         'fname': 'firefox-23.0.1-build3.en-US.win32.exe',
         'kwargs': {
             'platform': 'win32',
             'version': '23.0.1',
         }
     }),

    # DailyScraper
    ('daily',
     {
         'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
         'kwargs': {
             'platform': 'win32',
         }
     }),

    # TinderboxScraper
    ('tinderbox',
     {
         'fname': '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
         'kwargs': {
             'platform': 'win32',
         }
     }),

    # TryScraper
    ('try',
     {
         'builds': ['/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'],
         'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg',
         'kwargs': {
             'revision': '8fcac92cfcad',
             'platform': 'mac64',
         }
     }),
])
def test_factory(httpd, tmpdir, filename, args, mocker):
    """Testing various download scenarios for the factory."""
    query_builds_by_revision \
        = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    base_kwargs = {
        'base_url': httpd.get_url(),
        'destination': str(tmpdir),
        'log_level': 'ERROR',
    }

    if args.get('builds'):
        query_builds_by_revision.return_value = args.get('builds')

    kwargs = copy.deepcopy(base_kwargs)
    kwargs.update(args.get('kwargs'))

    build = FactoryScraper(filename, **kwargs)
    build.download()

    dir_content = os.listdir(str(tmpdir))
    assert args['fname'] in dir_content
