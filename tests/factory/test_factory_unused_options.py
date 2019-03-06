import copy
import os

import pytest

from mozdownload.utils import urljoin
from mozdownload import FactoryScraper


@pytest.mark.parametrize('filename,args', [
    # ReleaseScraper
    ('release',
     {
         'fname': 'firefox-23.0.1.en-US.win32.exe',
         'kwargs': {
             'version': '23.0.1',
             'platform': 'win32',
             # unused options
             'branch': 'mozilla-central',
             'build_id': '20131001030204',
             'build_number': '1',
             'revision': '8fcac92cfcad',
             'date': '2013-10-01',
             'debug_build': True,
             'url': 'http://localhost',
         }
     }),

    # ReleaseCandidateScraper
    ('candidate',
     {
         'fname': 'firefox-23.0.1-build3.en-US.win32.exe',
         'kwargs': {
             'platform': 'win32',
             'version': '23.0.1',
             # unused options
             'branch': 'mozilla-central',
             'build_id': '20131001030204',
             'revision': '8fcac92cfcad',
             'date': '2013-10-01',
             'debug_build': True,
             'url': 'http://localhost',
         }
     }),

    # DailyScraper
    ('daily',
     {
         'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe',
         'kwargs': {
             'platform': 'win32',
             # unused options
             'debug_build': True,
             'url': 'http://localhost',
             'version': '23.0.1',
         }
     }),

    # TinderboxScraper
    ('tinderbox',
     {
         'fname': '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe',
         'kwargs': {
             'platform': 'win32',
             # unused options
             'url': 'http://localhost',
             'version': '23.0.1',
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
             # unused options
             'build_id': '20131001030204',
             'build_number': '1',
             'url': 'http://localhost',
             'version': '23.0.1',
         }
     })
])
def test_unused_options(httpd, tmpdir, filename, args, mocker):
    """Test that unknown optional options do not break the given scraper."""
    base_kwargs = {
        'base_url': httpd.get_url(),
        'destination': str(tmpdir),
        'log_level': 'ERROR',
    }
    query_builds_by_revision = \
        mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')

    if args.get('builds'):
        query_builds_by_revision.return_value = args.get('builds')

    kwargs = copy.deepcopy(base_kwargs)
    kwargs.update(args.get('kwargs'))

    build = FactoryScraper(filename, **kwargs)
    build.download()

    dir_content = os.listdir(str(tmpdir))
    assert args['fname'] in dir_content


def test_unused_options_direct_scraper(httpd, tmpdir):
    filename = 'download_test.txt'
    test_url = urljoin(httpd.get_url(), filename)

    scraper = FactoryScraper(scraper_type='direct',
                             url=test_url,
                             destination=str(tmpdir),

                             platform='win32',
                             branch='mozilla-central',
                             build_id='20131001030204',
                             revision='8fcac92cfcad',
                             date='2013-10-01',
                             debug_build=True,
                             version='23.0.1')

    assert scraper.url == test_url
    assert scraper.filename == os.path.join(str(tmpdir), filename)
