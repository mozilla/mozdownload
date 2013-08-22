#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
 
VERSION_MANIFEST_DESTINY=0.5.6
VERSION_MOZTEST=0.1
VERSION_MOZFILE=0.7
VERSION_VIRTUAL_ENV=1.9.1
 
VENV_DIR="tests/venv"
 
# Check if environment exists, if not, create a virtualenv:
if [ -d $VENV_DIR ]
then
echo "Using virtual environment in $VENV_DIR"
else
echo "Creating a virtual environment (version ${VERSION_VIRTUAL_ENV}) in ${VENV_DIR}"
curl https://raw.github.com/pypa/virtualenv/${VERSION_VIRTUAL_ENV}/virtualenv.py | python - --no-site-packages $VENV_DIR
fi
. $VENV_DIR/bin/activate
 
python setup.py develop
pip install --upgrade ManifestDestiny==$VERSION_MANIFEST_DESTINY
pip install --upgrade moztest==$VERSION_MOZTEST
pip install --upgrade mozfile==$VERSION_MOZFILE
 
python tests/test.py $@
