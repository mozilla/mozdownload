import copy
import os

import mozfile
import pytest

from mozdownload import FactoryScraper
from mozdownload.utils import urljoin
from mozdownload.errors import NotSupportedError


def test_release_without_version(httpd, tmpdir):
    """Test that missing mandatory options for release builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('release', destination=str(tmpdir), base_url=httpd.get_url())


def test_candidate_without_version(httpd, tmpdir):
    """Test that missing mandatory options for candidate builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('release', destination=str(tmpdir), base_url=httpd.get_url())


def test_try_without_revision(httpd, tmpdir):
    """Test that missing mandatory options for try builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('try', destination=str(tmpdir), base_url=httpd.get_url())


def test_non_daily_fennec(httpd, tmpdir):
    """Test that non-daily scrapper_type for fennec raises exception"""
    with pytest.raises(NotSupportedError):
        FactoryScraper('candidate',
                       destination=str(tmpdir),
                       base_url=httpd.get_url(),
                       application='fennec',
                       version='60.0b1')


def test_non_release_non_candidate_devedition(httpd, tmpdir):
    """Test that non-relase and non-candidate scrapper type for devedition raises exception"""
    with pytest.raises(NotSupportedError):
        FactoryScraper('daily',
                       destination=str(tmpdir),
                       base_url=httpd.get_url(),
                       application='devedition',
                       version='60.0b1')


@pytest.mark.parametrize('scraper_type,builds,fname,arg', [
    # ReleaseScraper
    ('release', None, 'firefox-23.0.1.en-US.win32.exe', {
        'version': '23.0.1',
        'platform': 'win32',

        'branch': 'mozilla-central',
        'build_id': '20131001030204',
        'build_number': '1',
        'revision': '8fcac92cfcad',
        'date': '2013-10-01',
        'debug_build': True,
        'url': 'http://localhost',
    }),

    # ReleaseCandidateScraper
    ('candidate', None, 'firefox-23.0.1-build3.en-US.win32.exe', {
        'platform': 'win32',
        'version': '23.0.1',

        'branch': 'mozilla-central',
        'build_id': '20131001030204',
        'revision': '8fcac92cfcad',
        'date': '2013-10-01',
        'debug_build': True,
        'url': 'http://localhost',
    }),

    # DailyScraper
    ('daily', None,
     '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe', {
         'platform': 'win32',

         'debug_build': True,
         'url': 'http://localhost',
         'version': '23.0.1',
     }),

    # TinderboxScraper
    ('tinderbox', None, '1374583608-mozilla-central-firefox-25.0a1.en-US.win32.installer.exe', {
        'platform': 'win32',

        'url': 'http://localhost',
        'version': '23.0.1',
    }),

    # TryScraper
    ('try', ['/firefox/try-builds/test-user@mozilla.com-8fcac92cfcad/try-foobar/'],
     '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg', {
         'revision': '8fcac92cfcad',
         'platform': 'mac64',

         'build_id': '20131001030204',
         'build_number': '1',
         'url': 'http://localhost',
         'version': '23.0.1',
     })
])

def test_unknown_options(httpd, tmpdir, scraper_type, builds, fname, arg, mocker):
    """Test that unknown optional options do not break the given scraper."""

    base_kwargs = {
        'base_url': httpd.get_url(),
        'destination': str(tmpdir),
        'log_level': 'ERROR',
    }
    query_builds_by_revision = \
        mocker.patch('mozdownload.treeherder.Treeherder.query_builds_by_revision')

    if builds:
        query_builds_by_revision.return_value = builds

    kwargs = copy.deepcopy(base_kwargs)
    kwargs.update(arg)

    build = FactoryScraper(scraper_type, **kwargs)
    build.download()

    dir_content = os.listdir(str(tmpdir))
    assert fname in dir_content

    mozfile.remove(os.path.join(str(tmpdir), fname))


def test_unknown_options_direct_scraper(httpd, tmpdir):
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
