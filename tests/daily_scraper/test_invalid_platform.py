import pytest

from mozdownload import DailyScraper


@pytest.mark.parametrize('args', [
    ({'application': 'fenix', 'platform': 'mac'}),
])
def test_invalid_platform_falls_back_to_firefox(httpd, tmpdir, args):
    """fenix requested on a non-Android platform should fall back to firefox"""
    with pytest.warns(DeprecationWarning):
        scraper = DailyScraper(destination=str(tmpdir),
                               base_url=httpd.get_url(), **args)
    assert scraper.application == 'firefox'


@pytest.mark.parametrize('platform', [
    'android-arm64-v8a', 'android-armeabi-v7a',
    'android-x86', 'android-x86_64'])
def test_firefox_on_android_maps_to_fenix(httpd, tmpdir, platform):
    """firefox requested on an Android platform should map to fenix"""
    scraper = DailyScraper(destination=str(tmpdir),
                           base_url=httpd.get_url(),
                           application='firefox',
                           platform=platform)
    assert scraper.application == 'fenix'
