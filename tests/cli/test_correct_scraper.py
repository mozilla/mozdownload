import os

import mozfile
from mozprocess import processhandler

import mozhttpd_base_test as mhttpd


tests = [
    # ReleaseScraper
    {'options': ['-v', 'latest'],
     'fname': 'firefox-latest.en-US.linux64.tar.bz2'},

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
