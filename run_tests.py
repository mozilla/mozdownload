#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pip
from subprocess import call
import sys

VERSION_MANIFEST_DESTINY = '0.5.6'
VERSION_MOZFILE = '0.7'
VERSION_MOZHTTPD = '0.6'
VERSION_MOZLOG = '1.3'
VERSION_MOZTEST = '0.1'
VERSION_VIRTUAL_ENV = '1.9.1'


# see http://stackoverflow.com/questions/12332975/installing-python-module-within-code
def install(package, version):
    package_arg = "%s==%s" % (package, version)
    pip.main(['install', '--upgrade', package_arg])


def python(*args):
    call(['python'] + list(args))

try:
    # for more info see:
    # http://www.virtualenv.org/en/latest/#using-virtualenv-without-bin-python
    venv_dir = os.path.join('tests', 'venv')
    if sys.platform == 'win32':
        activate_this_file = os.path.join('tests', 'venv', 'Scripts',
                                          'activate_this.py')
    else:
        activate_this_file = os.path.join('tests', 'venv', 'bin',
                                          'activate_this.py')

    if not os.path.isfile(activate_this_file):
        # download and create venv
        install('virtualenv', VERSION_VIRTUAL_ENV)
        call(['virtualenv', '--no-site-packages', venv_dir])

    execfile(activate_this_file, dict(__file__=activate_this_file))
    print "Virtual environment activated successfully."

    # Installs
    install('ManifestDestiny', VERSION_MANIFEST_DESTINY)
    install('mozfile', VERSION_MOZFILE)
    install('mozhttpd', VERSION_MOZHTTPD)
    install('mozlog', VERSION_MOZLOG)
    install('moztest', VERSION_MOZTEST)

    # Install mozdownload
    python('setup.py', 'develop')
    # run the tests
    tests_path = os.path.join('tests', 'test.py')
    python(tests_path)

except IOError:
    print "Could not activate virtual environment."
    print "Exiting."
