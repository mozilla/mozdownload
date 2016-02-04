import subprocess
import unittest

from mozdownload import __version__, cli


class TestCLIOutput(unittest.TestCase):
    """Tests for the cli() function in scraper.py"""

    def test_cli_executes(self):
        """Test that cli will start and print usage message"""
        output = subprocess.check_output(['mozdownload', '--help'])
        self.assertTrue(cli.__doc__.format(__version__) in output)
