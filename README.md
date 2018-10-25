# mozdownload

[mozdownload](https://github.com/mozilla/mozdownload)
is a [python package](http://pypi.python.org/pypi/mozdownload)
which handles downloading of Mozilla applications.

[![Travis](https://travis-ci.org/mozilla/mozdownload.svg?branch=master)](https://travis-ci.org/mozilla/mozdownload)
[![Coverage](https://coveralls.io/repos/github/mozilla/mozdownload/badge.svg)](https://coveralls.io/github/mozilla/mozdownload)
[![Issues](https://img.shields.io/github/issues/mozilla/mozdownload.svg)](https://github.com/mozilla/mozdownload/issues)
[![pyup.io](https://pyup.io/repos/github/mozilla/mozdownload/shield.svg)](https://pyup.io/repos/github/mozilla/mozdownload/)

## Installation

If the tool should only be used for downloading applications we propose to
install it via pip. The following command will install the latest release:
```bash
pip install mozdownload
```

Otherwise follow the steps below to setup a development environment. It is
recommended that [virtualenv](http://virtualenv.readthedocs.org/en/latest/installation.html)
and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
be used in conjunction with mozdownload. Start by installing these. Then first fork
our repository into your own github account, and run:
```bash
git clone https://github.com/%your_account%/mozdownload.git
cd mozdownload
python setup.py develop
```

More detailed developer documentation can be found in the [wiki](https://github.com/mozilla/mozdownload/wiki).

## Command Line Usage

The `mozdownload` command will download the application based on the provided
command line options.

### Examples

Download the latest official Firefox release for your platform:
```bash
mozdownload --version=latest
```

Download the latest official Firefox beta release for your platform:
```bash
mozdownload --version=latest-beta
```

Download the latest official Firefox esr release for your platform:
```bash
mozdownload --version=latest-esr
```

Download the latest Firefox release candidate for your platform:
```bash
mozdownload --type candidate --version=latest
```

Download the latest Firefox Aurora build for Windows (32bit):
```bash
mozdownload --type=daily --branch=mozilla-aurora --platform=win32
```

Download the latest official Thunderbird release for your platform:
```bash
mozdownload --application=thunderbird --version=latest
```

Download the latest Earlybird build for Linux (64bit):
```bash
mozdownload --application=thunderbird --type=daily --branch=comm-aurora --platform=linux64
```

Download this README file:
```bash
mozdownload --url=https://raw.github.com/mozilla/mozdownload/master/README.md
```

Download a file from a URL protected with basic authentication:
```bash
mozdownload --url=http://example.com/secrets.txt --username=admin --password=password
```

Run `mozdownload --help` for detailed information on the command line options.

### Command Line Options

To see the full list of command line options, execute the command below and check the list
of options for the build type to download:
```bash
mozdownload --help
```

## API

Beside the CLI mozdownload also offers an API to be used. To create specific instances of scrapers
the FactoryScraper class can be used. Here some examples:
```python
# Create a release scraper for the German locale of Firefox 40.0.3
from mozdownload import FactoryScraper
scraper = FactoryScraper('release', version='40.0.3', locale='de')

# Create a candidate scraper for Windows 32bit of Firefox 41.0b9
from mozdownload import FactoryScraper
scraper = FactoryScraper('candidate', version='41.0b9', platform='win32')

# Create a daily scraper for the latest Dev Edition build on the current platform
from mozdownload import FactoryScraper
scraper = FactoryScraper('daily', branch='mozilla-aurora')
```

All those scraper instances allow you to retrieve the url which is used to download the files, and the filename for the local destination:
```python
from mozdownload import FactoryScraper
scraper = FactoryScraper('daily')
print scraper.url
print scraper.filename
```

To actually download the remote file the download() method has to be called:
```python
from mozdownload import FactoryScraper
scraper = FactoryScraper('daily')
filename = scraper.download()
```

## Testing

To run the entire test suite to check if your changes create any errors, run `tox`.

If you only run very specific tests, please specify it via `tox -- -k <keyword>`.
For example, if you are only interested in tests that look at tinderbox builds, run `tox -- -k tinderbox`.
The `-k <keyword>` works for folders, filenames and even names of test methods.
