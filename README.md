[![PyPI version](https://badge.fury.io/py/mozdownload.svg)](http://badge.fury.io/py/mozdownload)
[![Build Status](https://travis-ci.org/mozilla/mozdownload.svg?branch=master)](https://travis-ci.org/mozilla/mozdownload)
[![Stories in Ready](https://badge.waffle.io/mozilla/mozdownload.png?label=ready&title=Ready)](https://waffle.io/mozilla/mozdownload)

# mozdownload

[mozdownload](https://github.com/mozilla/mozdownload)
is a [python package](http://pypi.python.org/pypi/mozdownload)
which handles downloading of Mozilla applications.

## Installation

If the tool should only be used for downloading applications we propose to
install it via pip. The following command will install the latest release:

    pip install mozdownload

Otherwise follow the steps below to setup a development environment. It is
recommended that [virtualenv](http://virtualenv.readthedocs.org/en/latest/installation.html)
and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
be used in conjunction with mozdownload. Start by installing these.

Then:

    git clone https://github.com/%username%/mozdownload.git
    cd mozdownload
    python setup.py develop

More detailed developer documentation can be found in the [[wiki|wiki]].

## Command Line Usage

The `mozdownload` command will download the application based on the provided
command line options.

### Examples

Download the latest official Firefox release for your platform:

    mozdownload --version=latest

Download the latest Firefox Aurora build for Windows (32bit):

    mozdownload --type=daily --branch=mozilla-aurora --platform=win32

Download the latest official Thunderbird release for your platform:

    mozdownload --application=thunderbird --version=latest

Download the latest Earlybird build for Linux (64bit):

    mozdownload --application=thunderbird --type=daily --branch=comm-aurora --platform=linux64

Download this README file:

    mozdownload --url=https://raw.github.com/mozilla/mozdownload/master/README.md

Download a file from a URL protected with basic authentication:

    mozdownload --url=http://example.com/secrets.txt --username=admin --password=password

Run `mozdownload --help` for detailed information on the command line options.

### Command Line Options

To see the full list of command line options, execute the command below and check the list
of options for the build type to download:

    mozdownload --help
