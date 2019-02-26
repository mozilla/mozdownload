import subprocess

from mozdownload import __version__, cli


def test_cli_executes():
    """Test that cli will start and print usage message"""
    output = subprocess.check_output(['mozdownload', '--help'])
    assert cli.__doc__.format(__version__) in output
