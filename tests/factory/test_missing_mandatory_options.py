import pytest

from mozdownload import FactoryScraper
from mozdownload.errors import NotSupportedError


def test_release_without_version(httpd, tmpdir):
    """Test that missing mandatory options for release builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('release', destination=str(tmpdir), base_url=httpd.get_url())


def test_candidate_without_version(httpd, tmpdir):
    """Test that missing mandatory options for candidate builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('candidate', destination=str(tmpdir), base_url=httpd.get_url())


def test_try_without_revision(httpd, tmpdir):
    """Test that missing mandatory options for try builds raise an exception"""
    with pytest.raises(ValueError):
        FactoryScraper('try', destination=str(tmpdir), base_url=httpd.get_url())


def test_non_daily_fenix(httpd, tmpdir):
    """Test that non-daily scraper_type for fenix raises exception"""
    with pytest.raises(NotSupportedError):
        FactoryScraper('candidate',
                       destination=str(tmpdir),
                       base_url=httpd.get_url(),
                       application='fenix',
                       version='110.0b1')


def test_non_release_non_candidate_devedition(httpd, tmpdir):
    """Test that non-relase and non-candidate scraper type for devedition raises exception"""
    with pytest.raises(NotSupportedError):
        FactoryScraper('daily',
                       destination=str(tmpdir),
                       base_url=httpd.get_url(),
                       application='devedition',
                       version='60.0b1')
