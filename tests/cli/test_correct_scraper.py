import os

import mozfile
from mozprocess import processhandler

from mozdownload import Scraper
import mozhttpd_base_test as mhttpd


default_latest_binary_names = {
    'linux': 'firefox-latest-en-US.linux.tar.bz2',
    'linux64': 'firefox-latest.en-US.linux64.tar.bz2',
    'mac': 'firefox-latest.en-US.mac.dmg',
    'mac64': 'firefox-latest.en-US.mac64.dmg',
    'win32': 'firefox-latest.en-US.win.exe',
    'win64': 'firefox-latest.en-US.win.exe'
}

tests = [
    # ReleaseScraper
    {'options': ['-v', 'latest'],
     'fname': default_latest_binary_names[Scraper.detect_platform()]},

    # ReleaseCandidateScraper
    {'options': ['-t', 'candidate', '-v', '21.0', '-p', 'win32'],
     'fname': 'firefox-21.0-build3.en-US.win32.exe'},

    # DailyScraper
    {'options': ['-t', 'daily', '-p', 'win32'],
     'fname': '2013-10-01-03-02-04-mozilla-central-firefox-27.0a1.en-US.win32.installer.exe'},

    # TinderboxScraper
    {'options': ['-t', 'tinderbox', '-p', 'win32'],
     'fname': 'mozilla-central-firefox-25.0a1.en-US.win32.installer.exe'},

    # TryScraper
    {'options': ['-t', 'try', '-p', 'mac64', '--changeset=8fcac92cfcad'],
     'fname': '8fcac92cfcad-firefox-38.0a1.en-US.mac.dmg'},
]


class TestCLICorrectScraper(mhttpd.MozHttpdBaseTest):
    """Test mozdownload for correct choice of scraper"""

    def output(self, line):
        # Ignore any output to stdout
        pass

    def test_scraper(self):
        """Testing various download scenarios."""

        for entry in tests:
            command = ['mozdownload',
                       '--base_url=%s' % self.wdir,
                       '--destination=%s' % self.temp_dir]
            p = processhandler.ProcessHandler(command + entry['options'],
                                              processOutputLine=[self.output])
            p.run()
            p.wait()
            dir_content = os.listdir(self.temp_dir)
            self.assertTrue(entry['fname'] in dir_content)

            mozfile.remove(os.path.join(self.temp_dir, entry['fname']))
