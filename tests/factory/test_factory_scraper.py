import copy
import os

import pytest

from mozdownload import FactoryScraper


@pytest.mark.parametrize('scraper_type,builds,filename,args', [
    # ReleaseScraper
    ('release', None, 'firefox-23.0.1.en-US.win32.exe', {
        'platform': 'win32',
        'version': '23.0.1',
    }),

    # ReleaseCandidateScraper
    ('candidate', None, 'firefox-23.0.1-build3.en-US.win32.exe', {
        'platform': 'win32',
        'version': '23.0.1',
    }),

    # DailyScraper
    ('daily', None,
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe', {
         'platform': 'win32',
     }),

    # TinderboxScraper
    ('tinderbox', None, '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe', {
        'platform': 'win32',
    }),

    # TryScraper
    ('try', ['/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'],
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg', {
         'revision': '8fcac92cfcad',
         'platform': 'mac64',
     }),
])
def test_factory(httpd, tmpdir, scraper_type, builds, filename, args, mocker):
    """Testing various download scenarios for the factory."""
    query_builds_by_revision \
        = mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')
    base_kwargs = {
        'base_url': httpd.get_url(),
        'destination': str(tmpdir),
        'log_level': 'ERROR',
    }

    if builds:
        query_builds_by_revision.return_value = builds

    kwargs = copy.deepcopy(base_kwargs)
    kwargs.update(args)

    build = FactoryScraper(scraper_type, **kwargs)
    build.download()

    dir_content = os.listdir(str(tmpdir))
    assert filename in dir_content
