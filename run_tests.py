#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from subprocess import check_call, CalledProcessError
import shutil
import sys
import urllib2
import zipfile

# Link to the folder which contains the zip archives of virtualenv
URL_VIRTUALENV = 'https://codeload.github.com/pypa/virtualenv/zip/'
VERSION_VIRTUALENV = '1.9.1'

DIR_BASE = os.path.abspath(os.path.dirname(__file__))
DIR_ENV = os.path.join(DIR_BASE, 'tmp', 'venv')
DIR_TMP = os.path.join(DIR_BASE, 'tmp')

REQ_TXT = os.path.join('tests', 'requirements.txt')


def download(url, target):
    """Downloads the specified url to the given target."""
    response = urllib2.urlopen(url)
    with open(target, 'wb') as f:
        f.write(response.read())
    return target


# see http://stackoverflow.com/questions/12332975/installing-python-module-within-code
def install(package, version):
    package_arg = "%s==%s" % (package, version)
    check_call(['pip', 'install', '--upgrade', package_arg])


def python(*args):
    pypath = [os.path.join(DIR_ENV, 'bin', 'python')]
    check_call(pypath + list(args))


try:
    # Remove potentially pre-existing tmp_dir
    shutil.rmtree(DIR_TMP, True)
    # Start out clean
    os.makedirs(DIR_TMP)

    print 'Downloading virtualenv %s' % VERSION_VIRTUALENV
    virtualenv_file = download(URL_VIRTUALENV + VERSION_VIRTUALENV,
                               os.path.join(DIR_TMP, 'virtualenv.zip'))
    virtualenv_zip = zipfile.ZipFile(virtualenv_file)
    virtualenv_zip.extractall(DIR_TMP)
    virtualenv_zip.close()

    print 'Creating new virtual environment'
    virtualenv_script = os.path.join(DIR_TMP,
                                     'virtualenv-%s' % VERSION_VIRTUALENV,
                                     'virtualenv.py')
    check_call(['python', virtualenv_script, DIR_ENV])

    print 'Activating virtual environment'
    # for more info see:
    # http://www.virtualenv.org/en/latest/#using-virtualenv-without-bin-python
    if sys.platform == 'win32':
        activate_this_file = os.path.join(DIR_ENV, 'Scripts',
                                          'activate_this.py')
    else:
        activate_this_file = os.path.join(DIR_ENV, 'bin',
                                          'activate_this.py')

    if not os.path.isfile(activate_this_file):
        # create venv
        check_call(['virtualenv', '--no-site-packages', DIR_ENV])

    execfile(activate_this_file, dict(__file__=activate_this_file))
    print "Virtual environment activated successfully."

except (CalledProcessError, IOError):
    print "Could not activate virtual environment."
    print "Exiting."

# Install dependent packages
check_call(['pip', 'install', '--upgrade', '-r', REQ_TXT])

# Install mozdownload
python('setup.py', 'develop')

# run the tests
python(os.path.join('tests', 'test.py'))

# Clean up
shutil.rmtree(DIR_TMP)
