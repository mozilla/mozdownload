import subprocess
import unittest

from mozdownload import cli


class TestCLIOutput(unittest.TestCase):
    """Tests for the cli() function in scraper.py"""

    def test_cli_executes(self):
        """Test that cli will start and print usage message"""
        output = subprocess.check_output(['mozdownload'])
        self.assertTrue(cli.__doc__ in output)
